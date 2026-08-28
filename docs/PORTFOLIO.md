# Portfolio Notes

## One-line Description

A full-stack procurement intelligence platform that compares supplier quotes, quantifies savings, scores supplier options, and explains deterministic recommendations through an authenticated React dashboard.

## Short Portfolio Description

Supplier Price Intelligence helps procurement teams organize supplier, product, and quotation data and turn active quotes into currency-aware purchasing insights. A layered FastAPI backend performs deterministic analysis and supplier scoring, while a React dashboard presents the results and an optional AI provider explains recommendations without controlling them.

## Technical Description

The project combines a React/TypeScript/Vite single-page application with a FastAPI, Pydantic, SQLAlchemy, and Alembic backend. It follows a Repository -> Service -> API architecture, secures protected endpoints with bcrypt-hashed credentials and expiring JWTs, and uses a provider abstraction with deterministic fallback for AI explanations. A 92-test pytest suite covers CRUD behavior, validation, security boundaries, currency separation, analysis, scoring, and recommendation safety.

## Key Engineering Achievements

- Designed layered persistence, business-service, schema, and HTTP boundaries.
- Implemented quote comparison and savings analysis independently per currency.
- Built an explainable weighted supplier-scoring model with documented neutral defaults.
- Kept AI downstream of deterministic decision logic and added a provider-failure fallback.
- Added authentication tests for hashed storage, invalid/expired tokens, inactive users, and administrator authorization.
- Built a centralized frontend API client with bearer authentication, typed responses, network errors, and automatic session cleanup on 401.
- Added database migrations, environment-based configuration, reproducible dependency locks, and provider-neutral deployment documentation.

## Tech Stack

Python, FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite, JWT, bcrypt, pytest, React, TypeScript, Vite, React Router, CSS, Fetch API.

## Business Value

The application makes quote selection auditable: buyers can see the price spread and potential savings, understand how supplier performance affects the decision, and review a concise explanation without allowing a language model to invent commercial facts or compare incompatible currencies.

## Suggested CV Bullet Points

- Built a full-stack procurement intelligence application with React/TypeScript and a layered FastAPI/SQLAlchemy backend.
- Implemented currency-isolated quote comparison, savings analysis, and explainable weighted supplier ranking across active supplier quotes.
- Secured protected APIs with bcrypt, expiring JWTs, inactive-user checks, and administrator-only destructive operations; verified behavior in a 92-test pytest suite.
- Designed an AI-provider abstraction that explains structured deterministic results, prevents model overrides, and degrades safely to a deterministic fallback.

## Suggested LinkedIn Project Description

Built Supplier Price Intelligence, a full-stack procurement decision-support project using React, TypeScript, FastAPI, SQLAlchemy, Alembic, and pytest. The system manages supplier quotations, analyzes price spreads and savings independently by currency, and ranks suppliers using transparent price and performance weights. AI is deliberately constrained to explaining structured deterministic results, with authentication, authorization, provider fallback, and automated regression coverage included.

## Interview Talking Points

- Why Repository -> Service -> API separation keeps procurement rules testable and routes small.
- Why currency partitioning is a correctness boundary, not merely a display choice.
- How the 50/20/15/15 scoring weights and neutral missing-value defaults make decisions explainable.
- How AI safety is achieved by calculating recommendations first and accepting only explanation text afterward.
- Why JWT expiry, generic login errors, inactive-user checks, and admin dependencies are tested separately.
- Tradeoffs of sessionStorage versus cookies and what would change for a public, higher-risk deployment.
- Why SQLite is appropriate for a local portfolio demo but durable production hosting should use a managed relational database and backups.
- How Alembic migrations, pinned Python dependencies, package-lock.json, and clean builds improve reproducibility.
