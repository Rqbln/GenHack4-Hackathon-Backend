# Guide de Capture Vidéo - Démo MVP Dashboard

## 🎬 Objectif

Créer une vidéo de démonstration (5 minutes max) montrant les fonctionnalités du MVP Dashboard pour le livrable Semaine 3.

---

## 📋 Checklist Pré-Capture

- [ ] Dashboard démarré et fonctionnel (`npm run dev`)
- [ ] Backend connecté (si disponible) ou mode démo activé
- [ ] Données de test chargées
- [ ] Résolution d'écran : 1920x1080 (Full HD) minimum
- [ ] Audio : Microphone activé pour narration (optionnel)
- [ ] Outil de capture : OBS Studio, QuickTime, ou équivalent

---

## 🎯 Scénario de Démonstration (5 minutes)

### 1. Introduction (30 secondes)
- **Action** : Présenter le dashboard GenHack 2025
- **Points à mentionner** :
  - "Dashboard interactif pour l'analyse des îlots de chaleur urbains"
  - "Technologies : React 19, Deck.gl, MapLibre GL JS"
  - "Données : ERA5, Sentinel-2 NDVI, ECA&D stations"

### 2. Visualisation de la Carte (1 minute)
- **Action** : Naviguer sur la carte
- **Démontrer** :
  - ✅ Fond de carte sombre (Dark Mode)
  - ✅ Zoom/Pan fluides
  - ✅ Stations météo visibles (points rouges)
  - ✅ Tooltip au survol des stations

### 3. Interaction avec les Stations (1 minute)
- **Action** : Cliquer sur une station
- **Démontrer** :
  - ✅ Sélection visuelle (point jaune)
  - ✅ Affichage des informations de la station
  - ✅ Graphique temporel qui apparaît en bas
  - ✅ Navigation dans les données temporelles

### 4. Navigation Temporelle (1 minute)
- **Action** : Utiliser le Timeline Slider
- **Démontrer** :
  - ✅ Slider interactif en bas de l'écran
  - ✅ Changement de date
  - ✅ Boutons de navigation (début, fin, précédent, suivant)
  - ✅ Sélection de pas temporel (jour, semaine, mois)

### 5. Graphiques Temporels (1 minute)
- **Action** : Explorer les graphiques
- **Démontrer** :
  - ✅ Graphique de température par station
  - ✅ Tooltips interactifs sur les points
  - ✅ Zoom/Pan dans le graphique
  - ✅ Synchronisation avec la sélection de station

### 6. Connexion Backend (30 secondes)
- **Action** : Montrer le statut de connexion
- **Démontrer** :
  - ✅ Indicateur de connexion backend (coin supérieur droit)
  - ✅ Statut vert si connecté, rouge si offline
  - ✅ Monitoring automatique

### 7. Conclusion (30 secondes)
- **Action** : Résumer les fonctionnalités
- **Points à mentionner** :
  - "Dashboard MVP fonctionnel avec toutes les fonctionnalités de base"
  - "Prêt pour l'intégration des données IA (Prithvi WxC)"
  - "Prochaines étapes : Fine-tuning et visualisations avancées"

---

## 🎥 Paramètres de Capture Recommandés

### OBS Studio
- **Résolution** : 1920x1080
- **FPS** : 30 ou 60
- **Format** : MP4 (H.264)
- **Bitrate** : 5000-10000 kbps
- **Audio** : 48 kHz, 128 kbps

### QuickTime (Mac)
- **Résolution** : Enregistrement d'écran complet
- **Qualité** : Maximum
- **Format** : MP4

---

## 💡 Conseils pour une Bonne Démo

1. **Préparation** :
   - Tester toutes les fonctionnalités avant la capture
   - Préparer un script de narration (optionnel)
   - Fermer les applications inutiles

2. **Pendant la capture** :
   - Mouvements de souris fluides et lents
   - Pauses de 2-3 secondes sur chaque fonctionnalité
   - Zoom sur les éléments importants si nécessaire

3. **Post-production** :
   - Ajouter des annotations si besoin
   - Couper les temps morts
   - Ajouter une musique de fond discrète (optionnel)
   - Ajouter un titre et des crédits

---

## 📁 Fichiers à Générer

1. **Vidéo principale** : `demo_mvp_dashboard.mp4` (5 minutes max)
2. **Screenshots** : Captures d'écran des fonctionnalités clés
3. **Script** : Transcription de la narration (optionnel)

---

## 🚀 Commandes Utiles

```bash
# Démarrer le dashboard
cd GenHack4-Hackathon-Frontend
npm run dev

# Build de production (pour test)
npm run build
npm run preview

# Activer le mode démo
# Cliquer sur le bouton "🎬 Demo Mode" dans le dashboard
```

---

## ✅ Checklist Post-Capture

- [ ] Vidéo enregistrée et sauvegardée
- [ ] Qualité vidéo vérifiée
- [ ] Durée respectée (≤ 5 minutes)
- [ ] Toutes les fonctionnalités démontrées
- [ ] Audio clair (si narration)
- [ ] Vidéo uploadée sur Drive/plateforme

---

*Guide créé le 07 Décembre 2025 pour le livrable Semaine 3*

