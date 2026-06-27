#!/usr/bin/env bash
# read-only: checks Go version and prints which mistake categories apply
# Usage: bash <skill-dir>/scripts/check-go-version.sh [go.mod path]
set -euo pipefail

GOMOD="${1:-go.mod}"

if [[ ! -f "$GOMOD" ]]; then
  echo "INFO: No go.mod found at '$GOMOD'; skipping version check." >&2
  exit 0
fi

VERSION=$(grep -m1 '^go ' "$GOMOD" | awk '{print $2}')

if [[ -z "$VERSION" ]]; then
  echo "ERROR: Could not parse Go version from $GOMOD" >&2
  exit 1
fi

MAJOR=$(echo "$VERSION" | cut -d. -f1)
MINOR=$(echo "$VERSION" | cut -d. -f2)

echo "Go version: $VERSION"

# Emit version-sensitive notes
if [[ "$MINOR" -lt 18 ]]; then
  echo "NOTE: Generics (#9) not available before Go 1.18"
fi

if [[ "$MINOR" -lt 20 ]]; then
  echo "NOTE: strings.Clone (#41) not available before Go 1.20"
fi

if [[ "$MINOR" -lt 21 ]]; then
  echo "NOTE: context.WithoutCancel (#61) not available before Go 1.21"
fi

if [[ "$MINOR" -lt 22 ]]; then
  echo "NOTE: Loop variable per-iteration capture (#63) requires Go 1.22+"
fi
