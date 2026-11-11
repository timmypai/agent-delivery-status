import ast
import hashlib
import json
from pathlib import Path
import subprocess

root = Path.cwd()
workflow = json.loads((root/'.github/workflows/manual.yml').read_text())
assert set(workflow['on']) == {'workflow_dispatch'}
assert set(workflow['jobs']) == {'test', 'docker-smoke'}
assert workflow['permissions'] == {'contents':'read'}
for job in workflow['jobs'].values():
    assert 'if' not in job and not job.get('continue-on-error', False)
    for step in job['steps']:
        if 'run' in step:
            assert '${{' not in step['run']
            subprocess.run(['sh','-n'], input=step['run'], text=True, check=True)
paths = [Path('app.py'), *Path('scripts').glob('*.py'), *Path('tests').glob('*.py')]
for path in paths:
    assert not path.is_symlink()
    tree = ast.parse(path.read_text(), filename=str(path))
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id in {'eval','exec'} for n in ast.walk(tree))
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            assert not any(k.arg == 'shell' and isinstance(k.value,ast.Constant)
                           and k.value.value is True for k in n.keywords)
        if isinstance(n, ast.FunctionDef) and n.name.startswith('test_real_http'):
            assert not n.decorator_list
            assert not any(isinstance(c,ast.Attribute) and c.attr == 'skipTest'
                           for c in ast.walk(n))
    assert all(not line.rstrip('\n').endswith((' ', '\t')) for line in path.read_text().splitlines(True))
for path in ['spec.md','acceptance-matrix.md']:
    assert (root/'docs'/path).read_bytes() == (root.parent/path).read_bytes()
    print(path, hashlib.sha256((root/'docs'/path).read_bytes()).hexdigest())
print('PASS: manual-only jobs, no conditional bypass, shell parsing, Python AST, no eval/exec/shell=True, real HTTP tests unconditional, source whitespace, exact Architect imports.')
print('Scope: lightweight static assertions/manual source review; no third-party linter/type checker/security scanner installed or run. No socket, Docker or network invoked.')
