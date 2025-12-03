#!/bin/bash
# Script pour démarrer tous les services

echo "=========================================="
echo "Démarrage des Services GenHack 2025"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Vertex"
FRONTEND_DIR="$PROJECT_ROOT/GenHack4-Hackathon-Frontend"

# Fonction pour vérifier si un port est utilisé
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Démarrer API Backend
echo -e "\n1. Démarrage API Backend (port 8000)..."
if check_port 8000; then
    echo "⚠️  Port 8000 déjà utilisé"
else
    cd "$BACKEND_DIR"
    python3 src/api_simple.py > /tmp/api.log 2>&1 &
    API_PID=$!
    echo "✅ API démarrée (PID: $API_PID)"
    echo "   Logs: tail -f /tmp/api.log"
    sleep 2
fi

# Démarrer Frontend
echo -e "\n2. Démarrage Frontend (port 5173)..."
if check_port 5173; then
    echo "⚠️  Port 5173 déjà utilisé"
else
    cd "$FRONTEND_DIR"
    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend démarré (PID: $FRONTEND_PID)"
    echo "   Logs: tail -f /tmp/frontend.log"
    sleep 3
fi

# Vérification
echo -e "\n3. Vérification des services..."
sleep 2

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API accessible: http://localhost:8000"
else
    echo "❌ API non accessible"
fi

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend accessible: http://localhost:5173"
else
    echo "❌ Frontend non accessible"
fi

echo -e "\n=========================================="
echo "Services démarrés!"
echo "=========================================="
echo -e "\nAPI: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo -e "\nPour arrêter:"
echo "  kill $API_PID $FRONTEND_PID"
echo -e "\nOu utilisez: pkill -f 'api_simple.py|npm run dev'"

