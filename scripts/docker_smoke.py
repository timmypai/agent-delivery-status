"""Authorized CI only: real Docker smoke; receipts/second build are TEST ONLY.

No registry writes. Only containers created here are removed. Image IDs are
local content addresses, NOT registry digests or deployment evidence.
"""
import argparse
from datetime import datetime, timezone
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import read_json, validate_build


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True, timeout=120).strip()


def smoke(image, metadata, directory):
    # Narrow inspect templates avoid dumping container environment/credentials.
    image_id = docker('image', 'inspect', '--format', '{{.Id}}', image)
    revision = docker('image', 'inspect', '--format',
                      '{{index .Config.Labels "org.opencontainers.image.revision"}}', image)
    assert revision == metadata['commit']
    receipt_path = directory / 'receipt.json'
    good = dict(id='SYNTHETIC-CI-SMOKE-NOT-DEPLOYED',
                deployed_at=datetime.now(timezone.utc).isoformat(),
                commit=revision, image_digest=image_id)

    def put(data):
        candidate = directory / 'next.json'
        candidate.write_text(json.dumps(data))
        candidate.chmod(0o644)
        candidate.replace(receipt_path)

    put(good)
    fake = ('b' if revision != 'b'*40 else 'c') * 40
    container = docker('run', '-d', '--read-only', '--cap-drop=ALL',
                       '--security-opt=no-new-privileges', '--cpus=0.5',
                       '--memory=128m', '--pids-limit=64',
                       '--publish=127.0.0.1::8080',
                       '--mount', f'type=bind,src={directory},dst=/run/delivery,readonly',
                       '--env', 'COMMIT='+fake, '--env', 'GITHUB_SHA='+fake, image_id)
    try:
        ports = json.loads(docker('inspect', '--format', '{{json .NetworkSettings.Ports}}', container))
        binding = ports['8080/tcp']
        assert len(binding) == 1 and binding[0]['HostIp'] == '127.0.0.1'
        port = int(binding[0]['HostPort'])
        host = json.loads(docker('inspect', '--format', '{{json .HostConfig}}', container))
        assert host['ReadonlyRootfs'] and not host['Privileged']
        assert host['NetworkMode'] != 'host' and host['PidMode'] != 'host'
        assert host['Memory'] == 128*1024*1024 and host['PidsLimit'] == 64
        assert host['NanoCpus'] == 500000000
        assert docker('inspect', '--format', '{{.Config.User}}', container) == '65532:65532'
        assert docker('inspect', '--format', '{{.Image}}', container) == image_id
        mounts = json.loads(docker('inspect', '--format', '{{json .Mounts}}', container))
        assert len(mounts) == 1 and mounts[0]['Destination'] == '/run/delivery'
        assert not mounts[0]['RW']

        def request(method, path):
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
            try:
                conn.request(method, path)
                response = conn.getresponse()
                result = response.status, dict(response.getheaders()), response.read()
                assert result[1]['Cache-Control'] == 'no-store'
                return result
            finally:
                conn.close()

        for attempt in range(6):
            try:
                assert request('GET', '/healthz')[0] == 200
                break
            except (OSError, http.client.HTTPException):
                if attempt == 5:
                    raise
                time.sleep(1)
        for path in ['/', '/healthz', '/version']:
            get = request('GET', path)
            head = request('HEAD', path)
            assert get[0] == head[0] == 200 and head[2] == b''
            assert get[1]['Content-Length'] == head[1]['Content-Length']
        version = json.loads(request('GET', '/version')[2])
        assert version == dict(schema_version=1, **metadata,
                               deployment={k:good[k] for k in ('id','deployed_at')})
        assert request('POST', '/version')[0] == 405
        assert request('GET', '/../build-metadata.json')[0] == 404
        for invalid in [dict(good, commit=fake), {}, dict(good, image_digest='bad')]:
            put(invalid)
            for path in ['/', '/version', '/healthz']:
                assert request('GET', path)[0] == 503
        receipt_path.unlink()
        assert request('GET', '/healthz')[0] == 503
        put(good)
        assert request('GET', '/healthz')[0] == 200
        print(json.dumps({'test_only':True, 'commit':revision, 'image_id':image_id,
                          'result':'container HTTP/security/negative assertions passed'}))
        return image_id
    finally:
        docker('rm', '-f', container)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--metadata', required=True)
    args = parser.parse_args()
    metadata = validate_build(read_json(args.metadata))
    with tempfile.TemporaryDirectory(prefix='delivery-smoke-') as temp:
        root = Path(temp)
        root.chmod(0o755)
        first = smoke(args.image, metadata, root)
        # P4 second build: explicitly synthetic C_B, never a releasable artifact.
        context = root / 'context'
        context.mkdir()
        for filename in ['Dockerfile', 'app.py']:
            shutil.copyfile(ROOT / filename, context / filename)
        second = dict(metadata, commit=('d' if metadata['commit'] != 'd'*40 else 'e')*40)
        (context / 'build-metadata.json').write_text(json.dumps(second))
        iid = root / 'fixture-image-id'
        subprocess.run(['docker','build','--build-arg','COMMIT='+second['commit'],
                        '--iidfile',str(iid),str(context)], check=True, timeout=120)
        fixture_image = iid.read_text().strip()
        try:
            assert smoke(fixture_image, second, root) != first
        finally:
            docker('image', 'rm', fixture_image)


if __name__ == '__main__':
    main()
