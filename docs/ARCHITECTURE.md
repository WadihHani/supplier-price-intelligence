# Architecture

Supplier Price Intelligence is a React single-page application backed by a layered FastAPI service. The backend keeps persistence, business rules, and HTTP concerns separate without introducing additional infrastructure.

## Components

- **Frontend:** React, TypeScript, React Router, and a centralized typed Fetch client. The browser stores the access token in sessionStorage and attaches it to protected requests.
- **API:** FastAPI routes validate request data, resolve authentication dependencies, call services, and serialize Pydantic response models.
- **Authentication:** bcrypt hashes passwords; signed JWT access tokens include an expiry. Route dependencies reject missing, invalid, expired, or inactive-user credentials and enforce administrator-only deletion.
- **Services:** own CRUD coordination and deterministic procurement rules, including comparisons, analysis, scoring, and recommendations.
- **Repositories:** isolate SQLAlchemy queries and persistence operations.
- **Database:** SQLAlchemy uses DATABASE_URL; Alembic owns schema migrations. SQLite is the local/demo default.
- **AI provider abstraction:** selects the mock, OpenAI, or unavailable-provider implementation. Provider failures fall back to a deterministic explanation.

## Standard Request Flow

~~~text
React page
  -> typed API client
  -> FastAPI route
  -> JWT/admin dependency
  -> service
  -> repository
  -> SQLAlchemy session
  -> database
~~~

Routes contain HTTP concerns while services remain authoritative for business decisions. Repositories do not calculate procurement metrics.

## Procurement Recommendation Flow

~~~text
React Procurement Intelligence page
  -> AI recommendation endpoint
  -> deterministic quote comparison + procurement analysis + supplier scoring
  -> structured facts and deterministic recommended supplier
  -> AI provider explanation (or deterministic fallback)
  -> response preserving the deterministic recommendation
~~~

Currencies are partitioned before comparison or scoring. No service converts or compares monetary values across currencies. The AI provider is downstream of deterministic analysis and cannot change the returned supplier, price, or score.

## Configuration Boundaries

Backend configuration is environment-driven through Pydantic Settings. The database URL, JWT parameters, trusted CORS origins, and AI provider values are not embedded in deployment code. The frontend API origin is injected at build time through VITE_API_BASE_URL.

For a public deployment, serve the Vite build as static assets with an index.html SPA fallback, run FastAPI as a separate web service, and use durable database storage appropriate to the selected platform.
