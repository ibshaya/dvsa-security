"""
Lesson 10 — Unhandled Exceptions Fix
Adds a central try/except wrapper and input validation to all order handler Lambdas.
This fix also eliminates the Lesson 5 root cause (isAdmin from body) simultaneously.

Before (vulnerable):
  def lambda_handler(event, context):
      body = json.loads(event.get("body", "{}"))
      is_admin = json.loads(event.get("isAdmin", "false").lower())  # line 32 crash
      ...
  # No try/except → AttributeError propagates to AWS runtime → full traceback returned to client

After (fixed):
  - All exceptions caught at the handler boundary
  - Full traceback logged to CloudWatch (operators can debug)
  - Only generic messages returned to the client (no paths, no source code)
  - Input validation rejects unexpected field types before business logic
"""
import json
import logging

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


def _validate(body):
    """Strict input validation. Raises ValueError on bad input."""
    if not isinstance(body, dict):
        raise ValueError("body must be a JSON object")
    action = body.get("action")
    if not action or not isinstance(action, str):
        raise ValueError("action must be a non-empty string")
    # Drop any field the server did not explicitly invite
    return {k: v for k, v in body.items() if k in ALLOWED_FIELDS}


def lambda_handler(event, context):
    try:
        raw  = event.get("body", "{}")
        body = _validate(json.loads(raw) if isinstance(raw, str) else raw)

        # Privilege comes from the verified JWT (see Lesson 5 fix).
        # isAdmin is never read from the request body — it doesn't survive _validate().
        is_admin = _is_admin_from_jwt(event)
        user_sub = _sub_from_jwt(event)
        order_id = body.get("order-id")

        if is_admin:
            return _ok({"order": get_any_order(order_id)})
        return _ok({"order": get_own_order(order_id, user_sub)})

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        # Bad client input — controlled 400 with a generic message.
        # Log the reason at WARNING level (goes to CloudWatch, not to the client).
        log.warning("bad request: %s", e)
        return _err(400, "bad request")

    except Exception:
        # Anything unexpected: log the full traceback to CloudWatch for operators,
        # but NEVER return diagnostic details to the client.
        log.exception("unhandled exception in lambda_handler")
        return _err(500, "internal error")


# ── Placeholder helpers — replace with real implementations ───────────────

def _is_admin_from_jwt(event):
    """Derive is_admin from verified Cognito JWT claims (not from the body)."""
    # Implementation: verify the JWT against Cognito JWKS, then check cognito:groups
    # See Lesson 5 fix (fix/get_order_fixed.py) for the full JWT verification code.
    return False  # default non-admin; replace with actual JWT verification

def _sub_from_jwt(event):
    raise NotImplementedError

def get_own_order(order_id, user_sub):
    raise NotImplementedError

def get_any_order(order_id):
    raise NotImplementedError
