# Security and threat model

## Assets

Credentials and session cookies; uploaded business files; dataset schema and row data; workspace memberships; saved dashboards/reports; private exports; application secrets and database backups.

## Threats and controls

| Threat | Current control | Remaining work |
|---|---|---|
| Cross-workspace IDOR | Server-side membership check for dataset/dashboard/report operations | Expand adversarial permission tests to every endpoint and nested reference |
| Password disclosure | Django password hashing, minimum length and common-password validators | Email verification, password reset flow, MFA option |
| CSRF | Django CSRF middleware, session authentication, frontend CSRF header | Verify reverse-proxy origin/cookie behavior in production |
| Brute-force login | DRF anonymous throttle plus login-specific throttle | Shared-cache-backed throttling and edge/WAF limits; current in-memory defaults are not multi-worker safe |
| Malicious uploads | Size/extension checks, internal UUID storage names, no execution, parse errors sanitized | Malware scanning, content-signature checks for all formats, decompression-bomb limits, async sandboxed processing |
| CSV formula injection | Formula-leading string neutralization on CSV export | Add equivalent policy to all future export formats and validate spreadsheet interoperability |
| SQL injection | No user-built SQL; Django ORM and allowlisted Pandas filters | Add security regression suite and query resource isolation |
| XSS | React text rendering; no raw HTML rendering in UI | CSP and security-header review in deployed environment |
| Secret exposure | `.env.example` uses placeholders; production settings configurable | Secret manager integration and automated secret scanning |
| Resource exhaustion | Upload size, row/column and query result limits | Worker queue, CPU/memory/time quotas, request body limits at proxy |
| Sensitive logs | Errors return non-sensitive messages; no row payload logging | Correlation-ID middleware, structured redacted audit trail, operational alerting |

## Production checklist

- Set `DJANGO_DEBUG=0`, strong unique `DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS`.
- Serve only over HTTPS; use secure session and CSRF cookies; set HSTS at a correctly configured TLS termination layer.
- Replace development database credentials, use managed PostgreSQL with least privilege, and encrypt backups.
- Store uploads in private object storage with authorization-controlled signed downloads; do not expose `MEDIA_ROOT` publicly.
- Use a shared cache for throttles and background job locks; set worker/resource limits.
- Configure email delivery and test account recovery; seed demo credentials only in isolated development/demo deployments.
- Run dependency and container scans; rotate secrets; exercise restore procedures.

This is an engineering checklist, not a claim of formal OWASP certification or an independent security audit.
