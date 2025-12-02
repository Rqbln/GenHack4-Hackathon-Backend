# Guide de Test pour Nouvelles Implémentations

## Processus Standard

Pour chaque nouvelle implémentation, suivez ces étapes :

### 1. Créer le Test de Structure

Créez un fichier `test_day{N}_simple.py` qui teste la structure du code :

```python
#!/usr/bin/env python3
"""
Simplified test for Day N: <Description>
Tests the structure without requiring all dependencies
"""

import sys
from pathlib import Path

def test_structure():
    """Test class/method structure"""
    # Test file exists and can be parsed
    # Check for key classes and methods
    # Validate syntax
    pass

if __name__ == "__main__":
    success = test_structure()
    sys.exit(0 if success else 1)
```

### 2. Créer le Test Complet (Optionnel)

Créez un fichier `test_day{N}.py` qui teste la fonctionnalité complète :

```python
#!/usr/bin/env python3
"""
Full test for Day N: <Description>
Requires all dependencies
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import and test actual functionality
```

### 3. Exécuter les Tests

```bash
# Test structure uniquement
python3 scripts/tests/test_day{N}_simple.py

# Test complet (si deps disponibles)
python3 scripts/tests/test_day{N}.py

# Ou utiliser le script helper
./scripts/tests/test_new_implementation.sh {N} "<description>"
```

### 4. Vérifier que Tout Passe

- ✅ Syntaxe Python valide
- ✅ Structure du code correcte
- ✅ Tests de structure passent
- ✅ Build frontend compile (si changement frontend)

### 5. Commit et Push

```bash
git add .
git commit -m "feat: <description> - Day N"
git push
```

## Checklist Avant Commit

- [ ] Code compile sans erreurs
- [ ] Tests de structure passent
- [ ] Syntaxe validée
- [ ] Frontend build réussi (si applicable)
- [ ] Pas d'erreurs de linter
- [ ] Documentation à jour

## Tests Automatiques

Le script `test_all_days_1_4.py` peut être étendu pour inclure de nouveaux jours :

```python
tests = [
    # ... existing tests ...
    (f"Day {N}: {Description}", tests_dir / f"test_day{N}_simple.py"),
]
```

