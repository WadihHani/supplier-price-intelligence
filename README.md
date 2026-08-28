# Supplier Price Intelligence

## Local backend

Create and activate a Python virtual environment, then install dependencies and
apply migrations:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Copy the placeholders from `.env.example` into an ignored local `.env`. Set a
private `JWT_SECRET_KEY`; keep `JWT_ALGORITHM=HS256`, configure the access-token
lifetime, and allow the local frontend with
`CORS_ALLOWED_ORIGINS=http://localhost:5173`.

Create a local user explicitly—no user is created on application startup:

```powershell
python scripts/create_dev_user.py developer@example.com "your-password"
```

The command uses the existing authentication service and password hashing. It
does not store or print the plaintext password or password hash.

## Local frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` from its ignored `.env`. For local
development use:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Open `http://localhost:5173/login` and sign in with the local user. The JWT is
kept only in `sessionStorage`, attached to protected API requests, and removed
on logout or a `401` response.
