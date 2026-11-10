# v2 candidate evidence — not independent acceptance

Board agent-team; source-author card t_9e429a39; run 10; profile developer.
Base C1: d5db299057d7c28c884f4238db8e4f562c5b85fa.
Independent v1 approval: card t_46dfc432, reviewer run 9, full 14-test suite
exit 0, recorded in `.delivery/run9-independent-review.md` and
`.delivery/run9-review-full.txt`. That approval does not cover v2.
Intended v2 branch: delivery-status/v2-t_9e429a39. C2 is pending DevOps seal.

## Changes and preserved boundaries

VERSION is 1.0.1. Validated v2 build identity derives an exact source_url and
escaped clickable permalink. v1 metadata keeps the prior schema and response.
Receipt failure still fails closed, and neither environment variables nor
caller-provided source_url can replace the cached build identity.
All prior HTTP tests remain in default discovery. The added real v2 loopback
test verifies JSON/HTML, HEAD, method rejection, mismatched receipt and recovery.
Docker smoke expectations now cover v2's additive field and HTML link; the
Dockerfile, build producer/shell tooling and workflow_dispatch-only test and
docker-smoke jobs remain present. No automatic workflow event was added.
Approved spec/matrix and historical evidence are unchanged.

## Executed checks

Working directory: /opt/data/agent-team/projects/delivery-status/repo.
The exact named offline command is in README Local verification; it runs
12 named AppTests methods and both BuildTests methods, with
`PYTHONDONTWRITEBYTECODE=1 python -m unittest -v`.
Result: 14 tests OK, exit 0; `.delivery/run10-offline.txt`.
Before changes, the same subset without the two v2 methods ran 12 tests OK,
exit 0; `.delivery/run10-baseline.txt`.

TDD: `tests.test_app.AppTests.test_v2_source_permalink_is_exact_and_safe`
failed against v1's release rejection (exit 1, run10-red-behavior.txt), then
passed (exit 0, run10-green-feature-fixed.txt). The initial test had an extra
parenthesis (run10-red.txt), then a second synthetic SHA had 42 characters
(run10-green-feature.txt); both fixture defects were corrected, with their
failed logs retained. No validator was relaxed to accommodate invalid SHAs.
`tests.test_build.BuildTests.test_metadata_producer_requires_evidence_and_uses_actual_head`
failed expecting 1.0.1 before VERSION changed (exit 1, run10-red-version.txt),
then passed in the offline suite. These are development/TDD fixture iterations,
not fabricated independent review returns. v2 release review repair count 0/2;
upstream v1 repair count remains 1/2 and is not reset.

- `PYTHONPYCACHEPREFIX=/opt/data/agent-team/projects/delivery-status/repo/.cache/pycache python -m compileall -q app.py scripts tests`: exit 0, run10-syntax.txt.
- `sh -n scripts/build-image.sh`: exit 0, run10-shell.txt.
- `GIT_OPTIONAL_LOCKS=0 git -c core.fsmonitor=false -c core.hooksPath=/dev/null diff --check`: exit 0.
- `sha256sum docs/spec.md docs/acceptance-matrix.md .delivery/run9-review-full.txt`: matches approved v1 hashes.
- `command -v ruff; command -v mypy`: exit 127, neither installed; no installation or lint/type PASS claimed.

## Remaining gates

HTTP/FULL SUITE NOT VERIFIED IN DEVELOPER LANE. No sockets or Docker were
executed here. Independent reviewer must inspect safety first, then run
`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v` at immutable
C2, including all three real HTTP tests. Full actual GREEN is required.
Offline results permit only a frozen candidate Git seal, not review approval.
No Developer Git metadata mutation, push, PR, CI run, image build, deployment,
external link existence check, browser rendering or infrastructure change.
CI NOT RUN; Docker NOT BUILT; Oracle NOT DEPLOYED; original cloud root held.
After freeze, source stays untouched until DevOps custody completes; a later
Developer run verifies C2/hashes and the same offline command before SAME-CARD
independent review. Native Kanban, not this report, owns lifecycle state.
