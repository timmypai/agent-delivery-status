# PR exact-head CI and native auto-merge publication contract

This is **configuration/design, not hosted CI or deployment evidence**. Stage1 is
local-only; a new exact candidate needs independent SAME-CARD native Reviewer
approval before publication. Historical C1/C2 approvals do not approve it.

## Automatic bootstrap and bounded execution

`pr.yml` is JSON-compatible YAML. PR2 already exists and main is README-only:
publication appends the independently reviewed commit to the existing v1 branch,
never main. Its `pull_request` synchronize/ready/edited events bootstrap the new
workflow without relying on feature-only manual workflow discovery. The trigger
also includes opened/reopened; no draft/path skips or privileged target events.
Legacy `manual.yml` stays historical and has different context names. Do not
manually dispatch it as a substitute for required PR checks.

Only standard public `ubuntu-24.04`, two jobs <=10 minutes each, no caches,
uploads, registry push, environments/secrets or paid services. Stage2 must freshly
verify repository PUBLIC before publication/ready or other hosted admission; a
runner step cannot prevent its own allocation. Each job additionally verifies
live public status before tests/build and stops if private. Existing v1/v2 source
and full integration tests are preserved. No local Docker access is authorized
by this document. Docker build and actual smoke execute only on hosted runners
in the subsequent publication stage.

Required unique contexts: `pr-tests` then dependent `pr-docker-smoke`. Both use
Python3.14; tests run the full suite, including genuine loopback and negative
receipt paths (no skip/mock substitutes). Syntax checks parse Python sources
without writing bytecode and check shell syntax. Docker uses the actual checkout,
existing metadata producer, `sh scripts/build-image.sh`, and existing
`scripts/docker_smoke.py` HTTP/security/negative/two-build smoke. Synthetic smoke
receipts and the second image remain TEST ONLY, never Oracle deployment evidence.

## Immutable official action provenance

Resolved using GET-only official `repos/actions/{name}/git/ref/tags/{tag}`, official
repository identity, release and exact commit endpoints on 2026-11-11:

| Action | Official release tag | Immutable commit | Commit verification |
|---|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 | API verified=true |
| actions/setup-python | v7.1.0 | 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 | API verified=true |

Both refs directly target commits; official owner is `actions`, repositories
not archived, releases neither draft nor prerelease. These are selected release
SHAs, not guesses or moving latest aliases. Official release pages:
https://github.com/actions/checkout/releases/tag/v7.0.1 and
https://github.com/actions/setup-python/releases/tag/v7.1.0.

## Head, metadata and check provenance

Checkout uses event PR **head.sha**, persist-credentials=false. Each job's
`scripts/ci_pr.py` confirms actual git HEAD == event head; checks same-repo public
event and live PR identity/head/base/state, and validates real linked Issue API
identity (not a PR). PR2 must close Issue1; PR4 must close Issue3. In addition to
bare closing lines, admission accepts these exact existing historical lines only
for their corresponding scoped PR (verified by GET-only live projections):

- PR2: `Closes #1 (repository milestone only).`
- PR4: `Closes #3 (repository milestone only): https://github.com/timmypai/agent-delivery-status/issues/3`

This is narrow local parser compatibility, not a prerequisite remote body edit.
Suffixes are compared as data, never executed or fetched. Other suffixes, wrong
issue/repository/URL, query/fragment/userinfo and injection-shaped lines fail.
All standalone closing-keyword lines are counted before parsing, so a valid line
cannot hide an additional malformed or cross-repository closing reference.
Future same-repo PRs must contain exactly one standalone `Closes #N`, `Fixes #N`
or `Resolves #N` line (case-insensitive, optional trailing period), with a real
same-repo issue, or admission fails clearly. Forks fail closed. Behavioral tests
exercise these actual-format fixtures, ambiguity/security negatives and future-PR
controls; they do not mock or replace genuine HTTP/negative integration tests.

