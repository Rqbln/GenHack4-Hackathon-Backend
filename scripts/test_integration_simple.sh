#!/bin/bash
# Test d'intégration simplifié

echo "=========================================="
echo "Test d'Intégration Frontend-Backend"
echo "=========================================="

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"

# Test 1: API Health
echo -e "\n1. Test API Health:"
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo "✅ API accessible"
    curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/health"
else
    echo "❌ API non accessible - Démarrez avec: cd GenHack4-Hackathon-Vertex && python3 src/api_simple.py"
    exit 1
fi

# Test 2: API Endpoints
echo -e "\n\n2. Test des endpoints API:"
ENDPOINTS=(
    "/api/stations"
    "/api/metrics"
    "/api/metrics/comparison"
    "/api/metrics/advanced"
    "/api/validation/physics"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s "$API_URL$endpoint" > /dev/null 2>&1; then
        echo "✅ $endpoint"
    else
        echo "❌ $endpoint"
    fi
done

# Test 3: Frontend
echo -e "\n\n3. Test Frontend:"
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo "✅ Frontend accessible sur $FRONTEND_URL"
else
    echo "⚠️  Frontend non accessible - Démarrez avec: cd GenHack4-Hackathon-Frontend && npm run dev"
fi

# Test 4: CORS
echo -e "\n\n4. Test CORS:"
CORS_TEST=$(curl -s -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" \
    -X OPTIONS "$API_URL/api/stations" -i 2>&1 | grep -i "access-control" | head -1)
if [ -n "$CORS_TEST" ]; then
    echo "✅ CORS configuré: $CORS_TEST"
else
    echo "⚠️  CORS non détecté (peut être normal)"
fi

# Test 5: Données complètes
echo -e "\n\n5. Test données complètes:"
echo "Stations:"
curl -s "$API_URL/api/stations" | python3 -m json.tool 2>/dev/null | head -10

echo -e "\nMétriques (extrait):"
curl -s "$API_URL/api/metrics/comparison" | python3 -m json.tool 2>/dev/null | head -15

echo -e "\n\n=========================================="
echo "✅ Tests d'intégration terminés"
echo "=========================================="
echo -e "\nPour tester manuellement:"
echo "1. Ouvrez $FRONTEND_URL dans votre navigateur"
echo "2. Vérifiez que l'indicateur de connexion est vert"
echo "3. Testez les interactions avec l'API"

