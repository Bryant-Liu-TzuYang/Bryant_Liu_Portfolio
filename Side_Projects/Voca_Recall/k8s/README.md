# Kubernetes Quick Reference for Voca_Recaller

## File Overview

| File | Purpose | What It Does |
|------|---------|--------------|
| `namespace.yaml` | Creates a "folder" for your app | Organizes all resources |
| `configmap.yaml` | Non-sensitive config | Database URLs, Redis config, etc. |
| `secret.yaml` | Sensitive data | Passwords, API keys (base64 encoded) |
| `mysql-pvc.yaml` | Storage for database | Requests disk space for MySQL data |
| `mysql.yaml` | Database deployment | Runs MySQL with persistent storage |
| `redis.yaml` | Message broker | Runs Redis for Celery tasks |
| `backend.yaml` | Flask API | Your Python backend |
| `celery-worker.yaml` | Background tasks | Processes async jobs |
| `frontend.yaml` | React UI | Your web interface |
| `ingress.yaml` | External access | Routes internet traffic to your app |

## Deployment Order

```bash
# IMPORTANT: Deploy in this order!
1. namespace.yaml       # Create the namespace first
2. secret.yaml         # Create secrets (or use kubectl create)
3. configmap.yaml      # Create configuration
4. mysql-pvc.yaml      # Request storage
5. mysql.yaml          # Deploy database
6. redis.yaml          # Deploy Redis
7. backend.yaml        # Deploy Flask backend
8. celery-worker.yaml  # Deploy Celery workers
9. frontend.yaml       # Deploy React frontend
10. ingress.yaml       # Set up external access
```

**Or use the automated script:**
```bash
./k8s/deploy.sh
```

## Essential Commands

### View Status
```bash
# See everything
kubectl get all -n voca-recaller

# See pods
kubectl get pods -n voca-recaller

# See services
kubectl get services -n voca-recaller

# See ingress
kubectl get ingress -n voca-recaller

# Watch pods in real-time
kubectl get pods -n voca-recaller -w
```

### View Logs
```bash
# Backend logs
kubectl logs -n voca-recaller -l app=backend

# Follow logs (like tail -f)
kubectl logs -n voca-recaller -l app=backend -f

# Last 100 lines
kubectl logs -n voca-recaller -l app=backend --tail=100

# Specific pod
kubectl logs -n voca-recaller POD-NAME

# Previous crashed pod
kubectl logs -n voca-recaller POD-NAME --previous
```

### Troubleshooting
```bash
# Detailed info about a pod
kubectl describe pod POD-NAME -n voca-recaller

# Shell into a pod
kubectl exec -it POD-NAME -n voca-recaller -- /bin/bash

# Run a command in a pod
kubectl exec POD-NAME -n voca-recaller -- ls /app

# View recent events
kubectl get events -n voca-recaller --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward -n voca-recaller service/backend 5000:5000
# Then visit http://localhost:5000
```

### Updates and Scaling
```bash
# Scale deployment
kubectl scale deployment backend --replicas=3 -n voca-recaller

# Update image
kubectl set image deployment/backend backend=your-image:v2 -n voca-recaller

# Restart deployment (recreate pods)
kubectl rollout restart deployment/backend -n voca-recaller

# Check rollout status
kubectl rollout status deployment/backend -n voca-recaller

# Rollback to previous version
kubectl rollout undo deployment/backend -n voca-recaller

# View rollout history
kubectl rollout history deployment/backend -n voca-recaller
```

### Resource Management
```bash
# View resource usage
kubectl top pods -n voca-recaller
kubectl top nodes

# Edit a resource
kubectl edit deployment backend -n voca-recaller

# Delete a specific resource
kubectl delete pod POD-NAME -n voca-recaller

# Delete everything
kubectl delete namespace voca-recaller
```

## Common Issues and Solutions

