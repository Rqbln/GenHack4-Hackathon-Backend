#!/bin/bash
# Test runner script that uses virtual environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Using virtual environment: $(which python)"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Run test suite
python3 scripts/tests/test_all_days_1_4.py