Only metadata admission has a step-local read-only `github.token` as GH_TOKEN.
Permissions: contents, pull-requests, issues, actions, checks read only. No write
scope. The token is never written to GITHUB_ENV, checkout credentials, metadata,
logs, tests, app or Docker. API calls use fixed api.github.com paths; event body
or API URLs cannot select a network destination. Validated integers construct
URLs, and no untrusted event metadata is interpolated into shell source.

Logs and job summary record actual head/base/tested tree, synthetic GITHUB_SHA,
run head/workflow ID/run ID/attempt/URL, job ID/check ID/check head and verified
GitHub Actions app15368. Checks may be associated with a synthetic merge SHA;
that is NOT the tested head. Stage2 independently correlates run/event PR
association and these records with the current reviewed PR head. Do not demand
that a PR-head checkout equal synthetic GITHUB_SHA, nor call old-head green valid.

Build URL is actual `https://github.com/timmypai/agent-delivery-status/actions/runs/N`;
issue/PR URLs are validated real scope. Existing producer obtains commit from
actual git HEAD. No fabricated deployment receipt, run URL or status success.
No metadata admission API calls are made by the local unit fixture tests.

## External main guard: stage2 only, before ready

First GET main protection, repository rulesets and effective main rules, current
PR/base/head and public/auto-merge status; reconcile fresh external settings.
404 means absent only if independently confirmed as such, not a blanket success.
Preserve stronger existing settings. If settings conflict or cannot be read back,
hold rather than replace/disable them. Never blindly PUT this design over user
policy. No remote guard/status/ready writes occur in stage1.

Minimum branch protection design (JSON; reconcile before applying):

```json
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "pr-tests", "app_id": 15368},
      {"context": "pr-docker-smoke", "app_id": 15368},
      {"context": "native-review", "app_id": -1}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
```

`restrictions:null`, zero forge approvals and false review options describe the
minimum absent-policy case ONLY: preserve any existing restrictions/stronger
review requirements. Zero forge approvals is allowed with mandatory independent
native-review, NOT a second-account human review claim. app_id=-1 intentionally
means non-App/external status and is not an identity-authenticated Reviewer app.
Stage2 must verify native task/run exact-head verdict before posting status.
GitHub Actions app15368 must be freshly verified via `apps/github-actions`.
Read back protection/effective rules, strict/admin/force/delete/PR/context source
requirements and actual PR blockers before ready. Empty checks or mergeable CLEAN
alone never mean required checks succeeded.

## Publication handoff and native waiting proof

1. Consume exact independently reviewed SHA/tree/logs; verify C1 ancestry and
   allowlisted CI-only diff. No source edits in publication; no force/rebase/reset.
2. Reconcile guard above while PR2 still draft; create native-review PENDING at
   candidate. Recheck PUBLIC; append reviewed SHA to existing PR2 branch only.
   Read back exact head and protection before ready. No unrelated PR/new identity.
3. Arm GitHub native auto-merge with `--auto --merge --match-head-commit <SHA>`
   (or exact supported GraphQL equivalent), preserving original ancestry and
   v1 branch needed by PR4. Native-review remains PENDING even though its real
   independent verdict has already been checked.
4. Save actual autoMergeRequest non-null, PR OPEN, current exact head/timestamp
   and required review/CI pending snapshot. Without this queue proof do not
   substitute an ordinary/manual merge. No --admin, force or spoofed CI statuses.
5. Recheck head unchanged, then publish native-review SUCCESS tied to actual
   Reviewer card/run. GitHub alone merges after required actual non-skipped CI
   success and strict current-base requirements. Save jobs/logs/provenance and
   actual merged_at/merge commit/parents/tree/main/protection readbacks.
6. PR2 MERGED precedes v2 main integration/new exact-head independent review and
   PR4 retarget/ready/merge. Never delete v1 while PR4 depends on it.

Missing capability/error => preserve exact command and sanitized error, stop
that gate; no downgrade/permission/runtime changes. CI config failures return to
bounded CI author + SAME-CARD review; actual product failures go to Controller
for Developer/AppServer frozen-source custody + review, not DevOps product edits.
Max two normal repair/review rounds; native runtime/retry bounds remain separate.
No new dispatcher/worker harness. Original cloud/voice holds stay unchanged.
