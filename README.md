# Supplier Price Intelligence

A full-stack procurement application for managing supplier quotations and turning them into currency-aware, explainable purchasing recommendations.

## Overview

Supplier Price Intelligence helps procurement teams manage suppliers and products, record supplier quotes, compare pricing, identify savings opportunities, score supplier options, and review AI-assisted procurement explanations from an authenticated dashboard.

The procurement calculations are deterministic and authoritative. The AI layer receives structured results and explains them; it does not invent prices, calculate rankings, or override the selected supplier.

## Features

- Supplier, product, and supplier-quote CRUD workflows
- Independent quote comparison and recommendations per currency
- Lowest, highest, average, spread, and potential-savings analysis
- Explainable supplier scoring using price and performance inputs
- Provider-abstracted AI explanations with deterministic fallback
- JWT authentication, password hashing, protected routes, and admin-only deletion
- Responsive React dashboard for operational data and procurement intelligence
- OpenAPI/Swagger documentation, Alembic migrations, validation, and automated tests

## Architecture

~~~text
React + TypeScript frontend
          |
          v
      FastAPI API
          |
          v
      Service layer ------> AI provider abstraction
          |                    (explanation only)
          v
    Repository layer
          |
          v
 SQLAlchemy + database
~~~

The backend preserves a Repository -> Service -> API separation: repositories handle persistence, services own business rules, and routes handle HTTP concerns and response schemas. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the request flows.

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, Uvicorn |
| Frontend | React, TypeScript, Vite, React Router, Fetch API |
| Database | SQLite for local/demo use; PostgreSQL for production through `DATABASE_URL` |
| Testing | pytest, FastAPI/Starlette TestClient, TypeScript compiler, Vite build |
| Security | bcrypt password hashing, signed expiring JWTs, route authorization, configurable CORS |

## Project Structure

~~~text
app/
  api/                 FastAPI dependencies and versioned routes
  core/                Configuration and security primitives
  database/            SQLAlchemy engine and sessions
  models/              ORM models
  repositories/        Persistence operations
  schemas/             Pydantic request/response models
  services/            Business and procurement intelligence logic
alembic/                Database migrations
frontend/src/           React application, API client, auth, and pages
scripts/                Local development utilities
tests/                  Backend regression and security tests
docs/                   Architecture, deployment, demo, and portfolio guides
~~~

## Procurement Intelligence

- **Price comparison:** ranks active quotes from lowest unit price within each currency and identifies the cheapest quote.
- **Procurement analysis:** calculates price range, average, difference, percentage difference, and potential savings.
- **Supplier scoring:** balances price competitiveness with reliability, delivery, and supplier activity.
- **AI recommendation:** explains the deterministic highest-scoring supplier using only structured procurement facts.

USD, EUR, LBP, and other currencies are always evaluated independently. The application performs no currency conversion.

## Supplier Scoring

The score implemented in SupplierScoringService is:

~~~text
final score = price score       * 50%
            + reliability score * 20%
            + delivery score    * 15%
            + activity score    * 15%
~~~

Within one currency, the lowest active quote receives a price score of 100; other price scores are (lowest price / supplier price) * 100, clamped to 0-100. A missing reliability or delivery value receives a neutral score of 50. Active suppliers receive an activity score of 100, inactive suppliers receive 0, and the final score is rounded to two decimal places.

## AI Safety and Deterministic Recommendations

- AI does not calculate prices, savings, scores, or rankings.
- AI cannot replace or override the deterministic recommendation.
- The provider receives only structured procurement facts, not application secrets.
- The system prompt prohibits invented facts and currency conversion.
- A deterministic explanation is returned if the configured provider is unavailable or fails.

The default mock provider makes the project fully demonstrable without an external API key. The optional openai provider uses the configured model and key.

## Authentication and Authorization

Passwords are validated and stored only as bcrypt hashes. Successful login returns an expiring JWT signed with the environment-provided secret. Protected API groups require a valid bearer token; inactive users and invalid or expired tokens are rejected. Delete operations require an administrator. The frontend keeps the token in sessionStorage and clears it on logout or any 401 response.

## Installation

### Backend on Windows

~~~powershell
git clone <repository-url>
cd ai-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
~~~