### Issue: Pods in "Pending" state
```bash
# Check why
kubectl describe pod POD-NAME -n voca-recaller

# Look for:
# - "Insufficient cpu" or "Insufficient memory" -> Need more cluster resources
# - "FailedScheduling" -> Node selector issues
# - PVC issues -> Check PVC status
```

### Issue: Pods in "CrashLoopBackOff"
```bash
# View logs to see the error
kubectl logs POD-NAME -n voca-recaller --previous

# Common causes:
# - Application error (check logs)
# - Missing environment variables
# - Can't connect to database
```

### Issue: Can't access application
```bash
# 1. Check pods are running
kubectl get pods -n voca-recaller

# 2. Test backend directly
kubectl port-forward -n voca-recaller service/backend 5000:5000
# Visit http://localhost:5000

# 3. Check ingress
kubectl describe ingress voca-recaller-ingress -n voca-recaller

# 4. Check if Ingress controller is running
kubectl get pods -n ingress-nginx
```

### Issue: Database connection errors
```bash
# Check MySQL is running
kubectl get pods -n voca-recaller -l app=mysql

# Check MySQL logs
kubectl logs -n voca-recaller -l app=mysql

# Test connection from backend pod
kubectl exec -it BACKEND-POD -n voca-recaller -- mysql -h mysql -u root -p
```

## Configuration Updates

### Update ConfigMap
```bash
# Edit the configmap.yaml file, then:
kubectl apply -f k8s/configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n voca-recaller
kubectl rollout restart deployment/celery-worker -n voca-recaller
```

### Update Secret
```bash
# Create new secret
kubectl create secret generic voca-recaller-secrets \
  --namespace=voca-recaller \
  --from-literal=mysql-root-password='NewPassword' \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment/backend -n voca-recaller
kubectl rollout restart statefulset/mysql -n voca-recaller
```

## Before You Start

### 1. Update Image Names
Edit these files to use your Docker registry:
- `backend.yaml` - change `image: your-registry/voca-recaller-backend:latest`
- `frontend.yaml` - change `image: your-registry/voca-recaller-frontend:latest`
- `celery-worker.yaml` - change `image: your-registry/voca-recaller-backend:latest`

### 2. Create Secrets
```bash
kubectl create secret generic voca-recaller-secrets \
  --namespace=voca-recaller \
  --from-literal=mysql-root-password='YourPassword' \
  --from-literal=database-password='YourPassword' \
  --from-literal=flask-secret-key='YourFlaskSecret' \
  --from-literal=jwt-secret-key='YourJWTSecret' \
  --from-literal=mail-password='YourEmailPassword' \
  --from-literal=mail-username='your-email@example.com'
```

### 3. Update ConfigMap
Edit `configmap.yaml`:
- `FRONTEND_URL`: Your actual domain
- `BACKEND_URL`: Your API URL
- `MAIL_SERVER`: Your SMTP server

### 4. Update Ingress
Edit `ingress.yaml`:
- Replace `your-domain.com` with your actual domain

## Helpful Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods -n voca-recaller'
alias kgs='kubectl get services -n voca-recaller'
alias kga='kubectl get all -n voca-recaller'
alias kl='kubectl logs -n voca-recaller'
alias kd='kubectl describe -n voca-recaller'
alias ke='kubectl exec -it -n voca-recaller'

# Usage examples:
# kgp              -> Get pods
# kl backend-xxx   -> View logs
# ke backend-xxx -- /bin/bash  -> Shell into pod
```

## Next Steps After Deployment

1. ✅ Test the application
2. ✅ Set up monitoring (Prometheus/Grafana)
3. ✅ Configure automated backups
4. ✅ Enable HTTPS (cert-manager)
5. ✅ Set up CI/CD pipeline
6. ✅ Configure autoscaling (HPA)
7. ✅ Set up alerting

## Resources

- Full guide: `docs/K8S_DEPLOYMENT.md`
- Kubernetes docs: https://kubernetes.io/docs/
- kubectl cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
