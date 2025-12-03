#!/bin/bash
# Script pour exécuter tous les tests du projet

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GenHack 2025 - Tests Complets${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Vertex"
FRONTEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Frontend"

# Counters
PASSED=0
FAILED=0
TOTAL=0

# Function to run test and count results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    TOTAL=$((TOTAL + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Backend Tests
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  BACKEND TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$BACKEND_DIR"

# Test 1: All structure tests
run_test "Backend Structure Tests" "python3 scripts/tests/test_all_days_1_4.py"

# Test 2: Syntax validation
run_test "Python Syntax Validation" "python3 scripts/tests/test_syntax.py"

# Test 3: ETL Pipeline
run_test "ETL Pipeline Structure" "python3 scripts/tests/test_etl_simple.py"

# Test 4: Gap Filling
run_test "Gap Filling Structure" "python3 scripts/tests/test_gap_filling_simple.py"

# Test 5: Baseline Model
run_test "Baseline Model Structure" "python3 scripts/tests/test_baseline_simple.py"

# Test 6: GADM Indicators
run_test "GADM Indicators Structure" "python3 scripts/tests/test_gadm_simple.py"

# Test 7: Prithvi Setup
run_test "Prithvi Setup Structure" "python3 scripts/tests/test_prithvi_simple.py"

# Test 8: Dataset Preparation
run_test "Dataset Preparation Structure" "python3 scripts/tests/test_dataset_prep_simple.py"

# Test 9: Fine-Tuning
run_test "Fine-Tuning Structure" "python3 scripts/tests/test_finetuning_simple.py"

# Test 10: Model Analysis
run_test "Model Analysis Structure" "python3 scripts/tests/test_model_analysis_simple.py"

# Test 11: Advanced Metrics
run_test "Advanced Metrics Structure" "python3 scripts/tests/test_advanced_metrics_simple.py"

# Test 12: Physics Validation
run_test "Physics Validation Structure" "python3 scripts/tests/test_physics_validation_simple.py"

# Test 13: Product Generation
run_test "Product Generation Structure" "python3 scripts/tests/test_product_generation_simple.py"

# Test 14: Export Results
run_test "Export Results Structure" "python3 scripts/tests/test_export_results_simple.py"

# Frontend Tests
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FRONTEND TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$FRONTEND_DIR"

# Test 15: Build
run_test "Frontend Build" "npm run build"

# Test 16: TypeScript Compilation
run_test "TypeScript Compilation" "npm run build 2>&1 | grep -q 'built in'"

# Test 17: Performance Script
if [ -f "scripts/test_performance.sh" ]; then
    run_test "Performance Tests" "bash scripts/test_performance.sh"
fi

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\nTotal Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi

