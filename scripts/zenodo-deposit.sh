#!/usr/bin/env bash
set -euo pipefail

api_base="${1:?usage: zenodo-deposit.sh API_BASE TOKEN ARCHIVE}"
token="${2:?usage: zenodo-deposit.sh API_BASE TOKEN ARCHIVE}"
archive="${3:?usage: zenodo-deposit.sh API_BASE TOKEN ARCHIVE}"

auth_url="${api_base}/deposit/depositions?access_token=${token}"
deposition="$(curl --fail --silent --show-error -X POST -H "Content-Type: application/json" -d '{}' "${auth_url}")"
deposition_id="$(jq -r '.id' <<<"${deposition}")"
bucket_url="$(jq -r '.links.bucket' <<<"${deposition}")"

jq '{metadata: .}' zenodo.json > /tmp/mtor-nexus-zenodo-metadata.json
curl --fail --silent --show-error \
  -X PUT \
  -H "Content-Type: application/json" \
  --data @/tmp/mtor-nexus-zenodo-metadata.json \
  "${api_base}/deposit/depositions/${deposition_id}?access_token=${token}" >/dev/null
curl --fail --silent --show-error \
  -X PUT \
  --upload-file "${archive}" \
  "${bucket_url}/$(basename "${archive}")?access_token=${token}" >/dev/null
published="$(curl --fail --silent --show-error \
  -X POST \
  "${api_base}/deposit/depositions/${deposition_id}/actions/publish?access_token=${token}")"

jq -r '.doi // .metadata.prereserve_doi.doi' <<<"${published}"
