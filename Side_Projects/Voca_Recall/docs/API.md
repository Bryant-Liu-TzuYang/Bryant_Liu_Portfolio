# Backended API Documentation

Base URL: `/api`

All endpoints except Auth (Register/Login/Reset) require a valid JWT Access Token in the `Authorization` header: `Bearer <token>`.

## Authentication (`/api/auth`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| POST | `/register` | Register a new user | `{ "email": "...", "password": "...", "first_name": "...", "last_name": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/login` | Authenticate user | `{ "email": "...", "password": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/refresh` | Refresh access token | Requires Refresh Token cookie | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/logout` | Logout user | - | [`backend/app/auth.py`](../backend/app/auth.py) |
| GET | `/me` | Get current authenticated user | - | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/forgot-password` | Request password reset email | `{ "email": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/reset-password` | Reset password using token | `{ "token": "...", "new_password": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) |
| POST | `/validate-reset-token` | Validate a reset token | `{ "token": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) |

## User Management (`/api/user`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| GET | `/profile` | Get user profile details | - | [`backend/app/user.py`](../backend/app/user.py) |
| PUT | `/profile` | Update user profile | `{ "first_name": "...", "last_name": "..." }` | [`backend/app/user.py`](../backend/app/user.py) |
| GET | `/email-settings` | Get user email preferences | - | [`backend/app/user.py`](../backend/app/user.py) |
| PUT | `/email-settings` | Update user email preferences | `{ "is_active": true/false, ... }` | [`backend/app/user.py`](../backend/app/user.py) |
| GET | `/stats` | Get user usage statistics | - | [`backend/app/user.py`](../backend/app/user.py) |

## Notion Tokens (`/api/tokens`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| GET | `/` | List all Notion tokens | - | [`backend/app/tokens.py`](../backend/app/tokens.py) |
| POST | `/` | Add a new Notion token | `{ "token": "secret_...", "token_name": "..." }` | [`backend/app/tokens.py`](../backend/app/tokens.py) |
| GET | `/{id}` | Get specific token details | - | [`backend/app/tokens.py`](../backend/app/tokens.py) |
| PUT | `/{id}` | Update token details | `{ "token_name": "...", "is_active": true/false }` | [`backend/app/tokens.py`](../backend/app/tokens.py) |

## Notion Databases (`/api/databases`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| GET | `/` | List all databases | - | [`backend/app/database.py`](../backend/app/database.py) |
| POST | `/` | Add a new database | `{ "database_id": "...", "token_id": 1, "database_name": "..." }` | [`backend/app/database.py`](../backend/app/database.py) |
| GET | `/{id}` | Get database details | - | [`backend/app/database.py`](../backend/app/database.py) |
| PUT | `/{id}` | Update database | `{ "database_name": "...", ... }` | [`backend/app/database.py`](../backend/app/database.py) |
| DELETE | `/{id}` | Delete database | - | [`backend/app/database.py`](../backend/app/database.py) |
| POST | `/{id}/test` | Test database connection | - | [`backend/app/database.py`](../backend/app/database.py) |

## Email Services (`/api/email-services`)

Services are scheduled jobs linked to Notion databases.

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| GET | `/` | List all email services | - | [`backend/app/email_service.py`](../backend/app/email_service.py) |
| POST | `/` | Create email service | `{ "service_name": "...", "database_id": 1, "frequency": "daily", "send_time": "09:00", ... }` | [`backend/app/email_service.py`](../backend/app/email_service.py) |
| GET | `/{id}` | Get service details | - | [`backend/app/email_service.py`](../backend/app/email_service.py) |
| PUT | `/{id}` | Update service | `{ "service_name": "...", "is_active": true/false, ... }` | [`backend/app/email_service.py`](../backend/app/email_service.py) |
| DELETE | `/{id}` | Delete service | - | [`backend/app/email_service.py`](../backend/app/email_service.py) |
| GET | `/database/{db_id}` | Get services for a database | - | [`backend/app/email_service.py`](../backend/app/email_service.py) |

## Email Actions & Logs (`/api/email`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| POST | `/send-test` | Trigger a test email immediately | `{ "service_id": 1 }` OR `{ "database_pk": 1 }` | [`backend/app/email.py`](../backend/app/email.py) |
| GET | `/logs` | Get history of sent emails | `?page=1&per_page=10` | [`backend/app/email.py`](../backend/app/email.py) |

## Frontend Logging (`/api/frontend`)

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| POST | `/logs` | Send frontend logs to backend | `{ "level": "INFO", "message": "...", "context": "..." }` | [`backend/app/frontend_logs.py`](../backend/app/frontend_logs.py) |
| GET | `/logs/info` | Get debug info about log files | - | [`backend/app/frontend_logs.py`](../backend/app/frontend_logs.py) |

## Admin (`/api/admin`)

Requires `admin` role.

| Method | Endpoint | Description | Request Body | Related File |
|--------|----------|-------------|--------------|--------------|
| GET | `/users` | List all users | `?page=1&search=...` | [`backend/app/admin.py`](../backend/app/admin.py) |
| GET | `/users/{id}` | Get user details | - | [`backend/app/admin.py`](../backend/app/admin.py) |
| PUT | `/users/{id}/role` | Promote/Demote user | `{ "role": "admin|developer|user" }` | [`backend/app/admin.py`](../backend/app/admin.py) |
