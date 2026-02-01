# Kubernetes for Absolute Beginners

## Table of Contents
- [What is Kubernetes (k8s)?](#what-is-kubernetes-k8s)
  - [Why Use Kubernetes Instead of Docker Compose?](#why-use-kubernetes-instead-of-docker-compose)
- [Key Concepts Explained Simply](#key-concepts-explained-simply)
  - [1. Cluster](#1-cluster)
  - [2. Pod](#2-pod)
  - [3. Deployment](#3-deployment)
  - [4. Service](#4-service)
  - [5. ConfigMap](#5-configmap)
  - [6. Secret](#6-secret)
  - [7. Ingress](#7-ingress)
  - [8. Namespace](#8-namespace)
  - [9. PersistentVolumeClaim (PVC)](#9-persistentvolumeclaim-pvc)
- [How They Work Together](#how-they-work-together)
- [Your Deployment Flow](#your-deployment-flow)
  - [Step 1: Prepare](#step-1-prepare)
  - [Step 2: Configure](#step-2-configure)
  - [Step 3: Deploy](#step-3-deploy)
  - [Step 4: Verify](#step-4-verify)
  - [Step 5: Access](#step-5-access)
- [Common Commands You'll Use](#common-commands-youll-use)

## What is Kubernetes (k8s)?

Think of Kubernetes as a **smart manager** for your Docker containers. Just like Docker Compose manages multiple containers on one machine, Kubernetes manages containers across **multiple machines** and makes sure they stay running.

### Why Use Kubernetes Instead of Docker Compose?

| Docker Compose | Kubernetes |
|----------------|------------|
| Single server | Multiple servers (cluster) |
| Manual restart if server crashes | Automatic failover |
| Manual scaling | Automatic scaling |
| No load balancing | Built-in load balancing |
| Good for development | Production-ready |

## Key Concepts Explained Simply

### 1. **Cluster**
A cluster is a group of servers (called nodes) working together.

```
Your Kubernetes Cluster
┌─────────────────────────────────────┐
│  Master Node (Control Plane)       │  <- The brain
│  - Manages everything               │
│  - Makes decisions                  │
└─────────────────────────────────────┘
          │
          ├─────────────────┬─────────────────┐
          │                 │                 │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │  Worker   │    │  Worker   │    │  Worker   │
    │  Node 1   │    │  Node 2   │    │  Node 3   │
    │           │    │           │    │           │
    │ [Pods]    │    │ [Pods]    │    │ [Pods]    │
    └───────────┘    └───────────┘    └───────────┘
```

For beginners, you can start with a **single-node cluster** (one server that acts as both master and worker).

### 2. **Pod**
The smallest unit in Kubernetes. A pod wraps one or more containers.

```
┌─────────────────┐
│      Pod        │
│  ┌───────────┐  │
│  │ Container │  │  <- Your Flask app
│  │  (Flask)  │  │
│  └───────────┘  │
└─────────────────┘
```

Think of a pod as a "wrapper" that adds Kubernetes superpowers to your container:
- Automatic restarts if it crashes
- Health checks
- Resource limits
- Networking

### 3. **Deployment**
A Deployment ensures a specific number of pod copies are always running.

```
┌──────────────────────────────────────┐
│         Deployment (Backend)         │
│  "Keep 3 backend pods running"       │
└──────────────────────────────────────┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼─┐  ┌──▼──┐  ┌─▼───┐
│Pod 1│  │Pod 2│  │Pod 3│  <- All running your Flask app
└─────┘  └─────┘  └─────┘

If Pod 2 crashes → Kubernetes automatically creates a new Pod 2
```

**Why it's useful:**
- **High Availability**: If one pod crashes, others keep serving requests
- **Zero-Downtime Updates**: Deploy new versions without stopping the app
- **Easy Scaling**: `kubectl scale deployment backend --replicas=10`

### 4. **Service**
A Service gives your pods a stable address (like a permanent phone number).

```
Without Service:
  Frontend → 10.0.0.5 (Pod 1)  <- Pod restarts, new IP: 10.0.0.8
  Oops! Frontend can't find backend anymore ❌

With Service:
  Frontend → backend.voca-recaller (Service)
                   ↓
             ┌─────┼─────┐
             │     │     │
          Pod 1  Pod 2  Pod 3
  
  Service always available, even if pods change ✅
  Also load balances between pods!
```

### 5. **ConfigMap**
Stores configuration that's NOT secret.

```yaml
ConfigMap:
  DATABASE_HOST: mysql
  DATABASE_PORT: 3306
  REDIS_HOST: redis
  LOG_LEVEL: INFO
```

Why use it?
- ✅ Change config without rebuilding Docker images
- ✅ Same image works in dev, staging, production (different ConfigMaps)
- ✅ Easy to see and update configuration

### 6. **Secret**
Like ConfigMap, but for sensitive data (passwords, API keys).

```yaml
Secret:
  database-password: cGFzc3dvcmQxMjM=  # base64 encoded
  jwt-secret-key: c2VjcmV0a2V5NDU2
```

**Important:** Secrets are only base64 encoded (NOT encrypted by default!). In production, use proper secret management tools.

### 7. **Ingress**
Routes external traffic to your services (like nginx or Apache as a reverse proxy).

```
Internet
   │
   ▼
┌─────────────────────┐
│    Ingress          │  <- Smart router
│  your-domain.com    │
└─────────────────────┘
   │              │
   │              └──────────────┐
   ▼                             ▼
/api routes              / (everything else)
   │                             │
   ▼                             ▼
┌─────────┐              ┌──────────┐
│ Backend │              │ Frontend │
│ Service │              │ Service  │
└─────────┘              └──────────┘
```

**Features:**
- Host-based routing (api.example.com vs www.example.com)
- Path-based routing (/api → backend, / → frontend)
- SSL/TLS termination (HTTPS)
- Load balancing

### 8. **Namespace**
A "folder" to organize resources.

```
Kubernetes Cluster
├── default (namespace)
├── kube-system (namespace)
└── voca-recaller (namespace)  <- Your app lives here
    ├── backend pods
    ├── frontend pods
    ├── mysql pod
    ├── services
    └── configmaps
```

**Why use namespaces?**
- ✅ Keep different apps separate
- ✅ Multiple environments (dev, staging, prod) in one cluster
- ✅ Resource quotas per namespace
- ✅ Easy to delete everything: `kubectl delete namespace voca-recaller`

### 9. **PersistentVolumeClaim (PVC)**
Requests storage that survives pod restarts (essential for databases).

```
Without PVC:
  MySQL pod stores data → Pod crashes → Data gone ❌

With PVC:
  MySQL pod → PVC → Actual disk storage
  Pod crashes → New pod → Mounts same PVC → Data still there ✅
```

## How They Work Together

Here's how all pieces fit for Voca_Recaller:

```
┌─────────────────────────────────────────────────────┐
│                  Namespace: voca-recaller            │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Internet                                            │
│     │                                                │
│     ▼                                                │
│  [Ingress] ─────────┬────────────────┐             │
│                     │                │             │
│                     ▼                ▼             │
│             [Frontend Service]  [Backend Service]   │
│                     │                │             │
│              ┌──────┼──────┐   ┌────┼─────┐       │
│              │      │      │   │    │     │       │
│           [Pod] [Pod] [Pod] [Pod] [Pod] [Pod]     │
│           Frontend x3      Backend x3               │
│                                │                    │
│                                ├─────────┬─────────┐│
│                                │         │         ││
│                                ▼         ▼         ▼│
│                         [MySQL Svc] [Redis Svc]  [Celery]│
│                              │         │                 │
│                           [MySQL]   [Redis]       [Workers]│
│                              │                           │
│                          [PVC: 10GB]                     │
│                          (Persistent                     │
│                           Database)                      │
│                                                          │
│  Configuration:                                          │
│  - ConfigMap (env vars)                                 │
│  - Secret (passwords)                                   │
└─────────────────────────────────────────────────────────┘
```

## Your Deployment Flow

### Step 1: Prepare
```bash
# Build Docker images
docker build -t your-username/voca-recaller-backend:latest ./backend
docker build -t your-username/voca-recaller-frontend:latest ./frontend

# Push to registry
docker push your-username/voca-recaller-backend:latest
docker push your-username/voca-recaller-frontend:latest
```

### Step 2: Configure
1. Update `configmap.yaml` with your settings
2. Create secrets with your passwords
3. Update image names in deployment files

### Step 3: Deploy
```bash
# Use the automated script
./k8s/deploy.sh

# Or manually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
# ... and so on
```

### Step 4: Verify
```bash
# Check if everything is running
kubectl get pods -n voca-recaller

# Expected output:
# NAME                             READY   STATUS    RESTARTS
# backend-xxx                      1/1     Running   0
# backend-yyy                      1/1     Running   0
# celery-worker-xxx                1/1     Running   0
# frontend-xxx                     1/1     Running   0
# mysql-0                          1/1     Running   0
# redis-xxx                        1/1     Running   0
```

### Step 5: Access
```bash
# Get your application URL
kubectl get ingress -n voca-recaller

# Point your domain to the ADDRESS shown
```

## Common Commands You'll Use

```bash
# See what's running
kubectl get all -n voca-recaller

# Check logs (find out why something broke)
kubectl logs -n voca-recaller POD-NAME

# Get a shell inside a pod (debug)
kubectl exec -it POD-NAME -n voca-recaller -- /bin/bash

# Restart everything (force new pods)
kubectl rollout restart deployment/backend -n voca-recaller

# Scale up
kubectl scale deployment backend --replicas=5 -n voca-recaller

# Update to new version
kubectl set image deployment/backend backend=your-image:v2 -n voca-recaller

# Delete everything
kubectl delete namespace voca-recaller
```

## Comparison: Docker Compose vs Kubernetes

Your current `docker-compose.yml`:
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
  mysql:
    image: mysql:8.0
  redis:
    image: redis:alpine
```

In Kubernetes, this becomes:
- `backend` → Deployment + Service
- `mysql` → StatefulSet + Service + PVC
- `redis` → Deployment + Service
- Plus: ConfigMap, Secret, Ingress, Namespace

More files, but you get:
- ✅ Automatic scaling
- ✅ Self-healing
- ✅ Load balancing
- ✅ Zero-downtime updates
- ✅ Works across multiple servers

## Next Steps

1. **Learn by doing**: Deploy on a test cluster
2. **Break things**: Delete pods and watch them recreate
3. **Check logs**: Practice debugging with kubectl logs
4. **Experiment**: Scale deployments up and down
5. **Read docs**: Official Kubernetes tutorials

## Resources for Beginners

- [Kubernetes Official Tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [k3s Quickstart](https://docs.k3s.io/quick-start) - Easiest way to get started
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Play with Kubernetes](https://labs.play-with-k8s.com/) - Free online playground

Remember: **Everyone finds Kubernetes confusing at first!** Start small, experiment, and it will click. 🚀
