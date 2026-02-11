# Backended API Documentation

Base URL: `/api`

All endpoints except Auth (Register/Login/Reset) require a valid JWT Access Token in the `Authorization` header: `Bearer <token>`.

## Authentication (`/api/auth`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| POST | `/register` | Register a new user | `{ "email": "...", "password": "...", ... }` | [`backend/app/auth.py`](../backend/app/auth.py) | [`contexts/AuthContext.js`](../frontend/src/contexts/AuthContext.js): `register` |
| POST | `/login` | Authenticate user | `{ "email": "...", "password": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) | [`contexts/AuthContext.js`](../frontend/src/contexts/AuthContext.js): `login` |
| POST | `/refresh` | Refresh access token | Requires Refresh Token cookie | [`backend/app/auth.py`](../backend/app/auth.py) | [`contexts/AuthContext.js`](../frontend/src/contexts/AuthContext.js): `refreshToken` |
| POST | `/logout` | Logout user | - | [`backend/app/auth.py`](../backend/app/auth.py) | - |
| GET | `/me` | Get current authenticated user | - | [`backend/app/auth.py`](../backend/app/auth.py) | [`contexts/AuthContext.js`](../frontend/src/contexts/AuthContext.js): `checkAuth` (useEffect) |
| POST | `/forgot-password` | Request password reset email | `{ "email": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) | [`pages/ForgotPassword.js`](../frontend/src/pages/ForgotPassword.js): `handleSubmit` |
| POST | `/reset-password` | Reset password using token | `{ "token": "...", "new_password": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) | [`pages/ResetPassword.js`](../frontend/src/pages/ResetPassword.js): `handleSubmit` |
| POST | `/validate-reset-token` | Validate a reset token | `{ "token": "..." }` | [`backend/app/auth.py`](../backend/app/auth.py) | [`pages/ResetPassword.js`](../frontend/src/pages/ResetPassword.js): `validateToken` |

## User Management (`/api/user`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| GET | `/profile` | Get user profile details | - | [`backend/app/user.py`](../backend/app/user.py) | - |
| PUT | `/profile` | Update user profile | `{ "first_name": "...", ... }` | [`backend/app/user.py`](../backend/app/user.py) | [`contexts/AuthContext.js`](../frontend/src/contexts/AuthContext.js): `updateProfile` |
| GET | `/email-settings` | Get user email preferences | - | [`backend/app/user.py`](../backend/app/user.py) | [`pages/Settings.js`](../frontend/src/pages/Settings.js): `fetchEmailSettings` |
| PUT | `/email-settings` | Update user email preferences | `{ "is_active": true/false, ... }` | [`backend/app/user.py`](../backend/app/user.py) | [`pages/Settings.js`](../frontend/src/pages/Settings.js): `saveEmailSettings` |
| GET | `/stats` | Get user usage statistics | - | [`backend/app/user.py`](../backend/app/user.py) | [`pages/Dashboard.js`](../frontend/src/pages/Dashboard.js): `fetchStats` |

## Notion Tokens (`/api/tokens`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| GET | `/` | List all Notion tokens | - | [`backend/app/tokens.py`](../backend/app/tokens.py) | [`pages/ManageTokens.js`](../frontend/src/pages/ManageTokens.js): `fetchTokens` |
| POST | `/` | Add a new Notion token | `{ "token": "...", "token_name": "..." }` | [`backend/app/tokens.py`](../backend/app/tokens.py) | [`pages/ManageTokens.js`](../frontend/src/pages/ManageTokens.js): `handleAddToken` |
| GET | `/{id}` | Get specific token details | - | [`backend/app/tokens.py`](../backend/app/tokens.py) | - |
| PUT | `/{id}` | Update token details | `{ "token_name": "...", ... }` | [`backend/app/tokens.py`](../backend/app/tokens.py) | [`pages/ManageTokens.js`](../frontend/src/pages/ManageTokens.js): `handleUpdateToken` |

## Notion Databases (`/api/databases`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| GET | `/` | List all databases | - | [`backend/app/database.py`](../backend/app/database.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `fetchDatabases`<br>[`pages/Services.js`](../frontend/src/pages/Services.js): `fetchDatabases`<br>[`pages/Settings.js`](../frontend/src/pages/Settings.js): `fetchDatabases` |
| POST | `/` | Add a new database | `{ "database_id": "...", ... }` | [`backend/app/database.py`](../backend/app/database.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `onSubmit` |
| GET | `/{id}` | Get database details | - | [`backend/app/database.py`](../backend/app/database.py) | - |
| PUT | `/{id}` | Update database | `{ "database_name": "...", ... }` | [`backend/app/database.py`](../backend/app/database.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `onSubmit` |
| DELETE | `/{id}` | Delete database | - | [`backend/app/database.py`](../backend/app/database.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `handleDelete` |
| POST | `/{id}/test` | Test database connection | - | [`backend/app/database.py`](../backend/app/database.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `handleTestConnection` |

## Email Services (`/api/email-services`)

Services are scheduled jobs linked to Notion databases.

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| GET | `/` | List all email services | - | [`backend/app/email_service.py`](../backend/app/email_service.py) | [`pages/Services.js`](../frontend/src/pages/Services.js): `fetchServices`<br>[`pages/Settings.js`](../frontend/src/pages/Settings.js): `fetchEmailServices` |
| POST | `/` | Create email service | `{ "service_name": "...", ... }` | [`backend/app/email_service.py`](../backend/app/email_service.py) | [`components/EmailServiceModal.js`](../frontend/src/components/EmailServiceModal.js): `handleSubmit` |
| GET | `/{id}` | Get service details | - | [`backend/app/email_service.py`](../backend/app/email_service.py) | - |
| PUT | `/{id}` | Update service | `{ "service_name": "...", ... }` | [`backend/app/email_service.py`](../backend/app/email_service.py) | [`components/EmailServiceModal.js`](../frontend/src/components/EmailServiceModal.js): `handleSubmit` |
| DELETE | `/{id}` | Delete service | - | [`backend/app/email_service.py`](../backend/app/email_service.py) | [`pages/Services.js`](../frontend/src/pages/Services.js): `handleDeleteService`<br>[`pages/Databases.js`](../frontend/src/pages/Databases.js): `handleDeleteEmailService` |
| GET | `/database/{db_id}` | Get services for a database | - | [`backend/app/email_service.py`](../backend/app/email_service.py) | [`pages/Databases.js`](../frontend/src/pages/Databases.js): `fetchEmailServices` |

## Email Actions & Logs (`/api/email`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| POST | `/send-test` | Trigger a test email immediately | `{ "service_id": 1 }` OR ... | [`backend/app/email.py`](../backend/app/email.py) | [`pages/Settings.js`](../frontend/src/pages/Settings.js): `sendTestEmail` |
| GET | `/logs` | Get history of sent emails | `?page=1&per_page=10` | [`backend/app/email.py`](../backend/app/email.py) | [`pages/EmailLogs.js`](../frontend/src/pages/EmailLogs.js): `fetchLogs`<br>[`pages/Settings.js`](../frontend/src/pages/Settings.js): `fetchLogs` |

## Frontend Logging (`/api/frontend`)

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| POST | `/logs` | Send frontend logs to backend | `{ "level": "INFO", ... }` | [`backend/app/frontend_logs.py`](../backend/app/frontend_logs.py) | [`utils/logger.js`](../frontend/src/utils/logger.js): `_sendLogWithRetry` |
| GET | `/logs/info` | Get debug info about log files | - | [`backend/app/frontend_logs.py`](../backend/app/frontend_logs.py) | [`components/LoggingStatus.js`](../frontend/src/components/LoggingStatus.js): `fetchLoggingInfo` |

## Admin (`/api/admin`)

Requires `admin` role.

| Method | Endpoint | Description | Request Body | Related File | Caller |
|--------|----------|-------------|--------------|--------------|--------|
| GET | `/users` | List all users | `?page=1&search=...` | [`backend/app/admin.py`](../backend/app/admin.py) | [`pages/ManageUsers.js`](../frontend/src/pages/ManageUsers.js): `fetchUsers` |
| GET | `/users/{id}` | Get user details | - | [`backend/app/admin.py`](../backend/app/admin.py) | - |
| PUT | `/users/{id}/role` | Promote/Demote user | `{ "role": "..." }` | [`backend/app/admin.py`](../backend/app/admin.py) | [`pages/ManageUsers.js`](../frontend/src/pages/ManageUsers.js): `handleRoleChange` |
