# Delivery Status 1.0.0

Python standard-library read-only service: `GET`/`HEAD` `/`, `/healthz`, `/version`.
No database, runtime GitHub calls, credentials, write API or background poller.
Health means **local metadata health, not delivery acceptance**.

## Local verification

Requires Python 3.14 and permission to create ephemeral loopback sockets. No
packages need installation. From this repository:

```sh
python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX="$PWD/.cache/pycache" python -m compileall -q app.py scripts tests
sh -n scripts/build-image.sh
```

Tests create explicitly synthetic metadata in temporary directories, bind only
127.0.0.1 on an ephemeral port and close/join their server on cleanup. Synthetic
URLs, commits and digests in tests are NOT release evidence. Do not deploy them.
The Developer lane runs only the explicit offline subset below. Full discovery
unconditionally includes real HTTP tests and is required in the independent
Reviewer lane at the sealed commit. It is **NOT VERIFIED in the Developer lane**.
The historical socket/cache failures remain in `docs/evidence/repo-night-v1.md`;
the changed lane does not erase them. Latest evidence: `docs/evidence/run6.md`.

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v \
  tests.test_app.AppTests.test_version_reports_build_and_deployment \
  tests.test_app.AppTests.test_invalid_build_rejected \
  tests.test_app.AppTests.test_receipt_invalidates_immediately_and_recovers \
  tests.test_app.AppTests.test_html_escapes_values_and_links_are_safe \
  tests.test_app.AppTests.test_unknown_paths_are_not_files \
  tests.test_app.AppTests.test_invalid_unicode_receipt_fails_closed \
  tests.test_app.AppTests.test_runtime_environment_cannot_replace_cached_build \
  tests.test_app.AppTests.test_missing_metadata_process_fails_without_traceback \
  tests.test_app.AppTests.test_invalid_build_processes_fail_without_socket_or_secret \
  tests.test_app.AppTests.test_strict_schema_types_and_boundaries \
  tests.test_build.BuildTests
```

This is not an alternative acceptance command. It excludes exactly the real
HTTP tests `test_real_http_contract` and
`test_real_http_negative_receipts_in_child_process`, neither skipped nor mocked.

## Metadata and startup

Build JSON has exactly `release`, `commit`, `built_at`, `repository_url`, and
`evidence` (`issue_url`, `pr_url`, `ci_url`). See the byte-preserved approved
[spec](docs/spec.md) and [acceptance matrix](docs/acceptance-matrix.md).
The producer reads the actual local Git HEAD and VERSION, and timestamps its
execution. It validates syntax but cannot prove remote Issue/PR/run existence:
publication roles must read back those exact objects and match PR head first.
Missing URLs fail; there are no default release fixtures.

```sh
python scripts/build_metadata.py --issue-url "$ISSUE_URL" --pr-url "$PR_URL" \
  --ci-url "$CI_URL" --output build-metadata.json
python app.py --metadata build-metadata.json --receipt "$RECEIPT_PATH"
```

Default bind is loopback port 8080. Metadata is validated and cached at startup;
COMMIT/GITHUB_SHA environment variables cannot replace it. Receipt is read and
validated afresh per request, with a 64 KiB bound. Missing/corrupt/mismatched
receipt returns 503 and never stale green. Invalid build metadata exits nonzero
without paths/tracebacks. Duplicate JSON keys, unknown fields, invalid types,
non-UTC timestamps and non-allowlisted evidence URLs are rejected.

A real deployment receipt must be supplied by the authorized deployer with
`id`, `deployed_at`, `commit`, `image_digest`. It must match the baked full commit;
digest is `sha256:` plus 64 lowercase hex. Receipt ID must contain no secrets.
The receipt is a claim, not proof of the running image: external image/container
inspection and independent exact-head review remain mandatory.

## Container and manual CI boundaries

Dockerfile runs UID/GID 65532:65532, serves container port 8080, and checks baked
metadata against the OCI revision build argument. Runtime cannot override it.
`sh scripts/build-image.sh` requires a clean sealed checkout and explicit real
`ISSUE_URL`, `PR_URL`, `CI_URL`, `IMAGE_TAG`. It must only be run after separate
Docker/build authorization. Deployment must enforce read-only root filesystem,
read-only app-specific receipt mount, no privileges/socket/host namespaces,
CPU <=0.5, memory <=128 MiB and pids <=64, on explicitly approved host/path/port.
Dockerfile alone does not enforce those runtime options.

The workflow is JSON (valid YAML) and has **workflow_dispatch only**. There are
no automatic events. Do NOT dispatch until the private Actions free-budget and
no-paid-overage gates are proven. It defines both `test` and `docker-smoke`,
checking out `github.sha` with persisted credentials disabled. Select the exact
reviewed author head; supply externally verified Issue and same-head PR URLs.
Input values enter shell steps via environment variables, not shell interpolation.
The actual workflow run URL is supplied by GitHub at build time. The workflow
cannot itself establish independent review or that user-supplied URLs exist.

The smoke command (separate Docker authorization required) is:

```sh
python scripts/docker_smoke.py --image "$IMAGE_TAG" --metadata build-metadata.json
```

It starts only isolated nonroot read-only containers with an ephemeral loopback
port, no capabilities, resource limits and a read-only test receipt mount. It
checks real HTTP, OCI revision/image ID, mounts, invalid/missing receipt and
recovery, and an attempted runtime commit override. A second **synthetic** build
with C_B tests different baked identity. Test containers and that fixture image
are removed; the first candidate image remains for separately authorized gates.
Synthetic receipts are labeled NOT DEPLOYED. Local image IDs are not registry
digests. Neither smoke success nor URL syntax proves a real deployment.

Exact-head required-check association, real CI/image execution, external evidence
readbacks and deployment verification remain outstanding. Do not treat future
`test` success alone as release PASS. No workflow uploads/pushes artifacts/images.

**CI NOT RUN. Docker NOT BUILT. Oracle NOT DEPLOYED. No push or PR by Developer.**
Independent review and Git sealing are pending. The original cloud root remains
held. This repository work is not cloud acceptance. v2 is a separate authorized
incremental change after v1 independent review, not part of this implementation.
