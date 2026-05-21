#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-lecture-10}"
IMAGE_NAME="${IMAGE_NAME:-lecture-10-api:local}"

cd "$(dirname "$0")/.."

export PATH="$(pwd)/bin:$PATH"

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is required. Install kind first: https://kind.sigs.k8s.io/docs/user/quick-start/"
  exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required. Install kubectl first: https://kubernetes.io/docs/tasks/tools/"
  exit 1
fi

if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
  kind create cluster --name "$CLUSTER_NAME" --config kind-config.yaml
fi

docker build -t "$IMAGE_NAME" .
kind load docker-image "$IMAGE_NAME" --name "$CLUSTER_NAME"

kubectl apply -f k8s/observability
kubectl apply -f k8s/app

kubectl -n lecture-10 rollout restart deployment/lecture-10-api

kubectl -n lecture-10 rollout status deployment/lecture-10-api
kubectl -n observability rollout status deployment/prometheus
kubectl -n observability rollout status deployment/grafana
kubectl -n observability rollout status deployment/tempo
kubectl -n observability rollout status deployment/otel-collector

cat <<INFO

Kubernetes demo is ready.

API:        http://127.0.0.1:8080
Prometheus: http://127.0.0.1:19090
Grafana:    http://127.0.0.1:3000

Grafana login:
  username: admin
  password: admin

INFO
