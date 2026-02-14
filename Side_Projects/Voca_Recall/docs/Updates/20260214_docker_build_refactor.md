# Docker Build & Deployment Refactor - 2026-02-14

## Overview
This update refactors the production Docker setup to eliminate the need for running `npm run build` locally before deployment. The frontend application is now built inside the Docker container using a multi-stage build process.

## Motivation
Previously, the deployment relied on a standalone Nginx container mounting a local `frontend/build` directory. This required developers to manually build the React application on their host machine before deploying, leading to:
- Dependency on local Node.js environment.
- Risk of inconsistency between local builds and production.
- Extra manual steps during deployment.

## Key Changes

### 1. Docker Compose (`docker-compose.prod.yml`)
The separate `nginx` and `frontend` services have been consolidated.
- **Removed**: The standalone `frontend` service.
- **Updated**: The `nginx` service now builds from `frontend/Dockerfile` instead of using a generic `nginx:alpine` image.
- **Removed Volume**: The line ` - ./frontend/build:/usr/share/nginx/html` was removed. The container now relies on files copied during the build process rather than files mounted from the host.

**New Service Configuration:**
```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: voca_recaller_nginx_prod
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:5000}
    networks:
      - voca_recaller_network_prod
```

### 2. Frontend Dockerfile (`frontend/Dockerfile`)
The Dockerfile utilizes a multi-stage build strategy:
1.  **Build Stage (`FROM node:24-alpine AS build`)**: Installs dependencies and compiles the React application (`npm run build`).
2.  **Production Stage (`FROM nginx:alpine`)**: Starts fresh with a lightweight Nginx image.
3.  **Artifact Copy (`COPY --from=build ...`)**: Only the compiled static files (`/app/build`) are copied from the first stage to the Nginx serving directory (`/usr/share/nginx/html`). The heavy `node_modules` are discarded.

## Analysis: Standalone vs. Integrated Container

We moved from a "Standalone Nginx" approach to an "Integrated App Image" approach.

| Feature | Standalone Nginx (Old) | Integrated Image (New) |
| :--- | :--- | :--- |
| **Build Location** | Host Machine (Local) | Inside Docker Container |
| **Deployment Command** | `npm run build && docker-compose up` | `docker-compose up --build` |
| **Consistency** | Low (Depends on local env) | High (Immutable artifact) |
| **Config Updates** | Fast (Reload without rebuild) | Slower (Requires rebuild) |
| **Host Requirements** | Node.js required locally | Docker only |

### detailed Pros & Cons (New Approach)
**Pros:**
*   **Immutable Deployments**: The image contains exact code and config. If it works in staging, it works in production.
*   **Simplified Pipeline**: One command handles everything.
*   **Clean Host System**: No need to maintain Node.js versions on the production server.
*   **Better Scaling**: Self-contained images are easier to replicate in orchestrators like Kubernetes.

**Cons:**
*   **Slower Builds**: Docker must install dependencies during the build (mitigated by layer caching).

## New Deployment Workflow
To deploy the latest code, simply run:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```
