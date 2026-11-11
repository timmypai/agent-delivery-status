"""Build tooling tests: all evidence URLs here are synthetic fixtures only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/timmypai/agent-delivery-status'


class BuildTests(unittest.TestCase):
    def test_metadata_producer_requires_evidence_and_uses_actual_head(self):
        script = ROOT/'scripts/build_metadata.py'
        self.assertTrue(script.exists(), 'Metadata producer required')
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'metadata.json'
            command = [sys.executable,str(script),'--output',str(output)]
            missing = subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(missing.returncode,0)
            self.assertFalse(output.exists())
            good = subprocess.run(command+['--issue-url',REPO+'/issues/1',
                '--pr-url',REPO+'/pull/1','--ci-url',REPO+'/actions/runs/1'],capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            data = json.loads(output.read_text())
            actual = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
            self.assertEqual(data['commit'],actual)
            self.assertEqual(data['release'],'1.0.0')
            self.assertNotIn('image_digest',data)
            from app import validate_build
            validate_build(data)
            bad = subprocess.run(command+['--issue-url','javascript:bad',
                '--pr-url',REPO+'/pull/1','--ci-url',REPO+'/actions/runs/1'],capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)

    def test_container_and_workflow_definition_boundaries(self):
        self.assertTrue((ROOT/'Dockerfile').exists(), 'Docker definition required')
        docker = (ROOT/'Dockerfile').read_text()
        self.assertIn('USER 65532:65532',docker)
        self.assertIn('org.opencontainers.image.revision',docker)
        self.assertNotIn('docker.sock',docker)
        workflow = json.loads((ROOT/'.github/workflows/manual.yml').read_text())
        self.assertEqual(set(workflow['on']), {'workflow_dispatch'})
        self.assertEqual(workflow['permissions'], {'contents':'read'})
        self.assertIn('test',workflow['jobs'])
        self.assertIn('docker-smoke',workflow['jobs'])
        smoke = workflow['jobs']['docker-smoke']
        self.assertEqual(smoke['needs'], 'test')
        self.assertLessEqual(smoke['timeout-minutes'], 10)
        commands = '\n'.join(step.get('run','') for step in smoke['steps'])
        self.assertIn('sh scripts/build-image.sh', commands)
        self.assertIn('python scripts/docker_smoke.py', commands)
        self.assertNotIn('docker push', commands)
        for job in workflow['jobs'].values():
            checkout = next(s for s in job['steps'] if s.get('uses','').startswith('actions/checkout@'))
            self.assertEqual(checkout['with']['ref'], '${{ github.sha }}')
            self.assertFalse(checkout['with']['persist-credentials'])
