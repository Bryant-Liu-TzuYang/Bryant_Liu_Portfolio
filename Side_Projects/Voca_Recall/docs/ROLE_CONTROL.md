# Role-Based Access Control (RBAC)

## Overview

Three-tier role system for Voca Recaller:
- **User** (default): Standard application access
- **Developer**: User access + Logging features
- **Admin**: Full access including user management

## Quick Setup

### 1. Run Migration
```bash
cd backend
python migrations/add_user_roles.py
```

### 2. Restart Backend
```bash
python application.py
# or: docker-compose restart backend
```

### 3. Login & Verify
- Login as admin (bryant98360410@gmail.com)
- Verify "Manage Users" appears in navbar
- Verify "Logging" tab appears in Settings

**Note**: Admin email must be registered before running migration.

## Access Control Matrix

| Feature | User | Developer | Admin |
|---------|------|-----------|-------|
| Dashboard | ✅ | ✅ | ✅ |
| Databases | ✅ | ✅ | ✅ |
| Settings - Profile | ✅ | ✅ | ✅ |
| Settings - Email | ✅ | ✅ | ✅ |
| Settings - Logging | ❌ | ✅ | ✅ |
| Settings - Tokens | ✅ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |

## Admin Features

### Web UI (Recommended)
1. Navigate to "Manage Users"
2. **Create users** with role selection
3. **Update roles** via dropdown
4. **Activate/deactivate** accounts
5. **Search** by name or email

### Command Line
```bash
# List all users
python admin_utils.py --list

# Promote user
python admin_utils.py --promote user@example.com admin
python admin_utils.py --promote user@example.com developer

# Demote user
python admin_utils.py --demote user@example.com
```

## API Endpoints

### Admin Endpoints (Require Admin Role)
```
GET    /api/admin/users              - List all users (paginated, searchable)
GET    /api/admin/users/<id>         - Get user details
POST   /api/admin/users              - Create new user
PUT    /api/admin/users/<id>/role    - Update user role
PUT    /api/admin/users/<id>/activate - Toggle active status
GET    /api/admin/users/search       - Search users by email/ID
```

## Implementation Details

### Backend
- **Models** (`models.py`): Added `role` field to User model
- **Auth** (`auth.py`): JWT tokens include role claims
- **Middleware** (`middleware.py`): `@admin_required()` and `@developer_required()` decorators
- **Admin API** (`admin.py`): Full user management endpoints

### Frontend
- **AuthContext** (`AuthContext.js`): `isDeveloper()` and `isAdmin()` helpers
- **Settings** (`Settings.js`): Conditional Logging tab rendering
- **ManageUsers** (`ManageUsers.js`): Admin user management interface
- **Navbar** (`Navbar.js`): Conditional admin link
- **Routes** (`App.js`): Protected `/manage-users` route

### Security
- Backend: JWT authentication + role verification on every request
- Frontend: Role-based UI rendering + protected routes
- JWT tokens embed roles as additional claims
- Role changes require fresh login to take effect

## Troubleshooting

**Admin features not appearing**
- Log out and log back in to get fresh JWT token

**"Admin access required" error**
- Verify user role in database
- Ensure JWT token is fresh

**Default admin not promoted**
- Register bryant98360410@gmail.com first
- Run migration again

**Frontend shows features but API returns 403**
- Backend protection working correctly
- User role not updated in token - requires login

## Files Modified/Created

### Backend
```
backend/
├── app/
│   ├── admin.py              # New: Admin API
│   ├── models.py             # Modified: Added role field
│   ├── auth.py               # Modified: JWT with roles
│   └── middleware.py         # Modified: Role decorators
├── migrations/
│   └── add_user_roles.py     # New: Migration script
└── admin_utils.py            # New: CLI utility
```

### Frontend
```
frontend/src/
├── pages/
│   ├── ManageUsers.js        # New: Admin interface
│   └── Settings.js           # Modified: Conditional Logging tab
├── contexts/
│   └── AuthContext.js        # Modified: Role helpers
└── components/
    └── Navbar.js             # Modified: Admin link
```
