#!/bin/bash
# Test complet de l'API

echo "=========================================="
echo "Test Complet de l'API GenHack 2025"
echo "=========================================="
echo

API_URL="http://localhost:8000"

# Test 1: Health Check
echo "1. Health Check:"
echo "   GET $API_URL/health"
response=$(curl -s "$API_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo "   ✅ API accessible"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "   ❌ API non accessible"
    echo "   Response: $response"
    exit 1
fi
echo

# Test 2: Metrics
echo "2. Metrics:"
echo "   GET $API_URL/api/metrics"
response=$(curl -s "$API_URL/api/metrics")
if echo "$response" | grep -q "baseline_metrics"; then
    echo "   ✅ Métriques chargées"
    echo "$response" | python3 -m json.tool 2>/dev/null | head -25
else
    echo "   ❌ Erreur lors du chargement des métriques"
    echo "   Response: $response"
fi
echo

# Test 3: Stations
echo "3. Stations:"
echo "   GET $API_URL/api/stations"
response=$(curl -s "$API_URL/api/stations")
if echo "$response" | grep -q "stations"; then
    echo "   ✅ Stations chargées"
    echo "$response" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "   ❌ Erreur lors du chargement des stations"
    echo "   Response: $response"
fi
echo

# Test 4: Metrics Comparison
echo "4. Metrics Comparison:"
echo "   GET $API_URL/api/metrics/comparison"
response=$(curl -s "$API_URL/api/metrics/comparison")
if echo "$response" | grep -q "baseline"; then
    echo "   ✅ Comparaison disponible"
    echo "$response" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "   ❌ Erreur lors du chargement de la comparaison"
    echo "   Response: $response"
fi
echo

# Test 5: Advanced Metrics
echo "5. Advanced Metrics:"
echo "   GET $API_URL/api/metrics/advanced"
response=$(curl -s "$API_URL/api/metrics/advanced")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo

# Test 6: Physics Validation
echo "6. Physics Validation:"
echo "   GET $API_URL/api/validation/physics"
response=$(curl -s "$API_URL/api/validation/physics")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo

# Test 7: Temperature Endpoint
echo "7. Temperature Endpoint:"
echo "   GET $API_URL/api/temperature?lat=48.8566&lon=2.3522&date=2020-01-01"
response=$(curl -s "$API_URL/api/temperature?lat=48.8566&lon=2.3522&date=2020-01-01")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo

# Test 8: CORS
echo "8. CORS Headers:"
response=$(curl -s -X OPTIONS "$API_URL/api/stations" \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: GET" \
    -i 2>&1 | grep -i "access-control")
if [ -n "$response" ]; then
    echo "   ✅ CORS configuré"
    echo "$response"
else
    echo "   ⚠️  CORS headers non détectés"
fi
echo

# Test 9: 404 Handling
echo "9. 404 Handling:"
response=$(curl -s "$API_URL/api/nonexistent")
if echo "$response" | grep -q "error\|Not found"; then
    echo "   ✅ 404 géré correctement"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "   ⚠️  Réponse inattendue pour 404"
    echo "   Response: $response"
fi
echo

echo "=========================================="
echo "✅ Tests terminés"
echo "=========================================="

