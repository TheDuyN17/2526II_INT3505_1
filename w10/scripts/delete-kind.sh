#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-lecture-10}"

cd "$(dirname "$0")/.."
export PATH="$(pwd)/bin:$PATH"

kind delete cluster --name "$CLUSTER_NAME"
