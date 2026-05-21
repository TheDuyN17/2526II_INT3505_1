#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p bin

KIND_VERSION="${KIND_VERSION:-v0.23.0}"
KUBECTL_VERSION="${KUBECTL_VERSION:-v1.30.2}"
ARCH="$(uname -m)"

case "$ARCH" in
  x86_64)
    KIND_ARCH=amd64
    KUBECTL_ARCH=amd64
    ;;
  aarch64 | arm64)
    KIND_ARCH=arm64
    KUBECTL_ARCH=arm64
    ;;
  *)
    echo "Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

if [ ! -x bin/kind ]; then
  curl -Lo bin/kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${KIND_ARCH}"
  chmod +x bin/kind
fi

if [ ! -x bin/kubectl ]; then
  curl -Lo bin/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${KUBECTL_ARCH}/kubectl"
  chmod +x bin/kubectl
fi

cat <<INFO
Installed local Kubernetes tools:
  $(pwd)/bin/kind
  $(pwd)/bin/kubectl

Use them in this shell:
  export PATH="$(pwd)/bin:$PATH"
INFO

