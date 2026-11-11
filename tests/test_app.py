"""Synthetic unit fixtures ONLY; these URLs/digests are not release evidence."""
import importlib
import json
from pathlib import Path
import tempfile
import unittest

REPO = 'https://github.com/timmypai/agent-delivery-status'


def build(commit='a' * 40):
    return dict(release='1.0.0', commit=commit, built_at='2026-01-01T00:00:00Z',
                repository_url=REPO, evidence=dict(issue_url=REPO+'/issues/1',
                pr_url=REPO+'/pull/1', ci_url=REPO+'/actions/runs/1'))


def receipt(commit='a' * 40):
    return dict(id='synthetic-test-only', deployed_at='2026-01-01T00:01:00Z',
                commit=commit, image_digest='sha256:'+'b'*64)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.metadata = self.root/'build.json'
        self.receipt = self.root/'receipt.json'
        self.metadata.write_text(json.dumps(build()))
        self.receipt.write_text(json.dumps(receipt()))

    def app(self):
        self.assertIsNotNone(importlib.util.find_spec('app'), 'Application module is required')
        return importlib.import_module('app').Application(self.metadata, self.receipt)

    def test_version_reports_build_and_deployment(self):
        status, content_type, body = self.app().response('/version')
        self.assertEqual(status, 200)
        self.assertEqual(content_type, 'application/json')
        self.assertEqual(json.loads(body), dict(schema_version=1, **build(),
            deployment={'id':'synthetic-test-only', 'deployed_at':'2026-01-01T00:01:00Z'}))

    def test_invalid_build_rejected(self):
        mutations = [(k, None) for k in build()] + [
            ('release', '1.0.1'), ('commit','A'*40), ('commit','a'*39),
            ('built_at','2026-02-30T00:00:00Z'), ('built_at','2026-01-01'),
            ('repository_url', REPO+'/'), ('evidence', []),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                data = build(); data[key] = value
                self.metadata.write_text(json.dumps(data))
                with self.assertRaises(ValueError): self.app()
        for key in build():
            data = build(); del data[key]
            self.metadata.write_text(json.dumps(data))
            with self.assertRaises(ValueError): self.app()
        for key in build()['evidence']:
            for url in ['javascript:alert(1)', 'https://evil.invalid/',
                        REPO+'/issues/0', REPO+'/issues/1?token=SECRET',
                        'https://user:SECRET@github.com/timmypai/agent-delivery-status/issues/1',
                        REPO+'/issues/1\n']:
                data = build(); data['evidence'][key] = url
                self.metadata.write_text(json.dumps(data))
                with self.assertRaises(ValueError): self.app()
        for raw in ['{', '[]', '{}', '{"commit":1,"commit":2}', 'x'*65537]:
            self.metadata.write_text(raw)
            with self.assertRaises(ValueError): self.app()
        self.metadata.unlink()
        with self.assertRaises(ValueError): self.app()

    def test_receipt_invalidates_immediately_and_recovers(self):
        app = self.app()
        bad = [None, [], {}, dict(receipt(), commit='c'*40),
               dict(receipt(), image_digest='sha256:bad'),
               dict(receipt(), id=''), dict(receipt(), id=123),
               dict(receipt(), deployed_at='yesterday')]
        for data in bad:
            with self.subTest(data=data):
                self.receipt.write_text(json.dumps(data))
                self.assertEqual(app.response('/version')[0], 503)
                self.assertEqual(json.loads(app.response('/version')[2]), {'error':'metadata_unavailable'})
                status, _, body = app.response('/healthz')
                self.assertEqual(status, 503)
                self.assertEqual(json.loads(body), {'status':'unavailable', 'checks':
                    {'build_metadata':'ok', 'deployment_receipt':'invalid'}})
                self.assertEqual(app.response('/')[0], 503)
        for raw in ['{', ' '*65537, '{"id":"a","id":"b"}']:
            self.receipt.write_text(raw)
            self.assertEqual(app.response('/healthz')[0],503)
        self.receipt.unlink()
        self.assertEqual(app.response('/version')[0],503)
        self.receipt.write_text(json.dumps(receipt()))
        self.assertEqual(app.response('/version')[0],200)
        self.assertEqual(json.loads(app.response('/healthz')[2]), {'status':'ok',
            'checks':{'build_metadata':'ok','deployment_receipt':'ok'}})

    def test_html_escapes_values_and_links_are_safe(self):
        self.receipt.write_text(json.dumps(dict(receipt(), id='<script>"&</script>')))
        status, kind, body = self.app().response('/')
        self.assertEqual((status,kind),(200,'text/html; charset=utf-8'))
        html = body.decode()
        self.assertIn('&lt;script&gt;&quot;&amp;&lt;/script&gt;', html)
        self.assertNotIn('<script>', html)
        for url in build()['evidence'].values(): self.assertIn('href="'+url+'"', html)
        self.assertEqual(html.count('rel="noopener noreferrer"'),3)
        for value in ['1.0.0','a'*40,'2026-01-01T00:00:00Z','本機健康（非交付驗收）']:
            self.assertIn(value,html)
        self.assertNotIn('CI PASS', html)

    def test_unknown_paths_are_not_files(self):
        for path in ['/missing','/../build.json','/%2e%2e/build.json','/version?file=/etc/passwd']:
            self.assertEqual(self.app().response(path)[0],404)

    def test_invalid_unicode_receipt_fails_closed(self):
        app = self.app()
        for ident in ['\ud800', '\udfff', 'bad\x7fid']:
            with self.subTest(ident=repr(ident)):
                self.receipt.write_text(json.dumps(dict(receipt(), id=ident)))
                for path in ['/', '/version', '/healthz']:
                    self.assertEqual(app.response(path)[0], 503)

    def test_runtime_environment_cannot_replace_cached_build(self):
        import os
        from unittest.mock import patch
        app = self.app()
        self.metadata.write_text(json.dumps(build('c'*40)))
        with patch.dict(os.environ, {'COMMIT':'d'*40, 'GITHUB_SHA':'e'*40}):
            self.assertEqual(json.loads(app.response('/version')[2])['commit'],'a'*40)
        self.receipt.write_text(json.dumps(receipt('c'*40)))
        self.assertEqual(json.loads(self.app().response('/version')[2])['commit'],'c'*40)

    def test_real_http_contract(self):
        import http.client
        import threading
        module = importlib.import_module('app')
        self.assertTrue(hasattr(module,'make_server'), 'HTTP server is required')
        server = module.make_server(self.app(), '127.0.0.1', 0)
        self.addCleanup(server.server_close)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        def cleanup():
            server.shutdown(); thread.join(timeout=3); server.server_close()
        self.addCleanup(cleanup)
        def request(method, path):
            conn = http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
            try:
                conn.request(method,path)
                response = conn.getresponse()
                return response.status, dict(response.getheaders()), response.read()
            finally: conn.close()
        for path in ['/','/version','/healthz','/missing','/../secret']:
            get = request('GET',path); head = request('HEAD',path)
            self.assertEqual(get[0],200 if path in ['/','/version','/healthz'] else 404)
            self.assertEqual(head[0],get[0]); self.assertEqual(head[2],b'')
            for key in ['Content-Length','Content-Type','Cache-Control','Content-Security-Policy']:
                self.assertEqual(get[1][key],head[1][key])
            self.assertEqual(get[1]['Cache-Control'],'no-store')
            self.assertIn("frame-ancestors 'none'",get[1]['Content-Security-Policy'])
            self.assertNotIn('Access-Control-Allow-Origin',get[1])
            self.assertNotIn('Python',get[1].get('Server',''))
            self.assertEqual(get[1]['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(get[1]['Referrer-Policy'], 'no-referrer')
            self.assertEqual(int(get[1]['Content-Length']), len(get[2]))
        self.assertEqual(json.loads(request('GET','/version')[2]),
                         dict(schema_version=1, **build(), deployment={
                             'id':'synthetic-test-only','deployed_at':'2026-01-01T00:01:00Z'}))
        html = request('GET','/')[2].decode()
        for url in build()['evidence'].values():
            self.assertIn('href="'+url+'"', html)
        for method in ['POST','PUT','DELETE','PATCH','OPTIONS','TRACE','CONNECT','CUSTOM']:
            status, headers, _ = request(method,'/version')
            self.assertEqual(status,405); self.assertEqual(headers['Allow'],'GET, HEAD')
            self.assertEqual(headers['Cache-Control'],'no-store')
        self.receipt.unlink()
        for path in ['/','/healthz','/version']:
            self.assertEqual(request('GET',path)[0],503)
            self.assertEqual(request('HEAD',path)[0],503)
        for raw in ['{', 'x'*65537, json.dumps(dict(receipt(),commit='c'*40)),
                    json.dumps(dict(receipt(),id='\ud800'))]:
            self.receipt.write_text(raw)
            for path in ['/','/healthz','/version']:
                status, headers, body = request('GET',path)
                self.assertEqual(status,503)
                self.assertNotIn(b'Traceback',body)
                self.assertNotIn(str(self.root).encode(),body)
                self.assertEqual(headers['Cache-Control'],'no-store')
        self.receipt.write_text(json.dumps(receipt()))
        self.assertEqual(request('GET','/healthz')[0],200)
        self.assertEqual(json.loads(request('GET','/version')[2])['commit'],'a'*40)

    def test_invalid_build_processes_fail_without_socket_or_secret(self):
        import subprocess
        import sys
        cases = ['{', '[]', json.dumps(dict(build(),commit='bad')),
                 json.dumps(dict(build(),built_at='yesterday'))]
        for url in ['javascript:SECRET', REPO+'/wrong/1', 'https://evil.invalid/SECRET',
                    'https://user:SECRET@github.com/timmypai/agent-delivery-status/issues/1']:
            data = build(); data['evidence']['issue_url'] = url
            cases.append(json.dumps(data))
        for raw in cases:
            with self.subTest(raw=raw):
                self.metadata.write_text(raw)
                result = subprocess.run([sys.executable,'app.py','--metadata',str(self.metadata),
                    '--receipt',str(self.receipt)],capture_output=True,text=True,timeout=3)
                self.assertEqual(result.returncode,1)
                self.assertEqual(result.stdout,'')
                self.assertEqual(result.stderr,'metadata_unavailable\n')

    def test_real_http_negative_receipts_in_child_process(self):
        import http.client
        import subprocess
        import sys
        from concurrent.futures import ThreadPoolExecutor
        self.receipt.unlink()
        code = ('import app,sys; a=app.Application(sys.argv[1],sys.argv[2]); '
                's=app.make_server(a,"127.0.0.1",0); '
                'print(s.server_port,flush=True); s.serve_forever()')
        process = subprocess.Popen([sys.executable,'-u','-c',code,str(self.metadata),
                                    str(self.receipt)],stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,text=True)
        def cleanup():
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=3)
            process.stdout.close(); process.stderr.close()
        self.addCleanup(cleanup)
        # Bounded startup wait, even if a broken server never prints its port.
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(process.stdout.readline)
            try:
                line = future.result(timeout=3)
            except TimeoutError:
                process.terminate()
                raise
        self.assertTrue(line.strip().isdigit(), 'child must start real loopback HTTP')
        port = int(line)
        def request(path):
            conn = http.client.HTTPConnection('127.0.0.1',port,timeout=3)
            try:
                conn.request('GET',path)
                response = conn.getresponse()
                return response.status,response.read()
            finally:
                conn.close()
        for raw in [None,'{','x'*65537,json.dumps(dict(receipt(),commit='b'*40))]:
            if raw is not None: self.receipt.write_text(raw)
            for path in ['/','/version','/healthz']:
                status, body = request(path)
                self.assertEqual(status,503)
                self.assertNotIn(b'Traceback',body)
                self.assertNotIn(str(self.root).encode(),body)
        self.receipt.write_text(json.dumps(receipt()))
        self.assertEqual(request('/healthz')[0],200)
        self.assertEqual(json.loads(request('/version')[1])['commit'],'a'*40)

    def test_strict_schema_types_and_boundaries(self):
        app = self.app()
        invalid = [dict(receipt(), extra=True), dict(receipt(), id=' '*10),
                   dict(receipt(), id='x'*257), dict(receipt(), id=True),
                   dict(receipt(), deployed_at='2026-01-01T01:00:00+01:00'),
                   dict(receipt(), image_digest='sha256:'+'A'*64)]
        for key in receipt():
            data = receipt(); del data[key]; invalid.append(data)
        for data in invalid:
            with self.subTest(data=data):
                self.receipt.write_text(json.dumps(data))
                self.assertEqual(app.response('/healthz')[0],503)
        self.receipt.write_text(json.dumps(dict(receipt(),id='x'*256)))
        self.assertEqual(app.response('/version')[0],200)
        self.receipt.write_bytes(b'\xff')
        self.assertEqual(app.response('/version')[0],503)
        for data in [dict(build(), extra=True), dict(build(), release=True),
                     dict(build(), evidence=dict(build()['evidence'], extra='bad'))]:
            self.metadata.write_text(json.dumps(data))
            with self.assertRaises(ValueError): self.app()

    def test_missing_metadata_process_fails_without_traceback(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable,'app.py','--metadata',str(self.root/'SECRET'),
            '--receipt',str(self.receipt)],capture_output=True,text=True,timeout=3)
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('SECRET',result.stdout+result.stderr)
        self.assertNotIn('Traceback',result.stdout+result.stderr)
