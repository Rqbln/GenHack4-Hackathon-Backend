# Guide de Capture Vidéo Démo Marketing (4K)

## 🎬 Objectif

Créer une vidéo de démonstration marketing (5-10 minutes) pour présenter le projet GenHack 2025 de manière professionnelle et engageante.

---

## 📋 Checklist Pré-Capture

- [ ] Dashboard démarré en mode production (`npm run build && npm run preview`)
- [ ] Résolution d'écran : 3840x2160 (4K UHD) ou 1920x1080 (Full HD)
- [ ] Audio : Microphone de qualité + musique de fond discrète (optionnel)
- [ ] Outil de capture : OBS Studio (recommandé) ou QuickTime
- [ ] Éclairage : Bonne visibilité de l'écran
- [ ] Navigation préparée : Script de démonstration testé

---

## 🎯 Scénario de Démonstration (10 minutes)

### 1. Introduction (1 minute)
- **Action** : Présentation du projet
- **Points à mentionner** :
  - "GenHack 2025 - Chronos-WxC: AI-Powered Climate Downscaling"
  - "Solution pour les îlots de chaleur urbains"
  - "Downscaling de 9km à 100m avec Prithvi WxC"

### 2. Le Problème (1 minute)
- **Action** : Montrer la carte avec données ERA5 (basse résolution)
- **Démontrer** :
  - Limitation de la résolution 9km
  - Besoin de données à l'échelle de la rue
  - Impact sur la planification urbaine

### 3. Notre Solution (2 minutes)
- **Action** : Scrollytelling - Navigation dans l'histoire
- **Démontrer** :
  - Architecture Prithvi WxC (2.3B paramètres)
  - Fine-tuning avec QLoRA (1% des paramètres)
  - Fonction de perte composite (MSE + Perceptual + PINN)
  - Transitions fluides de la carte

### 4. Résultats (2 minutes)
- **Action** : SwipeMap - Comparaison ERA5 vs Prithvi
- **Démontrer** :
  - Amélioration de 38% du RMSE
  - Perkins Score : 0.84 (extrêmes capturés)
  - HeatmapLayer avec données haute résolution
  - Validation physique (4/4 tests passés)

### 5. Dashboard Interactif (2 minutes)
- **Action** : Navigation complète du dashboard
- **Démontrer** :
  - Sélection de stations météo
  - Graphiques temporels interactifs
  - Timeline slider avec navigation temporelle
  - Tooltips et interactions fluides
  - Glassmorphism et animations

### 6. Métriques et Validation (1 minute)
- **Action** : Afficher les métriques avancées
- **Démontrer** :
  - Tableau de comparaison Baseline vs Prithvi
  - Perkins Skill Score expliqué
  - Validation physique (UHI-NDVI, UHI-NDBI)
  - Analyse spectrale

### 7. Impact et Conclusion (1 minute)
- **Action** : Résumé et call-to-action
- **Points à mentionner** :
  - "Solution prête pour le déploiement"
  - "Applications : planification urbaine, santé publique"
  - "Code open-source disponible sur GitHub"

---

## 🎥 Paramètres de Capture Recommandés (OBS Studio)

### Résolution et FPS
- **Résolution** : 3840x2160 (4K) ou 1920x1080 (Full HD)
- **FPS** : 60 (pour fluidité) ou 30 (si ressources limitées)
- **Format** : MP4 (H.264)
- **Bitrate** : 50000 kbps (4K) ou 10000 kbps (Full HD)

### Audio
- **Sample Rate** : 48 kHz
- **Bitrate** : 192 kbps
- **Format** : AAC

### Scènes OBS
1. **Dashboard Full Screen** : Capture écran complète
2. **Dashboard + Webcam** : Picture-in-picture (optionnel)
3. **Code/Architecture** : Capture fenêtre IDE (si nécessaire)

---

## 💡 Conseils pour une Vidéo Professionnelle

### Préparation
1. **Script** : Préparer un script détaillé avec timing
2. **Test** : Répéter la démo plusieurs fois
3. **Nettoyage** : Fermer applications inutiles, notifications désactivées
4. **Thème** : Utiliser le thème sombre du dashboard

### Pendant la Capture
1. **Mouvements fluides** : Souris lente et précise
2. **Pauses** : 2-3 secondes sur chaque fonctionnalité
3. **Zoom** : Utiliser zoom navigateur pour détails importants
4. **Narration** : Parler clairement, rythme modéré

### Post-Production
1. **Montage** : Couper les temps morts et erreurs
2. **Annotations** : Ajouter textes/flèches pour points clés
3. **Musique** : Ajouter musique de fond discrète (optionnel)
4. **Transitions** : Transitions douces entre sections
5. **Titres** : Ajouter titre, crédits, liens GitHub

---

## 📁 Fichiers à Générer

1. **Vidéo principale** : `demo_marketing_4k.mp4` (5-10 minutes)
2. **Version courte** : `demo_marketing_short.mp4` (2-3 minutes, pour réseaux sociaux)
3. **Screenshots** : Captures d'écran haute résolution des fonctionnalités clés
4. **Script** : Transcription complète de la narration

---

## 🚀 Commandes Utiles

```bash
# Build production
cd GenHack4-Hackathon-Frontend
npm run build
npm run preview

# Démarrer en mode développement (pour tests)
npm run dev

# Capture avec OBS Studio
# 1. Créer nouvelle scène "Dashboard"
# 2. Ajouter source "Capture d'écran"
# 3. Configurer résolution 4K
# 4. Démarrer l'enregistrement
```

---

## ✅ Checklist Post-Capture

- [ ] Vidéo enregistrée et sauvegardée
- [ ] Qualité vidéo vérifiée (4K ou Full HD)
- [ ] Durée respectée (5-10 minutes)
- [ ] Audio clair (si narration)
- [ ] Toutes les fonctionnalités démontrées
- [ ] Post-production complétée
- [ ] Version courte créée (optionnel)
- [ ] Vidéo uploadée sur Drive/plateforme

---

## 📝 Script de Narration (Template)

```
[00:00-01:00] Introduction
"Bienvenue dans cette démonstration de Chronos-WxC, notre solution pour le downscaling climatique développée lors du GenHack 2025..."

[01:00-02:00] Le Problème
"Les modèles climatiques globaux comme ERA5 fournissent des données à 9km de résolution, insuffisantes pour capturer les variations à l'échelle de la rue..."

[02:00-04:00] Notre Solution
"Notre approche utilise Prithvi WxC, un modèle de fondation de 2.3 milliards de paramètres, fine-tuné avec QLoRA pour ne réentraîner que 1% des paramètres..."

[04:00-06:00] Résultats
"Les résultats sont impressionnants : 38% de réduction du RMSE, un Perkins Score de 0.84 pour capturer les événements extrêmes..."

[06:00-08:00] Dashboard
"Notre dashboard interactif permet d'explorer les données de manière intuitive, avec des visualisations haute performance..."

[08:00-09:00] Métriques
"La validation physique confirme que notre modèle respecte les lois physiques, avec 4 validations sur 4 passées..."

[09:00-10:00] Conclusion
"Cette solution est prête pour le déploiement et offre des perspectives prometteuses pour l'analyse des îlots de chaleur urbains..."
```

---

*Guide créé le 16 Décembre 2025 pour le livrable final*

