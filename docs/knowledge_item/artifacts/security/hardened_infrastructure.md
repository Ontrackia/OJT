# Hardened Infrastructure & Security

OnTrackIA V2.0 employs a multi-layered security strategy referred to as the "Bunker" protocol.

## 🛡️ Application Hardening

### Global Rate Limiting

- **Technology**: Redis-backed middleware.
- **Rules**: Enforces request limits per Minute/Hour/Day based on client IP.
- **Action**: Returns 429 status code with `Retry-After` headers to prevent brute-force attacks on sensitive endpoints (`/login`, `/register`).

### RBAC Matrix Middleware

- **Source**: Dynamic loading from `/docs/rbac_matrix.csv`.
- **Enforcement**: Middleware validates and caches user permissions. Prevents trainees from accessing supervisor-only functions (e.g., signing OJT entries) even if endpoint URLs are known.

### JWT Lifecycle & Timing

- **Security**: Timing-safe password verification and strict JWT verification.
- **Fail-Closed**: Any signature alteration or expiry immediately redirects to `/login` and logs an audit event.

## 🌐 Network & Environment

### Environment-Driven CORS

- **Strategy**: Forbidden use of wildcard `*` origins.
- **Logic**: `ALLOWED_ORIGINS` is strictly defined in environment variables. Defaults to `localhost` for dev and official domains for production.

### Production Readiness

- **Fail-Safe Checks**: Startup sequence verifies critical credentials. If `JWT_SECRET_KEY` is not present, the system Refuses to boot.
- **Trusted Proxies**: Configured for accurate IP resolution when running behind Nginx or Load Balancers.

## 🏛️ Deployment (Hetzner)

- **Host**: CX33 High-performance nodes (`46.225.79.232`).
- **Transfer**: Secure SCP/SSH delivery of the validated repository package.
