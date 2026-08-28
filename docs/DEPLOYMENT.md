# Deployment Checklist

This guide is provider-neutral. No hosting provider or production database has been selected, and following it does not create or deploy infrastructure.

## Recommended Topology

- **Frontend:** static hosting for the Vite dist/ output
- **Backend:** Python web service running FastAPI with Uvicorn
- **Database:** SQLite for local/demo use; a managed relational database for durable, concurrent production use

Before switching database engines, select the platform, add its SQLAlchemy driver to requirements.txt, and test all existing migrations against that engine.

## Backend

1. Install the supported Python version and dependencies:

   ~~~text
   python -m pip install -r requirements.txt
   ~~~

2. Configure these environment variables in the host's secret/configuration system:

   - DATABASE_URL
   - JWT_SECRET_KEY
   - JWT_ALGORITHM
   - JWT_ACCESS_TOKEN_EXPIRE_MINUTES
   - CORS_ALLOWED_ORIGINS
   - AI_PROVIDER
   - AI_MODEL
   - AI_API_KEY only when required by the selected provider

3. Apply schema migrations to the production database before starting the new application version:

   ~~~text
   alembic upgrade head
   ~~~

4. Start the API on the host-provided port. A POSIX-style command is:

   ~~~sh
   uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
   ~~~

   For local POSIX use, set PORT to 8000 if no platform supplies it. In PowerShell, where PORT is supplied:

   ~~~powershell
   uvicorn app.main:app --host 0.0.0.0 --port $env:PORT
   ~~~

5. Configure the health check as GET /health. It requires no authentication and returns no internal configuration.

## Frontend

1. Install exactly from the committed lockfile:

   ~~~text
   npm ci
   ~~~

2. Set VITE_API_BASE_URL to the externally reachable backend origin, without an API path suffix.
3. Run npm run build and publish the generated frontend/dist/ directory.
4. Configure the static host to return index.html for unknown application routes. This SPA fallback is required when refreshing /login, /products, /suppliers, /quotes, or /intelligence.
5. Add the exact deployed frontend origin to backend CORS_ALLOWED_ORIGINS. Use a comma-separated list for multiple trusted origins; do not use a wildcard with credentialed requests.

## Security and Operations

- Generate a long, random, deployment-specific JWT_SECRET_KEY; never reuse the example placeholder.
- Store secrets in the deployment provider's secret manager or environment configuration, never in Git.
- Terminate public traffic with HTTPS and expose only the necessary service ports.
- Restrict CORS to exact trusted frontend origins.
- Keep access-token lifetime appropriate for the environment.
- Use a persistent production database and configure tested backups and restore procedures.
- Review logs without recording passwords, bearer tokens, or provider credentials.
- Run pytest -W error, npm run build, and npm audit before each release.

## Release Verification

After deployment, verify /health, /docs according to the intended documentation policy, login, protected collection endpoints, procurement intelligence for a known product, expired-token rejection, and logout. Confirm that direct navigation to each frontend route receives the SPA entry point.
