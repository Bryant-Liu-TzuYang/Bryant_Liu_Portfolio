# Health Check Endpoint for Kubernetes

## What You Need to Add

Kubernetes uses health check endpoints to know if your application is working properly. The k8s configuration files expect a `/health` endpoint in your Flask backend.

## Add This to Your Flask App

Add this code to your `backend/app.py` or create a new route file:

```python
from flask import jsonify
from app import create_app, db

app = create_app()

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Kubernetes liveness and readiness probes.
    Returns 200 if the app is healthy, 500 otherwise.
    """
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - more strict than liveness.
    Only returns healthy when the app is fully ready to serve traffic.
    """
    try:
        # Check database
        db.session.execute('SELECT 1')
        
        # Add other checks here if needed
        # e.g., check if Redis is accessible, check if migrations are done, etc.
        
        return jsonify({
            'status': 'ready',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'error': str(e)
        }), 503
```

## Or a Simple Version

If you don't want to check the database:

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check that just returns 200 OK."""
    return jsonify({'status': 'healthy'}), 200
```

## Why This Matters

- **Liveness Probe**: Kubernetes uses `/health` to check if your pod is alive
  - If it fails, Kubernetes will restart the pod
  
- **Readiness Probe**: Kubernetes uses `/health` to check if your pod is ready
  - If it fails, Kubernetes won't send traffic to that pod

## Testing

```bash
# Test locally
curl http://localhost:5000/health

# Test in Kubernetes
kubectl exec -it BACKEND-POD -n voca-recaller -- curl http://localhost:5000/health
```

## Already Have a Health Check?

If your app already has a health check endpoint at a different URL (like `/api/health` or `/status`), you can either:

1. Update the k8s configuration files to use your existing endpoint
2. Add an additional `/health` endpoint that Kubernetes expects

To update the k8s files, change this in `backend.yaml` and `celery-worker.yaml`:

```yaml
livenessProbe:
  httpGet:
    path: /health  # Change this to your existing path
    port: 5000
```
