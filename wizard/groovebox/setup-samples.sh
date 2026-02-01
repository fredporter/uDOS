#!/usr/bin/env bash
set -euo pipefail

LIB_ROOT="$(dirname "$0")/library"
SAMPLES_JSON="$(dirname "$0")/sample-library.json"
mkdir -p "$LIB_ROOT"

if [[ ! -f "$SAMPLES_JSON" ]]; then
  echo "Sample metadata missing: $SAMPLES_JSON"
  exit 1
fi

echo "Downloading Groovebox public-domain samples into $LIB_ROOT"

jq -c '.samples[]' "$SAMPLES_JSON" | while IFS= read -r sample; do
  id=$(echo "$sample" | jq -r '.id')
  url=$(echo "$sample" | jq -r '.source')
  name=$(echo "$sample" | jq -r '.name')
  target="$LIB_ROOT/$id"

  if [[ -f "$target" ]]; then
    echo " · $name already downloaded"
    continue
  fi

  echo " · Fetching $name"
  curl -L --fail --output "$target" "$url"
done

echo "Groovebox sample library synchronized."
