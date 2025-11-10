#!/bin/bash
# GenHack Climate - Script de test local
# Usage: ./test_local.sh

set -e

echo "🧪 GenHack Climate - Tests locaux"
echo "=================================="
echo ""

# Vérifier que le venv existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création en cours..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activer le venv
echo "📦 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances de test si nécessaire
if ! python -c "import pytest" 2>/dev/null; then
    echo "📥 Installation des dépendances de test..."
    pip install -q pytest jsonschema pydantic pyyaml
    echo "✅ Dépendances installées"
fi

echo ""
echo "🧪 Exécution des tests de contrats..."
echo "--------------------------------------"
python -m pytest tests/test_contracts.py -v

echo ""
echo "✅ Tous les tests sont passés !"
echo ""
echo "📊 Résumé:"
echo "  - Tests de schémas JSON : OK"
echo "  - Validation Pydantic : OK"
echo "  - Contrats de données : OK"
