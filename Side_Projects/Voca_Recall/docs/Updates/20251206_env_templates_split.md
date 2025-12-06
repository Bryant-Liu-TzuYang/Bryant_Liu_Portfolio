# Environment Template Split

**Date:** December 6, 2025

## Summary

Split the single `env.example` file into separate development and production templates to better reflect the different configuration needs and importance levels documented in `ENV_VARIABLES.md`.

## Changes Made

### 1. New Template Files

Created two separate environment template files:

- **`backend/dev-env.example`** - Development environment template
  - Contains only absolutely required variables (SMTP credentials)
  - Includes sensible defaults for security keys (marked as insecure)
  - All optional variables are commented out with explanations
  - Follows the 3-category structure: Required, Can Use Defaults, Can Skip Entirely

- **`backend/prod-env.example`** - Production environment template
  - Contains all critical and highly recommended variables
  - Follows the 2-category structure: Critical Variables, Highly Recommended Variables
  - Includes security key generation commands
  - Comprehensive production configuration guide

### 2. Updated `setup.sh`

Modified the setup script to automatically use the correct template:

**New Behavior:**
- `./setup.sh dev` → Creates `.env` from `backend/dev-env.example`
- `./setup.sh prod` → Creates `.env` from `backend/prod-env.example`

**Key Changes:**
- Added `env_type` parameter to `validate_environment()` function
- Automatically selects appropriate template based on command (`dev` or `prod`)
- Informs users if `.env` already exists instead of overwriting
- Removed standalone `env` command (now integrated into `dev`/`prod`)

**Updated Help Message:**
```bash
First time setup:
  1. Run: ./setup.sh dev (or ./setup.sh prod)
  2. Edit .env file with your configuration
  3. Run: ./setup.sh dev (or ./setup.sh prod) again to start services
```

### 3. Updated Documentation

#### README.md
- Updated Quick Start section to explain the new template system
- Clarified that `.env` is automatically created from the appropriate template
- Added note about existing `.env` files being preserved
- Updated environment variable references to point to new template files

#### ENV_VARIABLES.md
- Added setup instructions for both automated (`./setup.sh`) and manual workflows
- Updated template references to use `dev-env.example` and `prod-env.example`
- Added instructions for manual setup if users prefer not to use the script

### 4. Removed Files

- **`backend/env.example`** - Replaced by separate dev/prod templates

## Benefits

1. **Clearer Separation**: Development and production configurations are now distinct, reducing confusion
2. **Better Onboarding**: Developers see only what they need for local development
3. **Improved Security**: Production template emphasizes security requirements
4. **Automated Setup**: Setup script automatically selects the right template
5. **Documentation Alignment**: Templates now match the structure in `ENV_VARIABLES.md`

## Usage Examples

### Development Setup
```bash
# First run - creates .env from dev-env.example
./setup.sh dev

# Edit .env to add SMTP credentials
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# Second run - validates and starts services
./setup.sh dev
```

### Production Setup
```bash
# First run - creates .env from prod-env.example
./setup.sh prod

# Edit .env with all production values
# - Generate secure SECRET_KEY and JWT_SECRET_KEY
# - Configure production database
# - Set up production SMTP service
# - Update FRONTEND_URL to your domain

# Second run - validates and starts services
./setup.sh prod
```

### Switching Environments
```bash
# To switch from dev to prod template:
rm .env
./setup.sh prod

# To switch from prod to dev template:
rm .env
./setup.sh dev
```

## Migration Guide

For existing installations:

1. Your current `.env` file will continue to work - no changes needed
2. If you want to use the new templates:
   ```bash
   # Backup your current .env
   cp .env .env.backup
   
   # Remove current .env
   rm .env
   
   # Create new .env from appropriate template
   ./setup.sh dev  # or ./setup.sh prod
   
   # Copy your values from .env.backup to the new .env
   ```

## Related Files

- `backend/dev-env.example` - Development template
- `backend/prod-env.example` - Production template  
- `setup.sh` - Setup script with automatic template selection
- `docs/ENV_VARIABLES.md` - Complete environment variable documentation
- `README.md` - Updated quick start guide
