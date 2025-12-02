#!/bin/bash
# Script to run before committing
# Validates all implementations and ensures code quality

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=" * 60
echo "Pre-Commit Validation"
echo "=" * 60

# Run all structure tests
echo ""
echo "Running test suite..."
python3 scripts/tests/test_all_days_1_4.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All tests passed! Safe to commit."
    exit 0
else
    echo ""
    echo "❌ Tests failed! Please fix issues before committing."
    exit 1
fi

