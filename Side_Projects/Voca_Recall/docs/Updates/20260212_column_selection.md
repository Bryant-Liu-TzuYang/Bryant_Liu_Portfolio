# Column Selection Feature Update - February 12, 2026

## Overview
This update introduces the ability for users to select specific columns (properties) from their Notion databases to be included in the scheduled emails. previously, all columns were included by default or a fixed set. Now, users can customize the content of their vocabulary emails.

## Changes Implemented

### 1. Backend Changes

#### Data Model (`backend/app/models.py`)
- **`EmailService` Model**:
  - Added `column_selection` field (JSON type) to store the list of selected column names.
  - Updated `to_dict` method to include `column_selection`.

#### API Endpoints
- **Database (`backend/app/database.py`)**:
  - Added `GET /api/databases/{id}/properties`: Fetches the schema (properties) of a Notion database to list available columns.
  
- **Email Service (`backend/app/email_service.py`)**:
  - Updated `POST /api/email-services`: Accepts `column_selection` list in the request body.
  - Updated `PUT /api/email-services/{id}`: ongoing updates to `column_selection`.

#### Email Logic (`backend/app/email.py`)
- Updated email generation logic to filter vocabulary properties based on the `column_selection` list stored in the service configuration.

### 2. Frontend Changes

#### Components (`frontend/src/components/EmailServiceModal.js`)
- Added a column selection step/section in the service creation/editing modal.
- Fetches available columns using the new `GET /api/databases/{id}/properties` endpoint when a database is selected.
- Allows users to select multiple columns via checkboxes.
- Saves the selected columns to the backend.

### 3. Database Migration
- Added a migration step to add the `column_selection` column to the `email_services` table.
- Existing services will have an empty or default selection (implying all or default behavior depending on implementation).

## API Changes Summary

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/databases/{id}/properties` | Get available columns for a database | **New** |
| POST | `/api/email-services` | Create service (now accepts `column_selection`) | **Updated** |
| PUT | `/api/email-services/{id}` | Update service (now accepts `column_selection`) | **Updated** |

## Impact
- Users can now tailor their vocabulary emails to only show relevant information (e.g., hiding created timestamps or internal IDs).
- Improved flexibility for different Notion database structures.
