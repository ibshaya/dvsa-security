# ICS-344 DVSA Security Lab

**Course:** ICS-344 — Information Security  
**Term:** 252 (2026)  
**University:** King Fahd University of Petroleum and Minerals (KFUPM)  
**Team:** Ibrahim Alshayea · Rakan Alsaeed · Khalid Aljohani

---

## What Is This?

This repository documents the discovery, exploitation, and remediation of **10 security vulnerabilities** in [DVSA (Damn Vulnerable Serverless Application)](https://github.com/OWASP/DVSA) — an intentionally vulnerable AWS serverless app built by OWASP for security education.

Every lesson follows the same structure:
1. Goal and vulnerability summary
2. Root cause analysis
3. Reproduction steps (with actual commands)
4. Evidence and proof
5. Fix applied
6. Verification after fix

---

## Lessons Overview

| # | Vulnerability | AWS Service(s) |
|---|--------------|---------------|
| [1](lessons/lesson-01-event-injection/) | Event Injection (Insecure Deserialization) | Lambda |
| [2](lessons/lesson-02-broken-authentication/) | Broken Authentication (JWT not verified) | Lambda, Cognito |
| [3](lessons/lesson-03-sensitive-info-disclosure/) | Sensitive Information Disclosure | Lambda, S3 |
| [4](lessons/lesson-04-insecure-cloud-config/) | Insecure Cloud Configuration | S3, Lambda |
| [5](lessons/lesson-05-broken-access-control/) | Broken Access Control (client-supplied privilege) | Lambda, DynamoDB |
| [6](lessons/lesson-06-denial-of-service/) | Denial of Service (no rate limiting) | API Gateway, Lambda |
| [7](lessons/lesson-07-over-privileged-function/) | Over-Privileged Function (IAM) | Lambda, IAM, S3, DynamoDB |
| [8](lessons/lesson-08-logic-vulnerability/) | Logic Vulnerability (race condition) | Lambda, DynamoDB |
| [9](lessons/lesson-09-vulnerable-dependencies/) | Vulnerable Dependencies (node-serialize) | Lambda |
| [10](lessons/lesson-10-unhandled-exceptions/) | Unhandled Exceptions (stack trace leak) | Lambda, API Gateway |

## Prerequisites

- An AWS account with sufficient permissions to deploy serverless applications
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured (`aws configure`)
- A deployed DVSA instance (see [docs/dvsa-setup.md](docs/dvsa-setup.md))
- WSL2 (Ubuntu 24.04) or a Linux terminal
- `curl`, `python3`, `jq` installed

---

## Quick Start

```bash
# 1. Deploy DVSA (see docs/dvsa-setup.md)

# 2. Set your API endpoint and a valid JWT in your terminal
export API="https://<your-api-id>.execute-api.us-east-1.amazonaws.com/Stage"
export TOKEN="<your-cognito-jwt>"

# 3. Navigate to any lesson folder and follow the README
cd lessons/lesson-01-event-injection
cat README.md
```

---

## Repository Structure

```
dvsa-security-lab/
├── README.md                        ← You are here
├── docs/
│   └── dvsa-setup.md                ← How to deploy DVSA on AWS
├── scripts/
│   └── get_token.sh                 ← Helper: capture a JWT from DVSA
└── lessons/
    ├── lesson-01-event-injection/
    │   ├── README.md                ← Detailed write-up
    │   ├── exploit/                 ← Exploit scripts
    │   ├── fix/                     ← Patched code / diffs
    │   └── screenshots/             ← Place your evidence screenshots here
    ├── lesson-02-broken-authentication/
    │   └── ...
    └── ... (lessons 03 – 10 follow the same pattern)
```

---

## Security Note

All exploits in this repository target an intentionally vulnerable application deployed in a **private AWS account for educational purposes only**. Do not run these scripts against any system you do not own or have explicit permission to test.

---

## Report

The full written report is available as `ICS344_Report.pdf` in docs.
