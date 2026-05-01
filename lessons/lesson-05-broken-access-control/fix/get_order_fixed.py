"""
Lesson 5 — Broken Access Control Fix
Fixed get_order.py Lambda handler.

Changes:
  - Privilege derived from verified Cognito JWT (not from the request body).
  - isAdmin and status fields stripped from body before dispatch.
  - try/except wrapper returns generic errors (also fixes Lesson 10).
"""
import json
import os
import logging
import urllib.request
from functools import lru_cache

import jwt  # pip install PyJWT[cryptography]

log = logging.getLogger()
log.setLevel(logging.INFO)

ALLOWED_FIELDS = {"action", "order-id", "cart-id", "items"}


def _err(status, msg):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "err", "msg": msg}),
    }


def _ok(payload):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok", **payload}),
    }


@lru_cache(maxsize=1)
def _jwks():
    region  = os.environ["AWS_REGION"]
    pool    = os.environ["userpoolid"]
    url     = f"https://cognito-idp.{region}.amazonaws.com/{pool}/.well-known/jwks.json"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def _verified_claims(event):
    """Verify JWT and return claims. Raises PermissionError on failure."""
    auth = event.get("headers", {}).get("Authorization", "").replace("Bearer ", "").strip()
    if not auth:
        raise PermissionError("missing token")
    try:
        kid       = jwt.get_unverified_header(auth)["kid"]
        key_data  = next(k for k in _jwks()["keys"] if k["kid"] == kid)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        return jwt.decode(auth, public_key, algorithms=["RS256"], options={"verify_aud": False})
    except Exception as e:
        raise PermissionError(f"invalid token: {e}") from e


def lambda_handler(event, context):
    try:
        claims   = _verified_claims(event)
        # Privilege comes from the verified JWT — NOT from the body.
        is_admin = "admins" in claims.get("cognito:groups", [])
        user_sub = claims["sub"]

        raw  = event.get("body", "{}")
        body = json.loads(raw) if isinstance(raw, str) else raw

        # Strip any client-supplied privilege or status fields.
        body.pop("isAdmin", None)
        body.pop("status",  None)
        # Keep only expected fields.
        body = {k: v for k, v in body.items() if k in ALLOWED_FIELDS}

        order_id = body.get("order-id")

        if is_admin:
            return _ok({"order": get_any_order(order_id)})
        return _ok({"order": get_own_order(order_id, user_sub)})

    except PermissionError as e:
        log.warning("auth failure: %s", e)
        return _err(401, "unauthorized")

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        log.warning("bad request: %s", e)
        return _err(400, "bad request")

    except Exception:
        # Log full traceback to CloudWatch — NEVER return it to the client.
        log.exception("unhandled exception in lambda_handler")
        return _err(500, "internal error")


# ── Placeholder data-access functions (implement against your DynamoDB table) ──

def get_own_order(order_id, user_sub):
    """Return the order only if it belongs to user_sub."""
    raise NotImplementedError

def get_any_order(order_id):
    """Admin path: return any order regardless of owner."""
    raise NotImplementedError
