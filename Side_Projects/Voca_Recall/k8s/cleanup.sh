#!/bin/bash

# ============================================================
# Kubernetes Cleanup Script for Voca_Recaller
# ============================================================
# This script removes all Voca_Recaller resources from the cluster
# Use with caution! This will delete everything including data!
# ============================================================

set -e

NAMESPACE="voca-recaller"
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${RED}WARNING: This will delete ALL Voca_Recaller resources!${NC}"
echo -e "${YELLOW}This includes:${NC}"
echo "  - All pods (backend, frontend, celery, database)"
echo "  - All services"
echo "  - Persistent data (database contents will be LOST!)"
echo "  - ConfigMaps and Secrets"
echo "  - The entire namespace"
echo ""
read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirmation

if [ "$confirmation" != "DELETE" ]; then
    echo -e "${GREEN}Cleanup cancelled. No resources were deleted.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Starting cleanup...${NC}"

# Delete in reverse order
echo "Deleting Ingress..."
kubectl delete -f k8s/ingress.yaml --ignore-not-found=true

echo "Deleting Frontend..."
kubectl delete -f k8s/frontend.yaml --ignore-not-found=true

echo "Deleting Celery Workers..."
kubectl delete -f k8s/celery-worker.yaml --ignore-not-found=true

echo "Deleting Backend..."
kubectl delete -f k8s/backend.yaml --ignore-not-found=true

echo "Deleting Redis..."
kubectl delete -f k8s/redis.yaml --ignore-not-found=true

echo "Deleting MySQL..."
kubectl delete -f k8s/mysql.yaml --ignore-not-found=true

echo "Deleting PVC (this will delete database data)..."
kubectl delete -f k8s/mysql-pvc.yaml --ignore-not-found=true

echo "Deleting ConfigMap..."
kubectl delete -f k8s/configmap.yaml --ignore-not-found=true

echo "Deleting Secrets..."
kubectl delete -f k8s/secret.yaml --ignore-not-found=true

echo "Deleting Namespace..."
kubectl delete -f k8s/namespace.yaml --ignore-not-found=true

echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
echo "The namespace may take a few moments to fully terminate."
echo ""
echo "Check status with: kubectl get namespace $NAMESPACE"
