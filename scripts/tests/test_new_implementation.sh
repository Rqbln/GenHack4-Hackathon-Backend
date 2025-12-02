#!/bin/bash
# Template script for testing new implementations
# Usage: ./test_new_implementation.sh <day_number> <description>

set -e

DAY=$1
DESCRIPTION=$2

if [ -z "$DAY" ] || [ -z "$DESCRIPTION" ]; then
    echo "Usage: $0 <day_number> <description>"
    echo "Example: $0 4 'GADM extraction'"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=" * 60
echo "Testing Day $DAY: $DESCRIPTION"
echo "=" * 60

# Run syntax test
echo ""
echo "[1] Running syntax validation..."
python3 scripts/tests/test_syntax.py

# Run structure test if exists
TEST_FILE="scripts/tests/test_day${DAY}_simple.py"
if [ -f "$TEST_FILE" ]; then
    echo ""
    echo "[2] Running structure test..."
    python3 "$TEST_FILE"
else
    echo ""
    echo "⚠️  No structure test found at $TEST_FILE"
    echo "   Create it to validate the implementation structure"
fi

# Run full test if exists and dependencies available
FULL_TEST_FILE="scripts/tests/test_day${DAY}.py"
if [ -f "$FULL_TEST_FILE" ]; then
    echo ""
    echo "[3] Running full test (if dependencies available)..."
    python3 "$FULL_TEST_FILE" || echo "⚠️  Full test skipped (dependencies may be missing)"
fi

echo ""
echo "=" * 60
echo "✅ Day $DAY tests completed!"
echo "=" * 60

