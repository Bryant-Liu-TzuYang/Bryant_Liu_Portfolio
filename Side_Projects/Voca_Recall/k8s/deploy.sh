#!/bin/bash

# ============================================================
# Kubernetes Deployment Script for Voca_Recaller
# ============================================================
# This script deploys all components in the correct order
# Make sure you've updated the configuration files first!
# ============================================================

set -e  # Exit on any error

NAMESPACE="voca-recaller"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BOLD}=== $1 ===${NC}\n"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_header "Starting Voca_Recaller Deployment"

# 1. Create namespace
print_info "Creating namespace..."
kubectl apply -f k8s/namespace.yaml
sleep 2

# 2. Check if secrets exist, if not create them
print_info "Checking secrets..."
if kubectl get secret voca-recaller-secrets -n $NAMESPACE &> /dev/null; then
    print_warning "Secret 'voca-recaller-secrets' already exists. Skipping..."
else
    print_warning "Secret 'voca-recaller-secrets' not found!"
    echo "Please create secrets using one of these methods:"
    echo "  1. kubectl apply -f k8s/secret.yaml (if you updated it)"
    echo "  2. kubectl create secret generic (see K8S_DEPLOYMENT.md)"
    read -p "Have you created the secrets? (yes/no): " answer
    if [ "$answer" != "yes" ]; then
        print_error "Deployment cancelled. Please create secrets first."
        exit 1
    fi
fi

# 3. Create ConfigMaps
print_info "Creating ConfigMaps..."
kubectl apply -f k8s/configmap.yaml
sleep 2

# 4. Create PersistentVolumeClaim for MySQL
print_info "Creating persistent storage for MySQL..."
kubectl apply -f k8s/mysql-pvc.yaml
sleep 2

print_info "Waiting for PVC to be bound..."
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/mysql-pvc -n $NAMESPACE --timeout=120s || {
    print_warning "PVC is not bound yet. Continuing anyway..."
}

# 5. Deploy MySQL
print_header "Deploying MySQL Database"
kubectl apply -f k8s/mysql.yaml
sleep 5

print_info "Waiting for MySQL to be ready (this may take a minute)..."
kubectl wait --for=condition=ready pod -l app=mysql -n $NAMESPACE --timeout=180s || {
    print_error "MySQL pod is not ready. Check logs with: kubectl logs -n $NAMESPACE -l app=mysql"
    exit 1
}
print_info "✓ MySQL is ready!"

# 6. Deploy Redis
print_header "Deploying Redis"
kubectl apply -f k8s/redis.yaml
sleep 5

print_info "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=120s || {
    print_error "Redis pod is not ready. Check logs with: kubectl logs -n $NAMESPACE -l app=redis"
    exit 1
}
print_info "✓ Redis is ready!"

# 7. Deploy Backend
print_header "Deploying Backend"
kubectl apply -f k8s/backend.yaml
sleep 5

print_info "Waiting for backend pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=180s || {
    print_warning "Backend pods are not ready yet. Check logs with: kubectl logs -n $NAMESPACE -l app=backend"
}

# 8. Deploy Celery Workers
print_header "Deploying Celery Workers"
kubectl apply -f k8s/celery-worker.yaml
sleep 5

print_info "Waiting for Celery workers to be ready..."
kubectl wait --for=condition=ready pod -l app=celery-worker -n $NAMESPACE --timeout=120s || {
    print_warning "Celery worker pods are not ready yet. Check logs with: kubectl logs -n $NAMESPACE -l app=celery-worker"
}

# 9. Deploy Frontend
print_header "Deploying Frontend"
kubectl apply -f k8s/frontend.yaml
sleep 5

print_info "Waiting for frontend pods to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=120s || {
    print_warning "Frontend pods are not ready yet. Check logs with: kubectl logs -n $NAMESPACE -l app=frontend"
}

# 10. Deploy Ingress
print_header "Deploying Ingress"
print_warning "Make sure you have an Ingress controller installed!"
echo "If not, install nginx-ingress:"
echo "  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml"
read -p "Continue with Ingress deployment? (yes/no): " answer
if [ "$answer" == "yes" ]; then
    kubectl apply -f k8s/ingress.yaml
    print_info "✓ Ingress deployed"
else
    print_warning "Skipping Ingress deployment"
fi

# Summary
print_header "Deployment Summary"
echo ""
kubectl get pods -n $NAMESPACE
echo ""
kubectl get services -n $NAMESPACE
echo ""
kubectl get ingress -n $NAMESPACE
echo ""

print_info "Deployment completed!"
echo ""
print_info "Useful commands:"
echo "  View all resources:  kubectl get all -n $NAMESPACE"
echo "  View logs:           kubectl logs -n $NAMESPACE -l app=backend -f"
echo "  Shell into pod:      kubectl exec -it POD-NAME -n $NAMESPACE -- /bin/bash"
echo "  Port forward:        kubectl port-forward -n $NAMESPACE service/backend 5000:5000"
echo ""
print_info "Check the K8S_DEPLOYMENT.md guide for more details!"
