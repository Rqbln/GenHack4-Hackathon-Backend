# 🔍 Statut du Modèle Prithvi WxC

**Date** : 18 Décembre 2025

## ✅ Code Disponible

Le code pour utiliser Prithvi WxC est disponible dans :
- `src/prithvi_setup.py` - Setup et chargement du modèle
- `src/finetuning.py` - Fine-tuning avec QLoRA
- `src/dataset_preparation.py` - Préparation des données pour l'entraînement

## ❌ Dépendances Manquantes

Pour utiliser le modèle Prithvi WxC, les dépendances suivantes doivent être installées :

```bash
pip install torch transformers pillow peft bitsandbytes accelerate
```

**Note** : Ces dépendances sont lourdes (~2-3GB) et nécessitent :
- PyTorch (CPU ou CUDA)
- Transformers (Hugging Face)
- PEFT (pour QLoRA)

## 📦 Modèle Non Téléchargé

Le modèle Prithvi WxC n'a pas encore été téléchargé. Pour le télécharger :

```bash
cd GenHack4-Hackathon-Vertex
source venv/bin/activate
pip install torch transformers pillow
python3 -c "from src.prithvi_setup import PrithviWxCSetup; setup = PrithviWxCSetup(); setup.download_model()"
```

**Taille du modèle** : ~9GB (2.3B paramètres)

## 🖥️ Ressources Nécessaires

### Pour l'Inférence (Test)
- **CPU** : Possible mais lent
- **RAM** : Minimum 8GB
- **Espace disque** : ~10GB pour le modèle

### Pour l'Entraînement (Fine-tuning)
- **GPU** : Recommandé (16GB+ VRAM)
- **RAM** : 32GB+ recommandé
- **Espace disque** : ~50GB pour modèle + données

## 🚀 Alternatives

Si le modèle ne peut pas être téléchargé/entraîné :

1. **Utiliser le baseline uniquement** ✅ (déjà fait)
   - Métriques baseline calculées avec vraies données
   - RMSE: 2.85°C, MAE: 1.94°C, R²: 0.72

2. **Utiliser Google Colab Pro / Kaggle**
   - GPU gratuit disponible
   - Peut télécharger et entraîner le modèle

3. **Présenter la méthodologie**
   - Code prêt pour Prithvi
   - Architecture documentée
   - Métriques baseline comme référence

## 📊 Métriques Actuelles

Les métriques baseline sont calculées et disponibles dans `results/all_metrics.json` :
- **Baseline** : RMSE 2.85°C, MAE 1.94°C, R² 0.72
- **Prithvi** : Non entraîné (status: "not_trained")

## ✅ Recommandation

Pour le hackathon, nous pouvons :
1. ✅ Présenter les métriques baseline (fait)
2. ✅ Expliquer l'architecture Prithvi (code prêt)
3. ✅ Montrer que le pipeline est opérationnel
4. ⚠️ Mentionner que l'entraînement nécessite GPU (non disponible localement)

---

**Dernière vérification** : 18 Décembre 2025

