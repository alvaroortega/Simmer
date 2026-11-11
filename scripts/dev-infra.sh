#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! docker info >/dev/null 2>&1; then
  echo "Starting Colima..."
  colima start
fi

docker info >/dev/null

docker-compose up -d --wait --wait-timeout 90 postgres