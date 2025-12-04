# Déploiement Vercel

Ce projet est configuré pour être déployé automatiquement sur Vercel.

## Configuration

- **vercel.json** : Configuration du build Python
- **.vercelignore** : Exclut les gros fichiers de données
- **requirements.txt** : Dépendances Python (vide car on utilise seulement la stdlib)

## Connexion du repo GitHub

Pour connecter ce repo à Vercel et activer les déploiements automatiques :

1. **Via l'interface web** (recommandé) :
   - Aller sur https://vercel.com/rqbins-projects/genhack4-hackathon-vertex/settings/git
   - Cliquer sur "Connect Git Repository"
   - Sélectionner le repo : `Rqbln/GenHack4-Hackathon-Vertex`
   - Choisir la branche `main` pour la production

2. **Via la CLI Vercel** :
   ```bash
   npm i -g vercel
   cd GenHack4-Hackathon-Vertex
   vercel link
   ```

## Structure pour Vercel

```
GenHack4-Hackathon-Vertex/
├── api/
│   └── index.py          # Handler Vercel (BaseHTTPRequestHandler)
├── vercel.json           # Configuration Vercel
├── requirements.txt      # Dépendances Python
└── .vercelignore        # Fichiers à exclure
```

## Endpoints API

- `GET /health` - Health check
- `GET /api/stations` - Liste des stations météo
- `GET /api/temperature?station_id=X&start_date=Y&end_date=Z` - Températures d'une station
- `GET /api/heatmap?date=Y&bbox=X` - Données de heatmap
- `GET /api/metrics` - Métriques du modèle

## Déploiement automatique

Une fois connecté, chaque push sur `main` déclenchera automatiquement un déploiement sur Vercel.
