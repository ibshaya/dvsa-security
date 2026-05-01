/**
 * Lesson 2 — Broken Authentication Fix
 * Drop-in replacement for the decode-and-trust pattern in order-manager.js.
 *
 * Before (vulnerable):
 *   const decoded = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
 *   const username = decoded.username;   // trusted without signature check!
 *
 * After (safe):
 *   const claims = await verifyCognitoJwt(token, region, userPoolId);
 *   const username = claims.username;
 */

const https = require('https');
const jose  = require('node-jose');   // npm install node-jose

// Cache the JWKS in-memory across warm Lambda invocations.
let _jwksCache = null;

async function fetchJwks(region, userPoolId) {
    if (_jwksCache) return _jwksCache;
    const url = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}/.well-known/jwks.json`;
    return new Promise((resolve, reject) => {
        https.get(url, res => {
            let raw = '';
            res.on('data', chunk => raw += chunk);
            res.on('end', () => {
                try { _jwksCache = JSON.parse(raw); resolve(_jwksCache); }
                catch (e) { reject(e); }
            });
        }).on('error', reject);
    });
}

/**
 * Verify a Cognito JWT and return its claims.
 * Throws an Error if verification fails for any reason.
 *
 * @param {string} token     - Raw JWT string (without "Bearer " prefix)
 * @param {string} region    - AWS region, e.g. "us-east-1"
 * @param {string} userPoolId - Cognito User Pool ID, e.g. "us-east-1_abc123"
 * @returns {object}         - Verified JWT claims
 */
async function verifyCognitoJwt(token, region, userPoolId) {
    const jwks = await fetchJwks(region, userPoolId);
    const keystore = await jose.JWK.asKeyStore(jwks);

    let verified;
    try {
        verified = await jose.JWS.createVerify(keystore).verify(token);
    } catch (e) {
        throw new Error(`JWT signature verification failed: ${e.message}`);
    }

    const claims = JSON.parse(verified.payload.toString());
    const now = Math.floor(Date.now() / 1000);

    if (claims.exp < now) {
        throw new Error('JWT has expired');
    }

    const expectedIss = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}`;
    if (claims.iss !== expectedIss) {
        throw new Error(`JWT issuer mismatch: ${claims.iss}`);
    }

    if (claims.token_use !== 'access') {
        throw new Error(`Unexpected token_use: ${claims.token_use}`);
    }

    return claims;
}

module.exports = { verifyCognitoJwt };