Edit .env, replace the JWT placeholder with a private random value, then initialize and run the API:

~~~powershell
alembic upgrade head
uvicorn app.main:app --reload
~~~

The API is available at http://127.0.0.1:8000.

### Frontend on Windows

~~~powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
~~~

Open http://localhost:5173/login.

## Environment Variables

Backend variables are loaded from the process environment or an ignored root .env:

| Variable | Purpose |
| --- | --- |
| DATABASE_URL | SQLAlchemy database connection URL |
| JWT_SECRET_KEY | Private key used to sign and verify access tokens |
| JWT_ALGORITHM | JWT signing algorithm; the example uses HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access-token lifetime |
| CORS_ALLOWED_ORIGINS | Comma-separated trusted frontend origins |
| AI_PROVIDER | Explanation provider: mock, openai, or an unavailable provider fallback |
| AI_API_KEY | Provider credential; required only when the selected provider needs it |
| AI_MODEL | Provider model identifier |

The frontend requires VITE_API_BASE_URL, set to the public backend origin at build time. The checked-in .env.example files contain development-safe placeholders only; real .env files are ignored.

## Creating a Development User

No user is created automatically. After migrations, run the helper and enter the password at its hidden prompt:

~~~powershell
python scripts/create_dev_user.py developer@example.com
~~~

The helper uses the same validation, hashing, and duplicate-email handling as the authentication service. A user can also be created through POST /api/v1/auth/register.

## Optional Demo Dataset

The manual demo seeder adds five fictional suppliers, eight products, and 33 competing quotes to the configured development database:

~~~powershell
alembic upgrade head
python scripts/seed_demo_data.py
~~~

It creates only missing demo records, so repeated runs are safe and existing records are not overwritten or deleted. The data includes price spreads, distinct supplier performance scores, an inactive quote, and USD/EUR examples that remain independently ranked. It does not create users, passwords, tokens, or API credentials.

Create the demo user separately with the hidden-password workflow above. A normal user is sufficient for the read-only dashboard demo. Delete endpoints require an administrator, and the application intentionally provides no public admin-promotion endpoint or default administrator credential.

## Testing

~~~powershell
pytest -v
pytest -W error
cd frontend
npm run build
npm audit
~~~

package-lock.json is committed so frontend installations can be reproduced with npm install or npm ci.

## API Documentation

With the backend running, interactive Swagger documentation is available at /docs. Major API groups are:

- Authentication: registration and login
- Suppliers
- Products
- Supplier Quotes
- Procurement Intelligence: price comparison, analysis, supplier ranking, and AI recommendation

GET /health is public and returns a minimal deployment health response.

## Deployment

The prepared production architecture uses Vercel for the Vite frontend, Render for the FastAPI service, and a compatible managed PostgreSQL database. Local development continues to use SQLite. Provider credentials, the JWT secret, database URL, CORS origins, and optional AI key stay in provider environment configuration and are never committed.

React Router's Vercel fallback is defined in `frontend/vercel.json`, while `render.yaml` defines the backend build, start, and health-check settings without creating paid resources. Detailed database migration, environment, security, and verification steps are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Live links can be added after deployment:

- Live demo: pending
- API: pending
- API documentation: pending

## Screenshots

The repository reserves docs/screenshots/ for reviewed application screenshots. The five strongest README images to capture are:

| Planned file | What it should show |
| --- | --- |
| docs/screenshots/dashboard.png | Live product, supplier, quote, and active-quote totals |
| docs/screenshots/quotes.png | Several suppliers competing for the same product |
| docs/screenshots/procurement-intelligence.png | Currency-aware comparison and savings analysis |
| docs/screenshots/supplier-ranking.png | Price, reliability, delivery, activity, and final scores |
| docs/screenshots/ai-recommendation.png | Deterministic recommendation with its AI/fallback explanation |

The files are intentionally not referenced as images until real captures exist, avoiding broken or fabricated screenshots. The complete capture checklist is in [docs/DEMO.md](docs/DEMO.md).

## Future Improvements

- PostgreSQL-backed production deployment and operational backups
- Historical quote and supplier-performance trends
- Auditable procurement decision history
- CSV import/export and richer reporting

## Author

Wadih Hani
