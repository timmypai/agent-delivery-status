"""Read-only PR CI admission/provenance. Never writes remote state or prints tokens.

Only the admission step receives GH_TOKEN; build, tests and container do not.
All API destinations are fixed api.github.com repository paths, never event URLs.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = 'timmypai/agent-delivery-status'
SHA = re.compile(r'[0-9a-f]{40}')


def linked_issue(number, body):
    # Deliberately fail closed on absent/ambiguous/cross-repository references.
    links = re.findall(r'(?im)^\s*(?:closes|fixes|resolves)\s+#([1-9][0-9]*)\s*[.]?\s*$', body or '')
    if len(links) != 1:
        raise ValueError('exactly one standalone same-repo Closes/Fixes/Resolves #N required')
    issue = int(links[0])
    if number in (2, 4) and issue != {2: 1, 4: 3}[number]:
        raise ValueError('scoped PR/Issue mapping mismatch')
    return issue


def validate_event(event):
    pr = event['pull_request']
    number = event['number']
    if type(number) is not int or number < 1 or number != pr['number']:
        raise ValueError('invalid PR number')
    for repo in (event['repository'], pr['head']['repo'], pr['base']['repo']):
        if repo['full_name'] != REPO or repo.get('private', True):
            raise ValueError('only same-repo PUBLIC PR execution admitted')
    head, base = pr['head']['sha'], pr['base']['sha']
    if not SHA.fullmatch(head) or not SHA.fullmatch(base):
        raise ValueError('invalid event commit')
    return number, head, base


def api(path):
    # Paths are constructed exclusively from fixed literals and validated integers.
    request = urllib.request.Request('https://api.github.com/'+path, headers={
        'Authorization': 'Bearer '+os.environ['GH_TOKEN'],
        'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def verify(job):
    if os.environ['GITHUB_EVENT_NAME'] != 'pull_request' or os.environ['GITHUB_REPOSITORY'] != REPO:
        raise ValueError('unexpected workflow context')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    number, head, base = validate_event(event)
    if git('rev-parse', 'HEAD') != head:
        raise ValueError('actual checkout differs from event PR head')
    repository = api('repos/'+REPO)
    if repository['full_name'] != REPO or repository['private'] or repository['visibility'] != 'public':
        raise ValueError('public/free-runner admission closed')
    live = api(f'repos/{REPO}/pulls/{number}')
    if (live['head']['sha'] != head or live['base']['sha'] != base or
            live['head']['repo']['full_name'] != REPO or live['state'] != 'open'):
        raise ValueError('stale head/base or non-scoped live PR; rerun current event')
    issue = linked_issue(number, live['body'])
    issue_data = api(f'repos/{REPO}/issues/{issue}')
    issue_url = f'https://github.com/{REPO}/issues/{issue}'
    pr_url = f'https://github.com/{REPO}/pull/{number}'
    if ('pull_request' in issue_data or issue_data['html_url'] != issue_url or
            live['html_url'] != pr_url):
        raise ValueError('linked issue/PR identity mismatch')
    run_id = os.environ['GITHUB_RUN_ID']
    attempt = os.environ['GITHUB_RUN_ATTEMPT']
    if not re.fullmatch(r'[1-9][0-9]*', run_id) or not re.fullmatch(r'[1-9][0-9]*', attempt):
        raise ValueError('invalid run identity')
    run = api(f'repos/{REPO}/actions/runs/{run_id}')
    ci_url = f'https://github.com/{REPO}/actions/runs/{run_id}'
    if (run['event'] != 'pull_request' or run['html_url'] != ci_url or
            run['repository']['full_name'] != REPO or run['run_attempt'] != int(attempt) or
            run['path'].split('@')[0] != '.github/workflows/pr.yml'):
        raise ValueError('workflow association mismatch')
    jobs = api(f'repos/{REPO}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100')
    matching = [j for j in jobs['jobs'] if j['name'] == job]
    if jobs['total_count'] > 100 or len(matching) != 1:
        raise ValueError('missing/ambiguous run job association')
    job_data = matching[0]
    check_id = job_data['check_run_url'].rsplit('/', 1)[-1]
    if not re.fullmatch(r'[1-9][0-9]*', check_id):
        raise ValueError('invalid check identity')
    check = api(f'repos/{REPO}/check-runs/{check_id}')
    if check['app']['id'] != 15368 or check['name'] != job:
        raise ValueError('GitHub Actions check source mismatch')
    # PR Actions may associate checks with synthetic merge SHA: retain BOTH.
    record = dict(pr=number, issue=issue, head=head, base=base,
                  tested_tree=git('rev-parse', 'HEAD^{tree}'),
                  github_sha=os.environ['GITHUB_SHA'], run_head=run['head_sha'],
                  workflow_id=run['workflow_id'], run_id=int(run_id), attempt=int(attempt),
                  ci_url=ci_url, job_id=job_data['id'], check_id=int(check_id),
                  check_head=check['head_sha'], app_id=check['app']['id'])
    print(json.dumps(record, sort_keys=True))
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
        summary.write('\nPR CI exact-checkout provenance (not deployment):\n```json\n'+
                      json.dumps(record, indent=2, sort_keys=True)+'\n```\n')
    # Fixed URL prefixes + validated numbers/SHA only; no event body reaches shell.
    with open(os.environ['GITHUB_ENV'], 'a') as output:
        output.write(f'ISSUE_URL={issue_url}\nPR_URL={pr_url}\nCI_URL={ci_url}\n'
                     f'IMAGE_TAG=delivery-status-smoke:{head}\n')


def syntax():
    paths = [ROOT/'app.py', *sorted((ROOT/'scripts').glob('*.py')),
             *sorted((ROOT/'tests').glob('*.py'))]
    for path in paths:
        ast.parse(path.read_text(), filename=str(path))
    subprocess.run(['sh', '-n', 'scripts/build-image.sh'], cwd=ROOT, check=True)
    print(f'syntax OK: {len(paths)} Python files; build-image.sh')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--syntax', action='store_true')
    group.add_argument('--job', choices=('pr-tests', 'pr-docker-smoke'))
    args = parser.parse_args()
    if args.syntax:
        syntax()
    else:
        # Avoid response/error bodies or bearer-bearing request dumps on failure.
        try:
            verify(args.job)
        except Exception as error:
            print('CI admission failed ('+type(error).__name__+'); inspect current PR/run metadata')
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
