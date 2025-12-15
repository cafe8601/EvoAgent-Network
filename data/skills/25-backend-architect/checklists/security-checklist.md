# Security Checklist

OWASP Top 10 (2025) compliance and security best practices checklist.

## Authentication

### Password Security
- [ ] Argon2id for password hashing (not bcrypt)
- [ ] Minimum password length: 12 characters
- [ ] Password complexity requirements enforced
- [ ] Password breach database check (haveibeenpwned)
- [ ] Account lockout after failed attempts
- [ ] Rate limiting on login endpoints

### Token Security
- [ ] JWT signed with RS256 (asymmetric)
- [ ] Access tokens short-lived (15 minutes)
- [ ] Refresh tokens in HTTP-only cookies
- [ ] Refresh token rotation enabled
- [ ] Token revocation mechanism
- [ ] No sensitive data in JWT payload

### OAuth/OIDC
- [ ] OAuth 2.1 compliance
- [ ] PKCE for all OAuth flows
- [ ] State parameter validated
- [ ] Nonce for replay prevention
- [ ] Token binding when possible

### MFA
- [ ] MFA available for sensitive operations
- [ ] TOTP implementation correct
- [ ] Backup codes generated
- [ ] Recovery flow secured

---

## Authorization

### Access Control
- [ ] Deny by default principle
- [ ] RBAC or ABAC implemented
- [ ] Role hierarchy properly designed
- [ ] Resource-level authorization
- [ ] Function-level access control
- [ ] Least privilege principle

### Session Management
- [ ] Session IDs cryptographically random
- [ ] Session timeout configured
- [ ] Session invalidation on logout
- [ ] Session fixation prevention
- [ ] Concurrent session limits

---

## Input Validation

### Data Validation
- [ ] All inputs validated server-side
- [ ] Validation library used (Zod, Joi)
- [ ] Whitelist validation preferred
- [ ] Input length limits enforced
- [ ] Content-type validation
- [ ] File upload validation

### Injection Prevention
- [ ] Parameterized queries only
- [ ] ORM used for database operations
- [ ] No string concatenation in queries
- [ ] NoSQL injection prevention
- [ ] Command injection prevention
- [ ] LDAP injection prevention

### XSS Prevention
- [ ] Output encoding enabled
- [ ] Content Security Policy headers
- [ ] HTML sanitization for user content
- [ ] JavaScript context escaping
- [ ] URL validation for redirects

---

## Cryptography

### Encryption at Rest
- [ ] Sensitive data encrypted in database
- [ ] Encryption keys properly managed
- [ ] Key rotation procedures
- [ ] AES-256-GCM for symmetric encryption
- [ ] HSM for key storage (production)

### Encryption in Transit
- [ ] TLS 1.3 enforced
- [ ] Strong cipher suites only
- [ ] HSTS enabled with preload
- [ ] Certificate pinning (mobile)
- [ ] Perfect forward secrecy

### Secrets Management
- [ ] No secrets in code
- [ ] Environment variables for config
- [ ] Secrets manager (Vault, AWS Secrets)
- [ ] Secrets rotation automated
- [ ] No secrets in logs

---

## Security Headers

### HTTP Headers
- [ ] Content-Security-Policy
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Strict-Transport-Security
- [ ] Referrer-Policy
- [ ] Permissions-Policy

### CORS
- [ ] Allowed origins explicitly listed
- [ ] No wildcard (*) in production
- [ ] Credentials properly handled
- [ ] Preflight caching configured

---

## API Security

### Rate Limiting
- [ ] Rate limits per user/IP
- [ ] Rate limits per endpoint
- [ ] Sliding window algorithm
- [ ] Response includes limit headers
- [ ] Graceful degradation

### Request Validation
- [ ] Request size limits
- [ ] JSON parsing limits
- [ ] File upload size limits
- [ ] Request timeout configured
- [ ] Malformed request handling

---

## Logging & Monitoring

### Security Logging
- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Sensitive operations logged
- [ ] Log injection prevention
- [ ] No sensitive data in logs
- [ ] Log retention policy

### Monitoring
- [ ] Anomaly detection enabled
- [ ] Failed login monitoring
- [ ] Rate limit breach alerts
- [ ] Error rate monitoring
- [ ] Incident response plan

### Audit Trail
- [ ] Who/what/when recorded
- [ ] Immutable audit logs
- [ ] Tamper detection
- [ ] Compliance retention

---

## Infrastructure

### Network Security
- [ ] Firewall rules configured
- [ ] Network segmentation
- [ ] VPN for admin access
- [ ] DDoS protection
- [ ] WAF enabled

### Container Security
- [ ] Minimal base images
- [ ] Non-root containers
- [ ] Image scanning
- [ ] Secrets not in images
- [ ] Read-only filesystem

### Dependency Security
- [ ] Dependencies regularly updated
- [ ] Vulnerability scanning (npm audit, Snyk)
- [ ] Lock files committed
- [ ] License compliance check
- [ ] Supply chain security

---

## Data Protection

### PII Handling
- [ ] PII identified and classified
- [ ] Data minimization practiced
- [ ] Consent management
- [ ] Right to erasure supported
- [ ] Data portability implemented

### Backup Security
- [ ] Backups encrypted
- [ ] Backup access restricted
- [ ] Backup testing scheduled
- [ ] Offsite backup storage
- [ ] Recovery procedures documented

---

## OWASP Top 10 (2025) Quick Check

| # | Category | Status |
|---|----------|--------|
| 1 | Broken Access Control | [ ] Mitigated |
| 2 | Cryptographic Failures | [ ] Mitigated |
| 3 | Injection | [ ] Mitigated |
| 4 | Insecure Design | [ ] Mitigated |
| 5 | Security Misconfiguration | [ ] Mitigated |
| 6 | Vulnerable Components | [ ] Mitigated |
| 7 | Auth Failures | [ ] Mitigated |
| 8 | Data Integrity Failures | [ ] Mitigated |
| 9 | Logging Failures | [ ] Mitigated |
| 10 | SSRF | [ ] Mitigated |

---

## Security Review Sign-off

| Phase | Reviewer | Date | Status |
|-------|----------|------|--------|
| Design Review | | | [ ] |
| Code Review | | | [ ] |
| Penetration Test | | | [ ] |
| Security Audit | | | [ ] |
| Compliance Check | | | [ ] |
