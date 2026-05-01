#!/usr/bin/env bash
# Helper: decode and display the username/sub from any DVSA JWT.
# Usage: TOKEN="eyJ..." bash scripts/get_token.sh

set -euo pipefail

if [[ -z "${TOKEN:-}" ]]; then
  echo "Usage: TOKEN='<your-jwt>' bash $0"
  exit 1
fi

python3 - <<'PY'
import os, json, base64

def decode(token):
    payload = token.split('.')[1]
    payload += '=' * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload.encode()))

data = decode(os.environ["TOKEN"])
print("username :", data.get("username", data.get("cognito:username", "n/a")))
print("sub      :", data.get("sub"))
print("email    :", data.get("email", "n/a"))
print("groups   :", data.get("cognito:groups", []))
print("expires  :", data.get("exp"))
PY
