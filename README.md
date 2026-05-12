# Feedback Admin Backend

Python/FastAPI backend for `web-admin` admin login and permission management.

## Setup

1. Create PostgreSQL database:

```sql
CREATE DATABASE feedback_admin;
```

2. Install dependencies:

```powershell
cd C:\Feedback\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Configure environment:

```powershell
Copy-Item .env.example .env
```

Update `DATABASE_URL` and `SECRET_KEY` in `.env`.

4. Run:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`web-admin` uses `http://localhost:8000/api` by default. If the backend runs elsewhere,
copy `C:\Feedback\web-admin\.env.example` to `C:\Feedback\web-admin\.env` and update
`VITE_ADMIN_API_URL`.

Default seeded users:

- `studio` / `studio123` -> Edit admin, Form Studio
- `admin` / `admin123` -> Super admin, Front admin
- `branch` / `branch123` -> Branch admin
- `direct` / `direct123` -> Direct admin

If you need to force-register only the full admin account directly in PostgreSQL:

```powershell
cd C:\Feedback\backend
.\seed-admin.ps1 -Password 'YOUR_POSTGRES_PASSWORD'
```

Blocked users cannot log in.
