#!/usr/bin/env bash
set -euo pipefail

# publish-to-appimagehub.sh
# Create an issue in the AppImage/appimage.github.io repo requesting a listing for this AppImage.
# Usage: publish-to-appimagehub.sh <release_tag> <release_url>

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <release_tag> <release_url>" >&2
  exit 2
fi

RELEASE_TAG="$1"
RELEASE_URL="$2"

# Accept token from env APPIMAGEHUB_PAT or GITHUB_TOKEN
TOKEN="${APPIMAGEHUB_PAT:-${GITHUB_TOKEN:-}}"
if [ -z "$TOKEN" ]; then
  echo "No APPIMAGEHUB_PAT or GITHUB_TOKEN found in env; skipping AppImageHub request." >&2
  exit 0
fi

TITLE="Add JukeBox AppImage ($RELEASE_TAG)"

BODY="Hello AppImageHub maintainers!

Please consider adding JukeBox to AppImageHub. A new release has just been published:

Release: ${RELEASE_TAG}
Download / assets: ${RELEASE_URL}

Notes:
- AppImage contains embedded Python virtualenv and dependencies.
- Provide both 'full' and 'slim' AppImages in the release assets for users.

If you'd like additional meta-data (icons, categories) I can provide a PR or more details.

Thanks!"

API_URL="https://api.github.com/repos/AppImage/appimage.github.io/issues"

echo "Creating issue in AppImage/appimage.github.io to request adding release ${RELEASE_TAG}"

payload=$(jq -n --arg t "$TITLE" --arg b "$BODY" '{title: $t, body: $b, labels: ["appimages"]}')

resp=$(curl -s -X POST -H "Authorization: token ${TOKEN}" -H "Accept: application/vnd.github+json" -d "$payload" "$API_URL")

issue_url=$(echo "$resp" | jq -r .html_url // empty)
if [ -n "$issue_url" ]; then
  echo "Created issue: $issue_url"
  exit 0
else
  echo "Failed to create issue. Response:" >&2
  echo "$resp" >&2
  exit 1
fi
