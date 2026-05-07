# Assessment API

REST API for managing clients and companies with an approval system.

## Setup

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8001
- Swagger: http://localhost:8001/api/docs/

## Tests

```bash
docker compose exec web pytest --cov=apps
```

## API Endpoints

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/auth/register/` | No |
| POST | `/api/auth/login/` | No |
| POST | `/api/auth/token/refresh/` | No |
| POST | `/api/companies/` | JWT |
| GET | `/api/companies/` | JWT |
| GET | `/api/companies/<id>/` | JWT |
| POST | `/api/clients/` | JWT |
| GET | `/api/clients/` | JWT |
| GET | `/api/clients/<id>/` | JWT |
| GET | `/api/approvals/` | Admin |
| PATCH | `/api/approvals/<id>/` | Admin |
