"""Produce metadata from actual checkout; caller must externally verify URLs/head."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import REPOSITORY, validate_build


def main():
    parser = argparse.ArgumentParser()
    for name in ('issue-url','pr-url','ci-url','output'):
        parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    try:
        commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        data = validate_build(dict(release=(ROOT/'VERSION').read_text().strip(),
            commit=commit, built_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            repository_url=REPOSITORY, evidence=dict(issue_url=args.issue_url,
            pr_url=args.pr_url,ci_url=args.ci_url)))
        Path(args.output).write_text(json.dumps(data,indent=2)+'\n')
    except (OSError,ValueError,subprocess.CalledProcessError):
        print('metadata_generation_failed',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
