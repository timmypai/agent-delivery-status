# v1 partial implementation evidence — NOT accepted

Board agent-team; card t_46dfc432; Developer run 5 (native kanban_show).
Workspace: /opt/data/agent-team/projects/delivery-status/repo.
Owner: developer. Runtime limit 1200 seconds; failure threshold requested 2;
no runtime policy/configuration was modified. No review cycles have occurred.

## Inputs and base

Read full project repo-only-continuation.md, Architect run1 spec.md and
acceptance-matrix.md, provisioning run4 JSON and native upstream handoffs.
Exact approved documents copied into docs, sha256sum exit 0:

- spec.md: a8fb9f3643fd3fae2a772dd90da5d0f8d2a0f91e419c0acae8f13ee6561bcb4d
- acceptance-matrix.md: 622776b50d2d81d05b059613e89032a9d6a225b88720269fa51d0bb87f7e7471

Initial `git status --short` empty; `git rev-parse HEAD` returned
f0da404e26ed3aea6f0768ff6252f049f25dd37c; branch main. All read-only Git
commands succeeded. No branch creation, index/commit or other Git mutation was
attempted: latest continuation explicitly delegates Git sealing to a separately
assigned DevOps task and forbids testing the known Developer metadata denial.
Product files are uncommitted in the fixed shared directory, NOT committed to
main. No other writer should edit this frozen snapshot until native handoff.
No product head, PR head, image digest or independent verdict exists yet.

## Actual execution

Python 3.14.9. All commands from repository root. Logs are preserved verbatim,
including historical failures; filenames beginning green describe the attempted
TDD phase, NOT an overall pass (green-http and syntax FAILED).

| Command | Exit | Result / full log |
|---|---:|---|
| python -m unittest discover -s tests -v (empty baseline) | 5 | Ran 0 tests; NO TESTS RAN |
| python -m unittest discover -s tests -v (version RED) | 1 | 1 failure; red-version.txt |
| same (version GREEN) | 0 | 1 passed; green-version.txt |
| same (validation RED) | 1 | 6 tests, 20 subtest failures / 4 errors; red-validation.txt |
| same (validation GREEN) | 0 | 6 passed; green-validation.txt |
| same (HTTP RED) | 1 | 8 tests, 2 failures; red-http.txt |
| same (HTTP implementation) | 1 | 8 tests, 7 passed / 1 socket error; green-http.txt |
| python -m unittest discover -s tests -p test_build.py -v (RED) | 1 | 2 failed; red-build.txt |
| same (GREEN) | 0 | 2 passed; green-build.txt |
| python -m compileall -q app.py scripts tests | 1 | read-only bytecode cache errors; syntax.txt |
| sh -n scripts/build-image.sh | 0 | no output |
| git diff --check | 0 | no output; tracked README only, not a full untracked-file audit |
| python --version | 0 | Python 3.14.9 |

Exact HTTP capability error at socket.socket creation:
`PermissionError: [Errno 1] Operation not permitted`.
Exact compileall errors:
`OSError: [Errno 30] Read-only file system: '/opt/data/.cache'`.
No retry with another tool, host change, escalation, test skipping or lower
acceptance threshold. No socket was created; no server remained running.
Final combined 10-test suite has NOT been rerun because it would repeat the
unchanged socket denial. No claim of a complete green suite or static gate PASS.

## Files and coverage

app.py: strict size-bounded JSON/build validation, duplicate-key rejection,
fixed repository/evidence URLs, UTC timestamps, immutable startup build,
dynamic receipt checks and recovery, escaped HTML, JSON health/version,
HTTP GET/HEAD/405/404 and security headers, sanitized logging/startup errors.
Tests: synthetic-only fixtures, validation/HTML/dynamic-health/env override,
real HTTP behavior test (blocked), process failure, metadata producer and
Docker/manual workflow boundary checks. VERSION 1.0.0.
Dockerfile: nonroot, OCI revision/metadata consistency assertion.
scripts/build_metadata.py and build-image.sh: actual HEAD metadata producer
and explicitly parameterized build command. Neither Docker nor build-image.sh
was executed; shell parsing only. No image claims.
.github/workflows/manual.yml: JSON-valid YAML, workflow_dispatch only, test job
with exact github.sha checkout. Required release docker-smoke job is NOT yet
implemented; do not call this release CI ready. README documents all limitations.
No dependencies installed; no credentials/runtime/configuration/system changes.

## Outstanding gates and next step

1. Existing controller must resolve native test capability without this worker
   bypassing restrictions; preserve/re-run the mandatory full suite afterward.
   Bytecode-cache capability also needs an authorized resolution.
2. Finish required release Docker-smoke definition and verify all applicable
   P1–P4 behavior; actual container P4 is unverified and daemon access prohibited
   in this phase. No skipped tests or synthetic deployment acceptance allowed.
3. Controller must assign the authorized separate DevOps seal handoff (no such
   seal card was present among inspected children). Frozen manifest JSON lists
   exact file hashes and base; no concurrent code writes while sealing. DevOps
   must not author product changes and must return exact feature branch/head.
4. Developer resumes, verifies sealed tree/head and actual tests, then requests
   SAME-CARD reviewer. Do not complete this card or bypass review now.

Inspected children t_06f86c8b (verifier), t_7e6e035f (publication), t_9e429a39
(v2) are NOT independent review/sealing cards. No child created or lifecycle
changed. Native task state is authoritative; this file is evidence only.

CI NOT RUN; Docker NOT BUILT; Oracle NOT DEPLOYED; PR not created/pushed.
Independent review NOT RUN. Original cloud root t_44704c9f remains held.
This partial local work is neither repo-ready acceptance nor cloud acceptance.
