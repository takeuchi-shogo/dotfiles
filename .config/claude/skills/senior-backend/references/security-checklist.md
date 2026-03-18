# API Security Checklist (OWASP Top 10)

## Input Validation
- [ ] All user input validated and sanitized
- [ ] Parameterized queries for database operations
- [ ] File upload restrictions (type, size, content)

## Authentication & Authorization
- [ ] Strong password hashing (bcrypt/argon2)
- [ ] Rate limiting on auth endpoints
- [ ] JWT expiration and refresh token rotation
- [ ] Role-based access control (RBAC)

## Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS for all data in transit
- [ ] No secrets in code or logs
- [ ] PII handling compliant

## API Security
- [ ] CORS properly configured
- [ ] Rate limiting on all endpoints
- [ ] Request size limits
- [ ] API versioning strategy

## Logging & Monitoring
- [ ] Security events logged (auth failures, access denials)
- [ ] No sensitive data in logs
- [ ] Alerting on anomalous patterns
