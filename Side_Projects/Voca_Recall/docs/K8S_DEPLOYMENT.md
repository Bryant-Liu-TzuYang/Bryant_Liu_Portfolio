# Kubernetes Deployment Guide for Voca_Recaller

This guide will help you deploy Voca_Recaller to a Kubernetes cluster on Ubuntu. This is a beginner-friendly guide with detailed explanations.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Understanding Kubernetes Basics](#understanding-kubernetes-basics)
3. [Preparing Your Application](#preparing-your-application)
4. [Deploying to Kubernetes](#deploying-to-kubernetes)
5. [Accessing Your Application](#accessing-your-application)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
7. [Scaling and Updates](#scaling-and-updates)
8. [Production Best Practices](#production-best-practices)

---

## Prerequisites

### 1. Ubuntu Server Setup
```bash
# Update your system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

### 2. Install Kubernetes (k3s - lightweight K8s for single server)
```bash
# Install k3s (easy Kubernetes distribution)
curl -sfL https://get.k3s.io | sh -

# Check if k3s is running
sudo systemctl status k3s

# Make kubectl usable without sudo
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc

# Verify Kubernetes is working
kubectl get nodes
# You should see your node in "Ready" state
```

**Alternative: Use kubeadm, minikube, or managed Kubernetes (EKS, GKE, AKS)**

### 3. Install kubectl (if not using k3s)
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

---

## Understanding Kubernetes Basics

### Key Concepts (Explained Simply)

**1. Pod**
- The smallest unit in Kubernetes
- Think of it as a "wrapper" around one or more containers
- Your Flask app runs in a pod

**2. Deployment**
- Manages pods and ensures the desired number are running
- Automatically restarts failed pods
- Handles updates without downtime

**3. Service**
- A stable network endpoint to access pods
- Like a "phone number" that doesn't change even if pods restart
- Load balances traffic across multiple pods

**4. ConfigMap**
- Stores non-sensitive configuration (URLs, feature flags)
- Like environment variables

**5. Secret**
- Stores sensitive data (passwords, API keys)
- Base64 encoded (not encrypted by default!)

**6. Ingress**
- Routes external traffic to your services
- Like a reverse proxy or load balancer
- Can handle SSL/HTTPS

**7. Namespace**
- A "folder" to organize resources
- Keeps your app separate from others

**8. PersistentVolumeClaim (PVC)**
- Requests storage for data that survives pod restarts
- Essential for databases

---

## Preparing Your Application

### 1. Build and Push Docker Images

You need to build Docker images for your backend and frontend, then push them to a registry.

**Option A: Use Docker Hub (easiest for beginners)**
```bash
# Login to Docker Hub
docker login

# Build backend image
cd backend
docker build -t YOUR-DOCKERHUB-USERNAME/voca-recaller-backend:latest .
docker push YOUR-DOCKERHUB-USERNAME/voca-recaller-backend:latest

# Build frontend image
cd ../frontend
docker build -t YOUR-DOCKERHUB-USERNAME/voca-recaller-frontend:latest .
docker push YOUR-DOCKERHUB-USERNAME/voca-recaller-frontend:latest
```

**Option B: Use a private registry**
```bash
# Set up a local registry (for testing)
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# Build and push to local registry
docker build -t localhost:5000/voca-recaller-backend:latest ./backend
docker push localhost:5000/voca-recaller-backend:latest

docker build -t localhost:5000/voca-recaller-frontend:latest ./frontend
docker push localhost:5000/voca-recaller-frontend:latest
```

### 2. Update Kubernetes Configuration Files

**Update image names in:**
- `k8s/backend.yaml` - line with `image: your-registry/voca-recaller-backend:latest`
- `k8s/frontend.yaml` - line with `image: your-registry/voca-recaller-frontend:latest`
- `k8s/celery-worker.yaml` - line with `image: your-registry/voca-recaller-backend:latest`

Replace `your-registry` with your actual Docker Hub username or registry URL.

### 3. Configure Secrets

**Generate secure secrets:**
```bash
# Generate a random Flask secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Encode secrets to base64
echo -n "your-mysql-password" | base64
echo -n "your-flask-secret-key" | base64
echo -n "your-jwt-secret" | base64
echo -n "your-email@gmail.com" | base64
echo -n "your-email-password" | base64
```

**Create secret using kubectl (recommended - more secure):**
```bash
kubectl create secret generic voca-recaller-secrets \
  --namespace=voca-recaller \
  --from-literal=mysql-root-password='YourSecurePassword123!' \
  --from-literal=database-password='YourDbPassword123!' \
  --from-literal=flask-secret-key='your-generated-flask-secret' \
  --from-literal=jwt-secret-key='your-generated-jwt-secret' \
  --from-literal=mail-password='your-email-password' \
  --from-literal=mail-username='your-email@gmail.com'
```

**OR edit `k8s/secret.yaml` with your base64-encoded values.**

### 4. Update ConfigMap

Edit `k8s/configmap.yaml` and update:
- `FRONTEND_URL`: Your domain (e.g., `https://voca-recaller.com`)
- `BACKEND_URL`: Your API URL (e.g., `https://voca-recaller.com/api`)
- `MAIL_SERVER`, `MAIL_PORT`: Your SMTP settings

---

## Deploying to Kubernetes

### Step-by-Step Deployment

**1. Create the namespace first:**
```bash
kubectl apply -f k8s/namespace.yaml
```

**2. Create secrets (if you didn't use kubectl create above):**
```bash
# Only if you edited secret.yaml file
kubectl apply -f k8s/secret.yaml
```

**3. Create ConfigMaps:**
```bash
kubectl apply -f k8s/configmap.yaml
```

**4. Create persistent storage for MySQL:**
```bash
kubectl apply -f k8s/mysql-pvc.yaml

# Check if PVC is created
kubectl get pvc -n voca-recaller
# Status should be "Bound" (may take a moment)
```

**5. Deploy database (MySQL):**
```bash
kubectl apply -f k8s/mysql.yaml

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql -n voca-recaller --timeout=120s

# Check MySQL pod status
kubectl get pods -n voca-recaller
```

**6. Deploy Redis:**
```bash
kubectl apply -f k8s/redis.yaml

# Wait for Redis
kubectl wait --for=condition=ready pod -l app=redis -n voca-recaller --timeout=60s
```

**7. Deploy backend:**
```bash
kubectl apply -f k8s/backend.yaml

# Check backend pods
kubectl get pods -n voca-recaller -l app=backend
```

**8. Deploy Celery workers:**
```bash
kubectl apply -f k8s/celery-worker.yaml
```

**9. Deploy frontend:**
```bash
kubectl apply -f k8s/frontend.yaml
```

**10. Set up Ingress (external access):**

First, install an Ingress controller (nginx example):
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

Update your domain in `k8s/ingress.yaml`, then:
```bash
kubectl apply -f k8s/ingress.yaml
```

### All-in-One Deployment (After Preparing)
```bash
# Deploy everything in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml  # Or create via kubectl
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/mysql-pvc.yaml
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/celery-worker.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## Accessing Your Application

### Get Your Application URL

**1. Check Ingress IP:**
```bash
kubectl get ingress -n voca-recaller

# You'll see an ADDRESS column with an IP or hostname
```

**2. Point your domain to that IP:**
- Go to your domain registrar (GoDaddy, Namecheap, etc.)
- Add an A record pointing to the Ingress IP
- Example: `A record: @ -> 203.0.113.42`

**3. For testing without a domain:**
```bash
# Add to /etc/hosts on your local machine
sudo nano /etc/hosts
# Add line: 203.0.113.42 your-domain.com
```

**4. If using LoadBalancer instead of Ingress:**
```bash
kubectl get services -n voca-recaller
# Look for EXTERNAL-IP of your LoadBalancer services
```

---

## Monitoring and Troubleshooting

### Essential Commands

**View all resources:**
```bash
kubectl get all -n voca-recaller
```

**Check pod status:**
```bash
kubectl get pods -n voca-recaller

# Show more details
kubectl get pods -n voca-recaller -o wide
```

**View pod logs:**
```bash
# Backend logs
kubectl logs -n voca-recaller -l app=backend --tail=100

# Follow logs in real-time
kubectl logs -n voca-recaller -l app=backend -f

# Specific pod
kubectl logs -n voca-recaller POD-NAME

# Previous pod logs (if it crashed)
kubectl logs -n voca-recaller POD-NAME --previous
```

**Describe a resource (detailed info):**
```bash
kubectl describe pod POD-NAME -n voca-recaller
kubectl describe service backend -n voca-recaller
```

**Execute commands inside a pod:**
```bash
# Shell into a pod
kubectl exec -it POD-NAME -n voca-recaller -- /bin/bash

# Run a single command
kubectl exec -it POD-NAME -n voca-recaller -- ls /app
```

**Check events (useful for debugging):**
```bash
kubectl get events -n voca-recaller --sort-by='.lastTimestamp'
```

### Common Issues

**1. Pods stuck in "Pending":**
```bash
# Check why
kubectl describe pod POD-NAME -n voca-recaller

# Common causes:
# - Insufficient resources (CPU/memory)
# - PVC not bound
# - Node selector mismatch
```

**2. Pods in "CrashLoopBackOff":**
```bash
# View logs to see the error
kubectl logs POD-NAME -n voca-recaller --previous

# Common causes:
# - Application error (check logs)
# - Missing environment variables
# - Database connection issues
```

**3. Can't access the application:**
```bash
# Check if pods are running
kubectl get pods -n voca-recaller

# Check if services exist
kubectl get services -n voca-recaller

# Check ingress
kubectl get ingress -n voca-recaller

# Test backend directly (port-forward)
kubectl port-forward -n voca-recaller service/backend 5000:5000
# Then visit http://localhost:5000
```

**4. Database connection errors:**
```bash
# Check MySQL is running
kubectl get pods -n voca-recaller -l app=mysql

# Check MySQL logs
kubectl logs -n voca-recaller -l app=mysql

# Test MySQL connection from backend pod
kubectl exec -it BACKEND-POD-NAME -n voca-recaller -- mysql -h mysql -u root -p
```

---

## Scaling and Updates

### Scaling

**Scale pods horizontally (more replicas):**
```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n voca-recaller

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=4 -n voca-recaller

# Check scaling
kubectl get pods -n voca-recaller
```

### Updating Your Application

**1. Build and push new image:**
```bash
docker build -t YOUR-USERNAME/voca-recaller-backend:v2 ./backend
docker push YOUR-USERNAME/voca-recaller-backend:v2
```

**2. Update deployment:**
```bash
# Method 1: Update the image directly
kubectl set image deployment/backend backend=YOUR-USERNAME/voca-recaller-backend:v2 -n voca-recaller

# Method 2: Edit deployment file and apply
# Edit k8s/backend.yaml to change image tag, then:
kubectl apply -f k8s/backend.yaml

# Watch the rollout
kubectl rollout status deployment/backend -n voca-recaller
```

**3. Rollback if something goes wrong:**
```bash
# Undo last rollout
kubectl rollout undo deployment/backend -n voca-recaller

# Rollback to specific revision
kubectl rollout history deployment/backend -n voca-recaller
kubectl rollout undo deployment/backend --to-revision=2 -n voca-recaller
```

---

## Production Best Practices

### 1. Security

**Use proper secret management:**
```bash
# Install Sealed Secrets (encrypts secrets in git)
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Or use cloud provider secret managers:
# - AWS Secrets Manager
# - Google Secret Manager
# - Azure Key Vault
```

**Enable HTTPS:**
```bash
# Install cert-manager for automatic SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt issuer (k8s/cert-issuer.yaml)
# See: https://cert-manager.io/docs/tutorials/acme/ingress/
```

**Network Policies:**
Create network policies to restrict pod-to-pod communication.

### 2. Backups

**Backup MySQL data regularly:**
```bash
# Create a CronJob for automated backups
# Example: k8s/mysql-backup-cronjob.yaml
```

**Backup commands:**
```bash
# Manual backup
kubectl exec -n voca-recaller MYSQL-POD -- mysqldump -u root -p$MYSQL_ROOT_PASSWORD voca_recaller > backup.sql

# Restore
kubectl exec -i -n voca-recaller MYSQL-POD -- mysql -u root -p$MYSQL_ROOT_PASSWORD voca_recaller < backup.sql
```

### 3. Monitoring

**Install monitoring tools:**
```bash
# Prometheus + Grafana (popular choice)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Or use cloud provider monitoring
# - AWS CloudWatch
# - Google Cloud Monitoring
# - Azure Monitor
```

**View resource usage:**
```bash
# Install metrics-server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View pod resources
kubectl top pods -n voca-recaller
kubectl top nodes
```

### 4. Logging

**Centralized logging:**
```bash
# ELK Stack (Elasticsearch, Logstash, Kibana)
# Or Loki + Grafana
# Or cloud provider logging services
```

### 5. High Availability

- Run multiple replicas of each service
- Use pod anti-affinity to spread pods across nodes
- Set up database replication (MySQL master-slave)
- Use autoscaling (HPA - Horizontal Pod Autoscaler)

**Example HPA:**
```bash
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10 -n voca-recaller
```

---

## Quick Reference

### Useful Commands Cheat Sheet

```bash
# View everything
kubectl get all -n voca-recaller

# Logs
kubectl logs -f -n voca-recaller -l app=backend

# Shell into pod
kubectl exec -it POD-NAME -n voca-recaller -- /bin/bash

# Port forward for testing
kubectl port-forward -n voca-recaller service/backend 5000:5000

# Delete and recreate
kubectl delete -f k8s/backend.yaml
kubectl apply -f k8s/backend.yaml

# Restart deployment (recreate all pods)
kubectl rollout restart deployment/backend -n voca-recaller

# Check resource usage
kubectl top pods -n voca-recaller

# View events
kubectl get events -n voca-recaller --sort-by='.lastTimestamp'

# Delete everything
kubectl delete namespace voca-recaller
```

---

## Next Steps

1. **Test your deployment thoroughly**
2. **Set up monitoring and alerting**
3. **Configure automated backups**
4. **Enable HTTPS with cert-manager**
5. **Set up CI/CD pipeline** (GitHub Actions, GitLab CI, Jenkins)
6. **Document your specific configuration**
7. **Plan for disaster recovery**

## Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [Kubernetes Patterns Book](https://www.oreilly.com/library/view/kubernetes-patterns/9781492050278/)
- [k3s Documentation](https://docs.k3s.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Need Help?** 
- Check pod logs first: `kubectl logs -n voca-recaller POD-NAME`
- Describe resources: `kubectl describe pod POD-NAME -n voca-recaller`
- Check events: `kubectl get events -n voca-recaller`

Good luck with your deployment! 🚀
