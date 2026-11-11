#!/bin/sh
# Requires separately authorized Docker access and verified real evidence URLs.
set -eu
: "${ISSUE_URL:?verified issue URL required}"
: "${PR_URL:?verified exact-head PR URL required}"
: "${CI_URL:?actual build run URL required}"
: "${IMAGE_TAG:?explicit local image tag required}"
cd "$(dirname "$0")/.."
test -z "$(git status --porcelain --untracked-files=normal)"
commit=$(git rev-parse HEAD)
python scripts/build_metadata.py --issue-url "$ISSUE_URL" --pr-url "$PR_URL" --ci-url "$CI_URL" --output build-metadata.json
docker build --build-arg "COMMIT=$commit" --tag "$IMAGE_TAG" .
