"""CI configuration policy; synthetic event fixtures are NOT hosted execution."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PINS = {'actions/checkout': '3d3c42e5aac5ba805825da76410c181273ba90b1',
        'actions/setup-python': '6d4fd22b20465ccc0f7354476588e8df7c9ca0e0'}
PERMISSIONS = {'contents': 'read', 'pull-requests': 'read', 'issues': 'read',
               'actions': 'read', 'checks': 'read'}


def validate_policy(workflow):
    """Fail closed on unbudgeted execution, credential exposure or missing gates."""
    assert set(workflow) == {'name', 'on', 'permissions', 'jobs'}
    assert workflow['on'] == {'pull_request': {'types': [
        'opened', 'synchronize', 'reopened', 'ready_for_review', 'edited']}}
    assert workflow['permissions'] == PERMISSIONS
    assert set(workflow['jobs']) == {'pr-tests', 'pr-docker-smoke'}
    for name, job in workflow['jobs'].items():
        assert set(job) == ({'runs-on', 'timeout-minutes', 'env', 'steps'} |
                            ({'needs'} if name == 'pr-docker-smoke' else set()))
        assert job['runs-on'] == 'ubuntu-24.04'
        assert type(job['timeout-minutes']) is int and 0 < job['timeout-minutes'] <= 10
        assert job['env'] == {'PYTHONDONTWRITEBYTECODE': '1'}
        actions = [s for s in job['steps'] if 'uses' in s]
        assert len(actions) == 2
        assert actions[0] == {'uses': 'actions/checkout@'+PINS['actions/checkout'],
                              'with': {'ref': '${{ github.event.pull_request.head.sha }}',
                                       'persist-credentials': False}}
        assert actions[1] == {'uses': 'actions/setup-python@'+PINS['actions/setup-python'],
                              'with': {'python-version': '3.14'}}
        verify = job['steps'][2]
        assert verify == {'name': 'Verify head, public budget, metadata and check association',
                          'env': {'GH_TOKEN': '${{ github.token }}'},
                          'run': 'python scripts/ci_pr.py --job '+name}
        for step in job['steps'][3:]:
            assert set(step) == {'name', 'run'}
            assert '${{' not in step['run']
        if name == 'pr-tests':
            assert [s['run'] for s in job['steps'][3:]] == [
                'python -m unittest discover -s tests -v',
                'python scripts/ci_pr.py --syntax']
        else:
            assert job['needs'] == 'pr-tests'
            assert [s['run'] for s in job['steps'][3:]] == [
                'sh scripts/build-image.sh',
                'python scripts/docker_smoke.py --image "$IMAGE_TAG" --metadata build-metadata.json']


class CIPolicyTests(unittest.TestCase):
    def workflow(self):
        return json.loads((ROOT/'.github/workflows/pr.yml').read_text())

    def test_actual_workflow_policy(self):
        validate_policy(self.workflow())
        # Required context names must remain unique across every workflow.
        names = []
        for path in (ROOT/'.github/workflows').glob('*.yml'):
            for key, job in json.loads(path.read_text())['jobs'].items():
                names.append(job.get('name', key))
        for context in ('pr-tests', 'pr-docker-smoke'):
            self.assertEqual(names.count(context), 1)

    def test_policy_rejects_unsafe_mutations(self):
        for mutation in ('trigger', 'paths', 'draft', 'write', 'runner', 'timeout',
                         'mutable', 'credentials', 'synthetic', 'cache', 'token', 'dependency'):
            with self.subTest(mutation=mutation):
                w = copy.deepcopy(self.workflow())
                j = w['jobs']['pr-tests']
                if mutation == 'trigger': w['on'] = {'pull_request_target': {}}
                if mutation == 'paths': w['on']['pull_request']['paths'] = ['app.py']
                if mutation == 'draft': j['if'] = '${{ !github.event.pull_request.draft }}'
                if mutation == 'write': w['permissions']['contents'] = 'write'
                if mutation == 'runner': j['runs-on'] = 'ubuntu-latest'
                if mutation == 'timeout': j['timeout-minutes'] = 11
                if mutation == 'mutable': j['steps'][0]['uses'] = 'actions/checkout@v7'
                if mutation == 'credentials': j['steps'][0]['with']['persist-credentials'] = True
                if mutation == 'synthetic': j['steps'][0]['with']['ref'] = '${{ github.sha }}'
                if mutation == 'cache': j['steps'].append({'uses': 'actions/cache@v4'})
                if mutation == 'token': j['env']['GH_TOKEN'] = '${{ github.token }}'
                if mutation == 'dependency': del w['jobs']['pr-docker-smoke']['needs']
                with self.assertRaises(AssertionError): validate_policy(w)

    def helper(self):
        spec = importlib.util.spec_from_file_location('ci_pr', ROOT/'scripts/ci_pr.py')
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_linked_issue_validation(self):
        m = self.helper()
        for number, issue in ((2, 1), (4, 3), (8, 9)):
            self.assertEqual(m.linked_issue(number, f'Closes #{issue}'), issue)
        for number, body in ((2, 'Closes #3'), (4, 'Closes #1'),
                             (8, ''), (8, 'Closes other/repo#9'),
                             (8, 'Closes #9\nFixes #10')):
            with self.subTest(number=number, body=body):
                with self.assertRaises(ValueError): m.linked_issue(number, body)

    def test_event_validation_rejects_fork_private_and_bad_sha(self):
        m = self.helper()
        repo = {'full_name': m.REPO, 'private': False}
        event = {'number': 2, 'repository': repo, 'pull_request': {
            'number': 2, 'head': {'sha': 'a'*40, 'repo': repo},
            'base': {'sha': 'b'*40, 'repo': repo}}}
        self.assertEqual(m.validate_event(event), (2, 'a'*40, 'b'*40))
        for kind in ('fork', 'private', 'sha', 'number'):
            bad = copy.deepcopy(event)
            if kind == 'fork': bad['pull_request']['head']['repo'] = {'full_name': 'other/repo'}
            if kind == 'private': bad['repository'] = dict(repo, private=True)
            if kind == 'sha': bad['pull_request']['head']['sha'] = 'bad; command'
            if kind == 'number': bad['number'] = 4
            with self.assertRaises(ValueError): m.validate_event(bad)
