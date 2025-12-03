#!/bin/bash
# Test rapide de l'API

echo "=========================================="
echo "Test Rapide de l'API"
echo "=========================================="

API_URL="http://localhost:8000"

# Test health
echo -e "\n1. Health Check:"
curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/health"

# Test stations
echo -e "\n\n2. Stations:"
curl -s "$API_URL/api/stations" | python3 -m json.tool 2>/dev/null | head -15 || curl -s "$API_URL/api/stations" | head -15

# Test metrics
echo -e "\n\n3. Metrics:"
curl -s "$API_URL/api/metrics" | python3 -m json.tool 2>/dev/null | head -20 || curl -s "$API_URL/api/metrics" | head -20

# Test comparison
echo -e "\n\n4. Metrics Comparison:"
curl -s "$API_URL/api/metrics/comparison" | python3 -m json.tool 2>/dev/null | head -20 || curl -s "$API_URL/api/metrics/comparison" | head -20

# Test advanced metrics
echo -e "\n\n5. Advanced Metrics:"
curl -s "$API_URL/api/metrics/advanced" | python3 -m json.tool 2>/dev/null | head -15 || curl -s "$API_URL/api/metrics/advanced" | head -15

# Test physics validation
echo -e "\n\n6. Physics Validation:"
curl -s "$API_URL/api/validation/physics" | python3 -m json.tool 2>/dev/null | head -20 || curl -s "$API_URL/api/validation/physics" | head -20

echo -e "\n\n=========================================="
echo "Tests terminés"
echo "=========================================="

