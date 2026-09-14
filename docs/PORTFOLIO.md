# Portfolio Notes

## One-line Description

A full-stack procurement intelligence platform that compares supplier quotes, quantifies savings, scores supplier options, and explains deterministic recommendations through an authenticated React dashboard.

## Short Portfolio Description

Supplier Price Intelligence helps procurement teams organize supplier, product, and quotation data and turn active quotes into currency-aware purchasing insights. A layered FastAPI backend performs deterministic analysis and supplier scoring, while a React dashboard presents the results and an optional AI provider explains recommendations without controlling them.

## Technical Description

The project combines a React/TypeScript/Vite single-page application with a FastAPI, Pydantic, SQLAlchemy, and Alembic backend. It follows a Repository -> Service -> API architecture, secures protected endpoints with bcrypt-hashed credentials and expiring JWTs, and uses a provider abstraction with deterministic fallback for AI explanations. Its 96 passing pytest tests run with warnings treated as errors and cover CRUD behavior, validation, security boundaries, currency separation, analysis, scoring, and recommendation safety. The production system uses Neon PostgreSQL, a Render backend, and a Vercel frontend.

## Key Engineering Achievements

- Designed layered persistence, business-service, schema, and HTTP boundaries.
- Implemented quote comparison and savings analysis independently per currency.
- Built an explainable weighted supplier-scoring model with documented neutral defaults.
- Kept AI downstream of deterministic decision logic and added a provider-failure fallback.
- Added authentication tests for hashed storage, invalid/expired tokens, inactive users, and administrator authorization.
- Built a centralized frontend API client with bearer authentication, typed responses, network errors, and automatic session cleanup on 401.
- Added database migrations, environment-based configuration, reproducible dependency locks, and provider-neutral deployment documentation.
- Deployed the production application with Neon PostgreSQL, FastAPI on Render, and React on Vercel.

## Tech Stack

Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, SQLite, JWT, bcrypt, pytest, React, TypeScript, Vite, React Router, CSS, Fetch API, Neon, Render, Vercel.

## Business Value

The application makes quote selection auditable: buyers can see the price spread and potential savings, understand how supplier performance affects the decision, and review a concise explanation without allowing a language model to invent commercial facts or compare incompatible currencies.

## CV Section

### Supplier Price Intelligence — Full-Stack Procurement Platform

- Built a production-deployed React/TypeScript/Vite application with a layered FastAPI, SQLAlchemy, and Alembic backend following Repository -> Service -> API boundaries.
- Implemented currency-isolated quote comparison, savings analysis, and explainable supplier ranking across active quotes using transparent price and performance weights.
- Designed a constrained AI explanation layer that consumes deterministic results, cannot override supplier selection, and falls back safely without a paid provider.
- Secured the platform with bcrypt-hashed passwords, expiring JWTs, inactive-user checks, and administrator-only destructive operations; validated it with 96 passing pytest tests and warnings treated as errors.
- Deployed the frontend on Vercel, backend on Render, and PostgreSQL production database on Neon while retaining SQLite for local development.

## LinkedIn Launch Post

I’ve finished building and deploying Supplier Price Intelligence, a project inspired by a practical procurement problem: the lowest quote is not always the best purchasing decision, and comparing prices without considering currency or supplier performance can be misleading.

The platform manages suppliers, products, and quotations, then turns active quotes into decision-ready analysis. It compares prices and calculates potential savings independently for each currency, so USD and EUR offers are never mixed. It also ranks suppliers using transparent price, reliability, delivery, and activity scores.

The application uses a React, TypeScript, and Vite frontend with a FastAPI, SQLAlchemy, and Alembic backend organized around Repository -> Service -> API boundaries. Production runs on Vercel and Render with PostgreSQL on Neon, while SQLite remains available for local development.

I treated AI as an explanation layer rather than a decision-maker. Supplier selection is calculated deterministically first; the AI can explain the result but cannot change prices, scores, rankings, or the recommended supplier. A deterministic fallback keeps the feature useful when an external provider is unavailable.

The final backend suite has 96 passing pytest tests with warnings treated as errors, covering CRUD workflows, authentication, authorization, analytics, currency separation, supplier scoring, and AI safety.

- Live Demo: https://supplier-price-intelligence.vercel.app
- GitHub: https://github.com/WadihHani/supplier-price-intelligence

## Interview Talking Points

- Why Repository -> Service -> API separation keeps procurement rules testable and routes small.
- Why currency partitioning is a correctness boundary, not merely a display choice.
- How the 50/20/15/15 scoring weights and neutral missing-value defaults make decisions explainable.
- How AI safety is achieved by calculating recommendations first and accepting only explanation text afterward.
- Why JWT expiry, generic login errors, inactive-user checks, and admin dependencies are tested separately.
- Tradeoffs of sessionStorage versus cookies and what would change for a public, higher-risk deployment.
- Why SQLite is appropriate for a local portfolio demo but durable production hosting should use a managed relational database and backups.
- How Alembic migrations, pinned Python dependencies, package-lock.json, and clean builds improve reproducibility.
