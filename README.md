# Assessment API

Django REST Framework backend API with JWT authentication, role-based permissions, and Redis caching.

## Stack

- Python 3.11 / Django 5.1 / DRF 3.15
- PostgreSQL 16 / Redis 7
- JWT auth (simplejwt) / drf-spectacular (Swagger)
- Docker & Docker Compose

## Quick Start (Docker)

Everything runs in containers — no local dependencies needed.

```bash
# Clone and start
cp .env.example .env
docker compose up --build

# The API is available at http://localhost:8000
# Swagger docs at http://localhost:8000/api/docs/
```

The entrypoint automatically waits for PostgreSQL and runs migrations.

### Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## Running Tests

```bash
# Run full test suite with coverage
docker compose exec web pytest --cov=apps --cov-report=term-missing

# Run specific test file
docker compose exec web pytest tests/test_companies.py -v
```

Tests use SQLite in-memory and local memory cache — no external dependencies needed.

## API Endpoints

### Auth (no token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Get access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Companies (token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/companies/` | Create a company |
| GET | `/api/companies/` | List companies |
| GET | `/api/companies/<id>/` | Get company detail |

### Clients (token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/clients/` | Create a client |
| GET | `/api/clients/` | List clients |
| GET | `/api/clients/<id>/` | Get client detail |

### Approvals (admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/approvals/` | List all approvals |
| PATCH | `/api/approvals/<id>/` | Update approval status |

## Response Format

All GET endpoints for companies and clients return:

```json
{
  "data": { "id": "...", "name": "...", ... },
  "approval": {
    "id": "...",
    "status": "pending",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

List endpoints wrap results in pagination:

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/companies/?page=2",
  "previous": null,
  "results": [{ "data": {...}, "approval": {...} }, ...]
}
```

## Company Types

Each type requires specific fields:

| Type | Required Fields |
|------|----------------|
| `small_business` | `employee_count`, `industry` |
| `startup` | `funding_stage`, `founded_year` |
| `corporate` | `revenue`, `stock_symbol` |

## Performance Decisions

**Database optimization:**
- `db_index=True` on all FK fields and frequently filtered columns (`status`, `type`, `object_id`)
- `select_related()` on FK lookups (Client -> Company, Approval -> reviewed_by)
- `prefetch_related()` with `Prefetch` objects to fetch only needed approval fields
- Approval creation in signals wrapped in `transaction.atomic()`

**Caching (Redis):**
- Company and client list endpoints cached for 60 seconds
- Cache automatically invalidated via `post_save` and `post_delete` signals
- Uses Django's cache framework with `django-redis` backend

**Pagination:**
- Default page size: 20, max: 100
- Custom `page_size` query parameter supported

**Query profiling:**
- django-silk enabled in development (`DEBUG=True`) at `/silk/`

## Postman Collection

Import `postman_collection.json` into Postman:

1. Open Postman -> Import -> Upload file
2. Select `postman_collection.json`
3. The `Login` request auto-sets `{{token}}` for authenticated requests
4. Set `{{base_url}}` to `http://localhost:8000` (default)

## Project Structure

```
├── config/             # Django settings, URLs, WSGI
├── apps/
│   ├── accounts/       # Custom User model, JWT auth
│   ├── companies/      # Company CRUD + signals
│   ├── clients/        # Client CRUD + signals
│   └── approvals/      # Approval management, permissions
├── tests/              # pytest test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```
