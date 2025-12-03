#!/bin/bash
# Script de test d'intégration Frontend-Backend

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test d'Intégration Frontend-Backend${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Vertex"
FRONTEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Frontend"

# Check if API is running
echo -e "${YELLOW}1. Vérification de l'API Backend...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Backend accessible${NC}"
else
    echo -e "${RED}❌ API Backend non accessible${NC}"
    echo -e "${YELLOW}   Démarrez l'API avec: cd $BACKEND_DIR && python3 src/api.py${NC}"
    exit 1
fi

# Test API endpoints
echo -e "\n${YELLOW}2. Test des endpoints API...${NC}"

ENDPOINTS=(
    "/health"
    "/api/stations"
    "/api/metrics"
    "/api/metrics/comparison"
    "/api/metrics/advanced"
    "/api/validation/physics"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s "http://localhost:8000$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $endpoint${NC}"
    else
        echo -e "${RED}❌ $endpoint${NC}"
    fi
done

# Check frontend build
echo -e "\n${YELLOW}3. Vérification du build Frontend...${NC}"
cd "$FRONTEND_DIR"
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Build Frontend réussi${NC}"
else
    echo -e "${RED}❌ Build Frontend échoué${NC}"
    exit 1
fi

# Check if frontend dev server is running
echo -e "\n${YELLOW}4. Vérification du serveur Frontend...${NC}"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Serveur Frontend accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Serveur Frontend non accessible${NC}"
    echo -e "${YELLOW}   Démarrez avec: cd $FRONTEND_DIR && npm run dev${NC}"
fi

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Résumé${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${GREEN}✅ Tests d'intégration terminés${NC}"
echo -e "\n${YELLOW}Pour tester manuellement:${NC}"
echo -e "1. Ouvrez http://localhost:5173"
echo -e "2. Vérifiez que l'indicateur de connexion est vert"
echo -e "3. Testez les interactions avec l'API"

