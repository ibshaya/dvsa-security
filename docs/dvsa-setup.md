# Deploying DVSA on AWS

Follow these steps to get a working DVSA instance before running any exploits.

---

## 1. Deploy from the AWS Serverless Application Repository

1. Log in to the [AWS Console](https://console.aws.amazon.com) and switch to **us-east-1**.
2. Go to **Serverless Application Repository** → **Available applications** → search for `DVSA`.
3. Click the DVSA application → **Deploy**.
4. Accept the default settings and click **Deploy**.
5. Wait for the CloudFormation stack to finish (~5 minutes). Note the **Outputs** tab — it contains your API Gateway URL and the S3 frontend URL.

---

## 2. Find Your API Endpoint and Frontend URL

After deployment, go to **CloudFormation → Stacks → serverlessrepo-OWASP-DVSA → Outputs**. You will see:

| Key | Example Value |
|-----|--------------|
| `ServiceEndpoint` | `https://abc123.execute-api.us-east-1.amazonaws.com/Stage` |
| `WebsiteURL` | `http://dvsa-website-<account>-us-east-1.s3-website.us-east-1.amazonaws.com` |

---

## 3. Register Test Users

Open the WebsiteURL in your browser and register **two separate accounts** (you will need both for Lessons 2 and 3):

- **User A / User B** — regular non-admin user (attacker)
- **User C** — regular non-admin user (victim)

Use an incognito window for the second account.

---

## 4. Capture a JWT Token

After logging in, open **DevTools → Network → Fetch/XHR**, click on any order request, and copy the `authorization` header value. This is your Cognito JWT.

You can also use the helper script:

```bash
# From the repo root
bash scripts/get_token.sh
```

---

## 5. Configure Your Terminal

```bash
export API="https://<your-api-id>.execute-api.us-east-1.amazonaws.com/Stage"
export TOKEN="<your-jwt>"
```

Add these to your `~/.bashrc` or set them at the start of each terminal session.

---

## 6. Verify the Deployment

```bash
curl -s "$API/order" \
  -H "content-type: application/json" \
  -H "authorization: $TOKEN" \
  --data-raw '{"action":"orders"}' | jq
```

Expected response:
```json
{
  "status": "ok",
  "orders": []
}
```

---

## AWS CLI Configuration

All exploits that use the AWS CLI require credentials with at least `s3:PutObject` on public buckets (Lesson 4). Run:

```bash
aws configure
```

And enter your **Access Key ID**, **Secret Access Key**, and set region to `us-east-1`.

---

## CloudWatch Log Access

Several lessons require checking CloudWatch logs. In the AWS Console:

1. Go to **CloudWatch → Log groups**.
2. Search for `/aws/lambda/DVSA-<function-name>`.
3. Open the most recent log stream.

---

## Cleanup

To avoid ongoing AWS charges, delete the CloudFormation stack when you are done:

```bash
aws cloudformation delete-stack --stack-name serverlessrepo-OWASP-DVSA --region us-east-1
```
