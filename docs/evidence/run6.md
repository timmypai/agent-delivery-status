# Run 6 candidate source evidence — NOT delivery acceptance

Board agent-team, card t_46dfc432, native Developer run 6.
Workspace `/opt/data/agent-team/projects/delivery-status/repo`.
Base `f0da404e26ed3aea6f0768ff6252f049f25dd37c` (main, read-only inspection).
Intended DevOps-owned branch `delivery-status/v1-t_46dfc432`.
No product commit/PR head exists at this source freeze. Independent verdict NOT RUN.
No Developer Git metadata writes, socket attempts, Docker execution, hosted CI,
network publication, package installation, runtime or configuration changes.

## Authorization and history

Read complete repo-only-continuation.md and evidence/git-custody-handoff.md.
Native claim is run 6; standalone shell routing task/run variables were absent,
so native kanban_show is authoritative. Existing run5 snapshot and every historic
failure log are preserved unchanged. Run5 manifest remains local historical
custody evidence, excluded from the new staged allowlist (no manifests staged).
The changed test-lane premise authorizes finishing source, not retrying socket
EPERM or writing Git metadata. No counters/history were reset.

Read exact Architect spec and matrix; both imported copies match upstream bytes
and recorded SHA256. Inspected children t_06f86c8b, t_7e6e035f, t_9e429a39:
verification/publication/v2, not separate independent review cards. SAME-CARD
Reviewer remains required after candidate sealing and resumed offline checks.

## Changes and coverage

- Retained stdlib read-only app, fixed v1 1.0.0 schema, immutable build metadata,
  dynamic size-bounded receipt checks, exact GitHub URL allowlist, escaped HTML,
  sanitized errors/logging and HTTP security headers.
- Fixed Unicode receipt validation at its input boundary. Escaped lone surrogate
  IDs previously passed validation and crashed HTML UTF-8 encoding; DEL/C1
  controls are now rejected too. RED recorded two encoding errors/one failure;
  same test GREEN after a single correction. No renderer workaround/mocking.
- P1: real HTTP GET/HEAD/body/header/405/path traversal/link assertions retained
  and extended; no skip decorators/environment skips.
- P2: pure validation/security/URL negatives plus independent-process malformed
  build cases. Added real child-process loopback missing/oversized/mismatched/
  corrupt receipt tests, unexecuted in Developer lane.
- P3: pure and genuine HTTP receipt invalidation/recovery, no cached green.
- P4: pure immutable-build/environment and fresh-build identity checks; manual
  Docker smoke defines actual OCI/image identity and environment override tests,
  plus a second synthetic C_B image. Actual container P4 NOT VERIFIED.
- workflow_dispatch ONLY, jobs test and docker-smoke, read-only contents,
  exact github.sha checkout/no persisted credentials, bounded jobs. Real smoke
  uses ephemeral loopback/nonroot/read-only/cap-drop/resource limits/test receipt,
  cleanup, and no registry publication. Docker/CI execution NOT performed.
- README documents commands, test-only fixtures, independent/full-suite gate,
  build/receipt provenance limits and unrun cloud gates. No v2 implementation.

## Actual checks

Exact commands/exits: `run6-commands.json`; full output in `run6-final-*.txt`.
Initial explicitly named offline baseline: 9 tests, exit 0 (run6-baseline.txt).
New Unicode regression RED exit 1, GREEN exit 0. Missing docker-smoke definition
RED exit 1, GREEN exit 0. Additional offline negative cases: 2 passed, exit 0.
Final named offline subset: 12 tests passed, exit 0. The two BuildTests methods
are test_metadata_producer_requires_evidence_and_uses_actual_head and
 test_container_and_workflow_definition_boundaries (both explicitly listed in log).
Syntax uses command-local repo/.cache PYTHONPYCACHEPREFIX: exit 0.
`sh -n scripts/build-image.sh`: exit 0. Read-only `git diff --check`: exit 0,
limited to tracked README; separate static check covers authored Python whitespace.
Static assertions cover manual-only workflow, both jobs/no conditional bypass,
all shell step parsing, Python AST, no eval/exec/shell=True, unconditional HTTP
integration tests and byte-identical Architect imports: exit 0.
No third-party lint/type/security scanner run; stdlib project has no added
runtime dependencies. Lightweight static assertions are not a formal audit.

**HTTP/full suite NOT VERIFIED IN DEVELOPER LANE.** Two excluded methods:
`test_real_http_contract`, `test_real_http_negative_receipts_in_child_process`.
Reviewer must FIRST inspect test/code safety then run the full unchanged
`python -m unittest discover -s tests -v` at sealed immutable C in its existing
native authorized runtime. No Developer remote-exec workaround. Full actual
GREEN is required before independent PASS/completion/publication.

## Custody and remaining gates

New manifest under .delivery records explicit source allowlist/modes/SHA256,
base, branch, deletions (none), test logs and repair accounting, excluding itself,
all manifests/.git/cache/pycache/secrets. Native freeze comment marks end of
source writes. DevOps-only helper may seal that candidate after verifying linked
settled handoff/no conflicting author; no product editing or product execution.
No normal review cycle yet (0). Conservatively account run6 Unicode fix as one
normal repair used of max two; one remaining. Feature-completion RED/GREEN for
missing workflow is not a review rework cycle. Historical run5 TDD and capability
failure remain as recorded; no counter reset/reclassification to a test PASS.

After helper completion, Developer verifies exact HEAD/frozen hashes, reruns
ONLY named offline tests unchanged, then requests SAME-CARD independent review.
No source writes while frozen/dependency pending. If a native handoff is refused,
retain error and stop without CLI/DB/alternate-tool ownership bypass.

CI NOT RUN; Docker NOT BUILT; Oracle NOT DEPLOYED; no push/PR/merge.
Independent verdict NOT RUN. Original cloud root t_44704c9f remains held.
