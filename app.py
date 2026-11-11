"""Read-only delivery metadata. No runtime credentials or network clients."""
import copy
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re

REPOSITORY = 'https://github.com/timmypai/agent-delivery-status'
LIMIT = 65536
SHA = r'[0-9a-f]{40}'


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def timestamp(value):
    if not matches(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)', value):
        raise ValueError('metadata_unavailable')
    datetime.fromisoformat(value)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('metadata_unavailable')
        result[key] = value
    return result


def read_json(path):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('metadata_unavailable')
        data = json.loads(raw, object_pairs_hook=pairs)
        if not isinstance(data, dict):
            raise ValueError('metadata_unavailable')
        return data
    except (OSError, ValueError, RecursionError) as exc:
        raise ValueError('metadata_unavailable') from None


def validate_build(data):
    try:
        if set(data) != {'release','commit','built_at','repository_url','evidence'}:
            raise ValueError()
        if data['release'] != '1.0.0' or not matches(SHA, data['commit']):
            raise ValueError()
        timestamp(data['built_at'])
        if data['repository_url'] != REPOSITORY:
            raise ValueError()
        evidence = data['evidence']
        if not isinstance(evidence, dict) or set(evidence) != {'issue_url','pr_url','ci_url'}:
            raise ValueError()
        for key, route in [('issue_url','issues'),('pr_url','pull'),('ci_url','actions/runs')]:
            if not matches(re.escape(REPOSITORY)+'/'+route+r'/[1-9][0-9]*', evidence[key]):
                raise ValueError()
        return copy.deepcopy(data)
    except (KeyError, TypeError, ValueError):
        raise ValueError('metadata_unavailable') from None


def validate_receipt(data, commit):
    try:
        if set(data) != {'id','deployed_at','commit','image_digest'}:
            raise ValueError()
        ident = data['id']
        if not isinstance(ident,str) or not ident.strip() or len(ident) > 256 or any(ord(c)<32 or 127 <= ord(c) <= 159 for c in ident):
            raise ValueError()
        ident.encode('utf-8')
        timestamp(data['deployed_at'])
        if data['commit'] != commit or not matches(r'sha256:[0-9a-f]{64}', data['image_digest']):
            raise ValueError()
        return data
    except (KeyError, TypeError, ValueError):
        raise ValueError('metadata_unavailable') from None


class Application:
    def __init__(self, metadata_path, receipt_path):
        self._build = validate_build(read_json(metadata_path))
        self.receipt_path = receipt_path

    def response(self, path):
        if path not in ('/', '/version', '/healthz'):
            return 404, 'application/json', b'{"error":"not_found"}'
        try:
            receipt = validate_receipt(read_json(self.receipt_path), self._build['commit'])
        except ValueError:
            receipt = None
        healthy = receipt is not None
        status = 200 if healthy else 503
        health = {'status':'ok' if healthy else 'unavailable', 'checks':
                  {'build_metadata':'ok','deployment_receipt':'ok' if healthy else 'invalid'}}
        if path == '/healthz':
            data = health
        elif path == '/version':
            data = dict(schema_version=1, **self._build,
                        deployment={k:receipt[k] for k in ('id','deployed_at')}) if healthy else {'error':'metadata_unavailable'}
        else:
            html = '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>Delivery Status</title><h1>Delivery Status</h1>'
            html += '<p>本機健康（非交付驗收）: '+health['status']+'</p>'
            if healthy:
                html += '<dl>'+''.join('<dt>'+escape(k)+'</dt><dd>'+escape(v)+'</dd>' for k,v in
                    [('Release',self._build['release']),('Commit',self._build['commit']),
                     ('Built at',self._build['built_at']),('Deployment',receipt['id'])])+'</dl>'
                html += '<nav>'+''.join('<a target="_blank" rel="noopener noreferrer" href="'+escape(url,quote=True)+'">'+label+'</a> '
                    for label,url in zip(('Issue','PR','CI'), (self._build['evidence'][k] for k in ('issue_url','pr_url','ci_url'))))+'</nav>'
            return status, 'text/html; charset=utf-8', (html+'</html>').encode()
        return status, 'application/json', json.dumps(data).encode()


def make_server(application, host, port):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        # Deliberately omit request URLs, addresses and environment from logs.
        def log_message(self, *args):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def send_payload(self, status, kind, body, allow=False):
            self.send_response_only(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'")
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Connection', 'close')
            if allow:
                self.send_header('Allow', 'GET, HEAD')
            self.end_headers()
            self.close_connection = True
            if self.command != 'HEAD':
                self.wfile.write(body)

        def do_GET(self):
            self.send_payload(*application.response(self.path))

        do_HEAD = do_GET

        def unsupported(self):
            self.send_payload(405, 'application/json', b'{"error":"method_not_allowed"}', allow=True)

        def __getattr__(self, name):
            if name.startswith('do_'):
                return self.unsupported
            raise AttributeError(name)

        def send_error(self, code, message=None, explain=None):
            self.send_payload(code, 'application/json', b'{"error":"invalid_request"}')

    class Server(HTTPServer):
        def handle_error(self, request, client_address):
            pass

    return Server((host,port),Handler)


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata', default='/app/build-metadata.json')
    parser.add_argument('--receipt', default='/run/delivery/receipt.json')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    try:
        app = Application(args.metadata,args.receipt)
    except ValueError:
        print('metadata_unavailable', file=sys.stderr)
        return 1
    with make_server(app,args.host,args.port) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
