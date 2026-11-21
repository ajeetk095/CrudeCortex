# Security Policy — CrudeCortex

No application can honestly be guaranteed hack-proof. The objective is to
minimise risk, test implemented controls and document residual weaknesses.

## Implemented controls

| Control | Implementation |
|---|---|
| Input protection | Widget-constrained parameters, strict types, bounded date ranges, pandas-only (no SQL string building), unexpected fields ignored |
| Secret management | Env vars / `st.secrets` only; `.env.example` documents all keys; no credentials in repo or client bundle |
| File protection | Documents served from whitelisted `documents/` only; no path traversal; no user uploads; no code execution from input; no pickle deserialisation |
| Notebook protection | Bundled notebook is a static pre-executed export — viewing it never executes code |
| Network | HTTPS enforced by host (Streamlit Cloud); XSRF protection on; telemetry off |
| Errors & logging | Safe generic error messages; no stack traces or secrets surfaced |
| Dependency hygiene | `pip-audit`, `bandit -r .`, `ruff check .` before each release; compatible pins |
| Container (optional) | Non-root user, single exposed port 8501 |

## Threat model (summary)

| Threat | Vector | Mitigation | Status |
|---|---|---|---|
| Credential leak | committed keys | env/secrets only + `.gitignore` | ✅ tested |
| Path traversal | document viewer | whitelist + filename normalisation | ✅ tested |
| Injection | user input | no SQL/shell/eval paths exist | ✅ tested |
| Malicious notebook | embedded JS/code | static export, no execution | ✅ by design |
| Provider outage | data feeds | last-good-value fallback, no fabrication | ✅ by design |
| Scraping / abuse | public app | public research data only, no auth surface | ⚠️ residual |
| Rate abuse | request floods | host-level (Streamlit Cloud) | ⚠️ residual |

## Checklist

- [x] No hardcoded credentials
- [x] `.env.example` complete; `.env` git-ignored
- [x] Whitelisted directory for document serving
- [x] No `eval` / `exec` / `pickle.loads` on untrusted data
- [x] Safe error handling (generic messages)
- [x] XSRF on, telemetry off
- [x] Pinned-compatible dependencies
- [x] Tests pass (`tests/test_reproduction.py`, `tests/test_security.py`)

## Reporting

Private disclosure via the repository's Security tab or the developer email.
