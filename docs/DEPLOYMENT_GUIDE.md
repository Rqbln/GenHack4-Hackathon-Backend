# 🚀 Guide de Déploiement - GenHack 2025

**Date** : 18 Décembre 2025

---

## 📋 Vue d'Ensemble

Ce guide explique comment déployer le backend API et le frontend pour GenHack 2025.

---

## 🔧 Backend API

### Option 1 : Déploiement Local (Développement)

```bash
cd GenHack4-Hackathon-Vertex
source venv/bin/activate
python3 src/api_simple.py
```

L'API sera accessible sur `http://localhost:8000`

### Option 2 : Docker (Recommandé pour Production)

```bash
cd GenHack4-Hackathon-Vertex

# Build image
docker build -t genhack-api .

# Run container
docker run -p 8000:8000 genhack-api
```

### Option 3 : Cloud Run (GCP)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/genhack-api

# Deploy to Cloud Run
gcloud run deploy genhack-api \
  --image gcr.io/PROJECT_ID/genhack-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

### Option 4 : Vercel Serverless

Le fichier `vercel.json` est déjà configuré. Pour déployer :

```bash
cd GenHack4-Hackathon-Vertex
vercel deploy
```

**Note** : Vercel nécessite que l'API soit adaptée pour les fonctions serverless.

---

## 🎨 Frontend

### Déploiement Vercel (Recommandé)

```bash
cd GenHack4-Hackathon-Frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy --prod
```

### Configuration des Variables d'Environnement

Créer un fichier `.env.production` :

```env
VITE_API_BASE_URL=https://your-api-url.com
```

Ou configurer dans Vercel Dashboard :
- Settings → Environment Variables
- Ajouter `VITE_API_BASE_URL` avec l'URL de l'API déployée

---

## ✅ Checklist de Déploiement

### Backend
- [ ] Tester l'API localement (`python3 src/api_simple.py`)
- [ ] Vérifier que les métriques sont chargées (`/api/metrics`)
- [ ] Vérifier que les stations sont chargées (`/api/stations`)
- [ ] Tester tous les endpoints
- [ ] Déployer sur Cloud Run / Vercel / Railway
- [ ] Tester l'API déployée
- [ ] Configurer CORS si nécessaire

### Frontend
- [ ] Tester localement avec `npm run dev`
- [ ] Vérifier la connexion à l'API
- [ ] Configurer `VITE_API_BASE_URL` pour la production
- [ ] Build de production (`npm run build`)
- [ ] Tester le build localement
- [ ] Déployer sur Vercel
- [ ] Vérifier que le frontend se connecte à l'API déployée

---

## 🔍 Tests Post-Déploiement

### Backend
```bash
# Health check
curl https://your-api-url.com/health

# Metrics
curl https://your-api-url.com/api/metrics

# Stations
curl https://your-api-url.com/api/stations
```

### Frontend
1. Ouvrir l'URL déployée
2. Vérifier l'indicateur de connexion (coin supérieur droit)
3. Vérifier que les stations s'affichent
4. Tester les interactions (cliquer sur une station, timeline, etc.)

---

## 📝 Notes Importantes

- **CORS** : L'API simple a CORS activé pour toutes les origines (`*`). En production, restreindre aux domaines autorisés.
- **Variables d'environnement** : Ne pas commiter les fichiers `.env` avec des secrets.
- **Données** : Les fichiers de données (`data/processed/`, `results/`) doivent être inclus dans le déploiement ou servis depuis un stockage externe.

---

**Dernière mise à jour** : 18 Décembre 2025


