#!/usr/bin/env bash
# extract-usage.sh — Quartermaster usage manifest generator
# Delegates to extract-usage.py (pure Python, no dependencies)
# Place this file at: [YOUR_WORKSPACE]/quartermaster/extract-usage.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/extract-usage.py"
