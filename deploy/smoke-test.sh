#!/bin/sh
set -eu
base_url="${1:?usage: smoke-test.sh https://your-domain}"
curl --fail --silent --show-error "$base_url/api/v1/health"
curl --fail --silent --show-error "$base_url/docs" >/dev/null
printf '\nSmoke test OK: %s\n' "$base_url"
