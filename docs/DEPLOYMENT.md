# Deployment Guide

The selected deployment architecture is a Vercel static frontend, a Render FastAPI web service, and a managed PostgreSQL database. Nothing in this repository creates provider accounts or paid resources, and all production credentials remain in provider environment settings.

## Local

Local development continues to use SQLite. Copy the example environment files, replace the JWT placeholder, run migrations, and start both applications:

~~~powershell
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

cd frontend
Copy-Item .env.example .env
npm install
npm run dev
~~~

The local frontend calls `http://127.0.0.1:8000`, and the default database remains `sqlite:///./supplier_intelligence.db`.

## Production

The production request flow is:

~~~text
Vercel React application -> Render FastAPI service -> managed PostgreSQL
~~~

Use any compatible managed PostgreSQL provider, including Render Postgres, Neon, or Supabase. Do not deploy with SQLite: a web service's local filesystem may be ephemeral and is unsuitable for durable concurrent production data.

### 1. Create the database

1. Create a managed PostgreSQL database using the provider's free offering if one is suitable.
2. Copy its connection URL into Render's secret environment configuration as `DATABASE_URL`.
3. Do not place that URL in Git, `.env.example`, `render.yaml`, build logs, or frontend variables.

The application accepts provider URLs beginning with `postgresql://` or legacy `postgres://` and selects SQLAlchemy's Psycopg 3 driver automatically. An explicit URL is also supported:

~~~text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
~~~

### 2. Configure the backend on Render

Create a Blueprint from the repository's `render.yaml`, or enter the equivalent settings in the Render dashboard:

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start lifecycle | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/health` |

The checked-in Blueprint deliberately does not create a database or select a paid plan. Automatic deployment is disabled so configuration can be reviewed before the first release. To remain usable without Render's paid pre-deploy feature, it applies the idempotent Alembic migration immediately before Uvicorn starts.

Before the first application start, and before each release containing migrations, run:

~~~text
alembic upgrade head
~~~

Render's dedicated pre-deploy command is not available on every service plan. If a paid service is selected later, move `alembic upgrade head` to that dedicated phase and leave Uvicorn as the start command. Do not embed a database credential in either command.

### 3. Configure the frontend on Vercel

Import the same GitHub repository and use these project settings:

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Framework preset | Vite |
| Build command | `npm run build` |
| Output directory | `dist` |

Set `VITE_API_BASE_URL` to the deployed Render origin, such as `https://api.example.com`, without `/api/v1` and without embedding credentials. Vite reads this value at build time, so redeploy after changing it.

`frontend/vercel.json` rewrites direct requests to `index.html`, allowing React Router to resolve `/dashboard`, `/products`, `/suppliers`, `/quotes`, and `/intelligence` after refresh.

### 4. Connect the origins

After Vercel assigns the real frontend origin, set Render's `CORS_ALLOWED_ORIGINS` to that exact HTTPS origin. Multiple trusted origins may be supplied as a comma-separated list. Do not use a wildcard for this authenticated API.

## Backend Environment

Configure these values in Render, not in Git:

| Variable | Production guidance |
| --- | --- |
| `DATABASE_URL` | Secret managed PostgreSQL connection URL |
| `JWT_SECRET_KEY` | Long, random, deployment-specific secret |
| `JWT_ALGORITHM` | `HS256` unless intentionally changed and tested |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Appropriate token lifetime, such as `30` |
| `CORS_ALLOWED_ORIGINS` | Exact deployed frontend origin(s) |
| `AI_PROVIDER` | `mock` for keyless demo or `openai` when configured |
| `AI_MODEL` | Backend provider model identifier |
| `AI_API_KEY` | Backend-only secret; omit when using `mock` |

`AI_API_KEY` must never be configured in Vercel or exposed through a `VITE_` variable. If a configured AI provider is unavailable, the deterministic procurement recommendation and fallback explanation remain functional.

## Frontend Environment

Configure this build-time value in Vercel:

~~~text
VITE_API_BASE_URL=https://api.example.com
~~~

Replace the example with the real backend origin. The production build fails clearly when the value is missing.

## Database Migration

Alembic reads the same environment-driven `DATABASE_URL` as the application. The production migration command is:

~~~text
alembic upgrade head
~~~

Keep the migration history intact and apply migrations before starting the corresponding backend version. Configure tested database backups and a restore procedure with the selected PostgreSQL provider.

## Optional Demo Data

Demo data is never loaded automatically. After migrations, optionally run this manually in an authorized backend environment:

~~~text
python scripts/seed_demo_data.py
~~~

The script uses `DATABASE_URL`, creates only missing fictional demo records, and does not create credentials. Re-running it does not delete or overwrite existing application data.

## Authentication and Administration

No default administrator or production credential exists. `scripts/create_dev_user.py` intentionally creates regular development users only; do not treat it as an administrator-provisioning tool. Provisioning a production administrator requires a separate, audited operational decision rather than a public privilege-escalation endpoint.

`POST /api/v1/auth/register` is currently public. That is convenient for a portfolio demonstration, but unrestricted registration and the absence of rate limiting should be reviewed before exposing the application to untrusted production traffic. Do not publish sensitive business data in a public demo.

## Production Verification

After deployment, verify without exposing secrets:

1. `GET /health` returns only `{"status":"healthy"}`.
2. `/docs` loads according to the intended public documentation policy.
3. Registration/login works with a test user and invalid/expired tokens are rejected.
4. The dashboard and protected products, suppliers, quotes, and procurement intelligence views load.
5. Direct navigation to frontend routes returns the React application.
6. Currency groups remain independent in comparison, analysis, ranking, and recommendations.
7. AI explanations work with the selected provider and fall back deterministically when it is unavailable.
8. Logout clears the browser session.

Before each release, run `pytest -W error`, `npm run build`, `npm audit`, and a secret scan of tracked files.
