

# **Rapport Stratégique et Technique : GenHack 2025 – Innovation Disruptive par Modèles de Fondation et Visualisation Immersive**

## **Résumé Exécutif**

Ce rapport définit l'architecture scientifique, technique et opérationnelle pour la participation au Hackathon GenHack 2025\. À la date critique du 30 novembre 2025, alors que l'échéance de la semaine 3 est imminente, une réorientation stratégique s'impose pour garantir une différenciation décisive face à la concurrence, notamment l'équipe Pentagen. L'analyse approfondie des datasets (ERA5, Sentinel-2, ECA\&D, GADM) et de l'état de l'art technologique 2024-2025 révèle que les approches conventionnelles de downscaling (SRCNN, Interpolation) sont obsolètes face aux **Modèles de Fondation Climatiques** et aux **Réseaux Informés par la Physique (PINNs)**.

Notre stratégie repose sur le déploiement du modèle **Prithvi WxC**, un Vision Transformer (ViT) pré-entraîné sur des pétaoctets de données atmosphériques, capable de capturer les dépendances spatio-temporelles complexes que les architectures CNN standard (probablement utilisées par Pentagen) échouent à modéliser. Cette modélisation sera validée non seulement par des métriques d'erreur classiques, mais par le **Perkins Skill Score**, démontrant notre capacité à capturer les extrêmes climatiques critiques pour l'adaptation urbaine.

En parallèle, l'expérience utilisateur sera transformée par une stack **React 19 \+ Deck.gl**, abandonnant les cartes statiques pour un **Digital Twin** interactif piloté par GPU, intégrant du "Scrollytelling" pour contextualiser l'Îlot de Chaleur Urbain (ICU). Ce document détaille une roadmap exhaustive du 1er au 20 décembre 2025, assurant une exécution millimétrée de la fusion des données à la livraison finale.

---

## **1\. Analyse Critique de l'Écosystème de Données et Stratégie d'Intégration**

La réussite du projet GenHack 2025 ne dépend pas uniquement de la sophistication algorithmique, mais avant tout de la capacité à orchestrer une fusion cohérente des quatre jeux de données hétérogènes fournis. L'analyse suivante décortique les limites intrinsèques de chaque source et propose des protocoles de remédiation avancés pour construire une "Vérité Terrain" composite robuste.

### **1.1 ERA5 : La Référence Macro-Climatique et ses Limites Spatiales**

Le jeu de données de réanalyse ERA5, produit par l'ECMWF, constitue la colonne vertébrale thermodynamique de notre projet. Il fournit une représentation cohérente de l'état de l'atmosphère, intégrant les lois de conservation de la masse et de l'énergie. Cependant, son utilisation brute dans un contexte urbain constitue un piège méthodologique majeur.

Analyse de la Résolution et de la Représentativité :  
Avec une résolution spatiale native d'environ 31 km (0.25°), un pixel ERA5 englobe des environnements radicalement différents : centre-ville dense, banlieue pavillonnaire, forêts périurbaines et surfaces aquatiques.1 Dans le contexte de l'Îlot de Chaleur Urbain (ICU), cette résolution lisse totalement les micro-phénomènes thermiques. Par exemple, une différence de température de 4 à 5°C peut exister entre un parc urbain et une artère bétonnée adjacente, une variance totalement invisible pour ERA5.  
Stratégie d'Exploitation :  
Plutôt que d'utiliser ERA5 comme une "carte de température", nous l'exploiterons comme un conditionnement aux limites (Boundary Condition). ERA5 fournit le contexte synoptique (la météo globale, la position des fronts, la pression atmosphérique) qui pilote le climat local. Notre modèle de fondation utilisera ces champs macroscopiques pour "guider" la génération de textures haute fréquence.  
Les variables critiques à extraire incluent non seulement la température à 2m (t2m), mais aussi les composantes du vent (u10, v10) et la température de rosée, car l'advection et l'humidité jouent un rôle crucial dans la dissipation ou la concentration de la chaleur urbaine.3  
Il est également pertinent de noter que les données ERA5-Land, bien qu'offrant une résolution améliorée à 9 km, restent insuffisantes pour l'échelle du quartier, justifiant le besoin impératif d'un downscaling par IA.4

### **1.2 Sentinel-2 : Caractérisation de la Texture Urbaine et Gestion des Lacunes**

Si ERA5 fournit le "Quoi" (la météo), Sentinel-2 fournit le "Où" (la structure de la ville). Avec une résolution de 10 à 60 mètres, les capteurs MSI (MultiSpectral Instrument) capturent l'hétérogénéité des surfaces urbaines.

Le Rôle des Indices Spectraux :  
L'analyse ne doit pas se limiter aux bandes RGB. La dérivation d'indices biophysiques est essentielle pour nourrir le modèle de downscaling avec des prédicteurs pertinents :

* **NDVI (Normalized Difference Vegetation Index) :** Corrélation négative forte avec l'ICU grâce à l'évapotranspiration.  
* **NDBI (Normalized Difference Built-up Index) :** Corrélation positive avec l'ICU due à l'inertie thermique des matériaux (béton, asphalte).  
* **MNDWI (Modified Normalized Difference Water Index) :** Identification des plans d'eau modérateurs thermiques.6

Le Défi Critique : La Discontinuité Temporelle (Nuages) :  
Contrairement aux satellites radar, Sentinel-2 est optique et donc aveugle sous la couverture nuageuse. Pour un hackathon se déroulant en hiver (décembre), la probabilité d'obtenir des images claires est faible. Une série temporelle lacunaire briserait la continuité du modèle IA.  
L'approche naïve (interpolation linéaire ou spline) est à proscrire car elle ne respecte pas la phénologie de la végétation ni les changements brusques d'occupation du sol.  
Solution Novatrice : Reconstruction par Apprentissage Automatique :  
Nous proposons d'implémenter une stratégie de Gap Filling basée sur des recherches de 2024-2025. Deux approches sont possibles :

1. **Random Forest Spatialisé :** Entraînement d'un modèle pour prédire les pixels manquants en fonction des pixels voisins valides et des dates adjacentes. Cette méthode a montré une robustesse supérieure aux méthodes harmoniques (HANTS) pour des lacunes complexes.7  
2. Approche Générative (GANs) : Pour les lacunes étendues, un GAN peut "imaginer" la texture manquante en se basant sur la structure globale de l'image, bien que cela soit plus risqué en termes d'artefacts.8  
   Pour le hackathon, la méthode Random Forest offre le meilleur compromis rapidité/robustesse.6

### **1.3 ECA\&D : La Vérité Terrain et la Validation Rigoureuse**

L'European Climate Assessment & Dataset (ECA\&D) est souvent sous-estimé par les équipes concurrentes qui se fient trop aux modèles. Or, c'est la seule source de données mesurée in-situ.

Validation et Correction de Biais :  
Les données de stations serviront de Ground Truth (Vérité Terrain) pour calculer la fonction de perte (Loss Function) lors du fine-tuning du modèle. Plus important encore, elles permettront de quantifier le biais systématique d'ERA5. Il est documenté que les modèles de réanalyse tendent à sous-estimer les extrêmes de température en milieu urbain dense.  
L'intégration des données ECA\&D permet de "calibrer" les prédictions du modèle Prithvi WxC, assurant que les valeurs downscalées ne sont pas seulement réalistes en texture, mais justes en magnitude absolue.9

### **1.4 GADM : Structuration Spatiale et Optimisation Vectorielle**

La base GADM fournit les limites administratives nécessaires pour l'agrégation des indicateurs (ex: température moyenne par quartier).  
Optimisation Technique pour le Dashboard :  
Le rendu de polygones complexes (milliers de sommets pour une ville détaillée) est coûteux pour le navigateur. Nous transformerons ces vecteurs en formats optimisés pour le web, tels que les Vector Tiles (MVT) ou le format binaire GeoArrow, permettant une interactivité fluide (60 FPS) même lors du survol de centaines de zones administratives simultanément.11 Cette optimisation est cruciale pour l'expérience utilisateur sur le dashboard React.

---

## **2\. État de l'Art 2024-2025 : Rupture Technologique et Différenciation**

Pour surpasser l'équipe Pentagen, nous devons identifier et exploiter les technologies de rupture qui rendent les approches de 2022-2023 obsolètes.

### **2.1 Le Changement de Paradigme : Des CNNs aux Vision Transformers (ViT)**

La majorité des solutions concurrentes (Pentagen) s'appuiera probablement sur des réseaux de neurones convolutifs (CNN) de type U-Net ou SRGAN (Super-Resolution Generative Adversarial Networks).12  
Critique des CNNs : Les convolutions ont un "champ réceptif" limité. Elles excellent à détecter des motifs locaux (bords, textures) mais peinent à capturer des dépendances à longue portée, comme l'influence d'un système dépressionnaire distant de 500 km sur le vent local.  
L'Avantage ViT (Vision Transformers) : Les architectures basées sur l'attention (Self-Attention), comme les ViT, traitent l'image globale simultanément. Elles peuvent modéliser comment la pression atmosphérique dans un coin de l'image influence la température à l'opposé. C'est ce mécanisme qui permet une cohérence physique supérieure lors du downscaling.3

### **2.2 Prithvi WxC : Le Modèle de Fondation Climatique**

Le pivot central de notre stratégie est l'adoption de **Prithvi WxC**, un modèle de fondation open-source publié par IBM et la NASA fin 2024\.14

* **Architecture :** 2,3 milliards de paramètres, entraînés sur 160 variables du dataset MERRA-2 pendant des décennies.  
* **Capacités Uniques :** Contrairement à un modèle entraîné "from scratch" sur nos quelques datasets (ce que fera Pentagen), Prithvi possède une "connaissance innée" de la dynamique des fluides et de la thermodynamique atmosphérique acquise lors de son pré-entraînement massif.  
* **Application au Downscaling :** Des études récentes 3 montrent que le fine-tuning de Prithvi pour le downscaling surpasse les méthodes d'interpolation et les CNNs classiques, en particulier pour la reconstruction des champs de vent et de température en terrain complexe.

### **2.3 Approches Informées par la Physique (PINNs)**

L'Îlot de Chaleur Urbain n'est pas une simple anomalie statistique ; c'est le résultat d'un bilan d'énergie perturbé.  
Différenciation Scientifique :  
Nous intègrerons des principes de Physics-Informed Neural Networks (PINNs). L'idée est d'ajouter un terme de régularisation dans la fonction d'apprentissage qui pénalise les prédictions violant les lois physiques (par exemple, une température de surface incohérente avec l'albédo et le rayonnement solaire incident).16  
Cette approche hybride (Data-Driven \+ Physics-Driven) garantit que nos cartes de chaleur ne sont pas des "hallucinations" de l'IA, mais des estimations physiquement plausibles, un argument de poids pour le jury scientifique.18

---

## **3\. Architecture Scientifique de Modélisation "Chronos-WxC"**

Nous baptisons notre pipeline de modélisation "Chronos-WxC", symbolisant la maîtrise du temps et du climat via l'IA.

### **3.1 Architecture du Modèle et Flux de Données**

Le modèle repose sur une architecture **Encoder-Decoder** hybride, exploitant les poids pré-entraînés de Prithvi WxC.

**1\. Entrées (Inputs) :**

* **Canaux Basse Résolution (Conditionnement) :** ERA5 (Température, Vent, Pression, Humidité) upsamplé à la résolution cible via interpolation bicubique pour fournir un "prior".  
* **Canaux Haute Résolution (Prédicteurs) :** Sentinel-2 (NDVI, NDBI, Albédo), Modèle Numérique de Terrain (SRTM/GADM). Ces données statiques ou quasi-statiques fournissent les détails de haute fréquence.

2\. Le Cœur (Prithvi WxC Backbone) :  
Le modèle Prithvi traite ces entrées sous forme de tokens. L'architecture ViT permet de mixer ces tokens provenant de sources hétérogènes. Nous utiliserons l'implémentation granite-geospatial-wxc-downscaling disponible sur Hugging Face, spécifiquement conçue pour adapter ce modèle de fondation aux tâches de super-résolution.19  
3\. Têtes de Sortie (Decoders) :  
Des têtes convolutionnelles spécifiques (CNN heads) décodent les représentations latentes du Transformer pour reconstruire les champs spatiaux de température et d'humidité à la résolution cible (ex: 100m ou 1km).21 L'utilisation d'une architecture multi-têtes (1EMD) permet de prédire conjointement plusieurs variables, favorisant le transfert de connaissances (le vent aide à prédire la température).22

### **3.2 Stratégie d'Entraînement et Fine-Tuning**

Le fine-tuning d'un modèle de 2,3 milliards de paramètres est gourmand en ressources.  
Optimisation (QLoRA) :  
Pour contourner les limites matérielles potentielles du hackathon, nous utiliserons des techniques de Low-Rank Adaptation (LoRA) ou QLoRA (Quantized LoRA). Cela permet de ne réentraîner qu'un petit sous-ensemble de paramètres (moins de 1% du total) tout en gelant le backbone pré-entraîné, réduisant drastiquement l'empreinte mémoire GPU tout en conservant la performance du modèle de fondation.19  
Fonction de Perte Composite (Loss Function) :  
Pour surpasser Pentagen, notre fonction de perte ne sera pas un simple MSE (Mean Squared Error).  
$$ \\mathcal{L}{total} \= \\lambda{MSE} \\mathcal{L}{pixel} \+ \\lambda{percep} \\mathcal{L}{VGG} \+ \\lambda{phys} \\mathcal{L}\_{PINN} $$

* $\\mathcal{L}\_{pixel}$ : Assure la précision des valeurs (MSE ou L1).  
* $\\mathcal{L}\_{VGG}$ (Perceptual Loss) : Force le modèle à générer des textures réalistes en comparant les features extraites par un réseau VGG, évitant l'effet de flou typique du MSE.12  
* $\\mathcal{L}\_{PINN}$ : Pénalité physique basée sur les équations de bilan d'énergie simplifiées.16

### **3.3 Validation Avancée : Le Perkins Skill Score (S-score)**

C'est ici que nous portons le coup de grâce à l'approche de Pentagen. La concurrence validera probablement son modèle avec le RMSE (Root Mean Square Error).  
Critique du RMSE : Le RMSE favorise les modèles qui prédisent la moyenne et minimisent la variance. Or, pour les vagues de chaleur, ce sont les extrêmes qui comptent. Un modèle avec un bon RMSE peut totalement rater les pics de température de 40°C.  
Notre Métrique : Le Perkins Skill Score (S-score).  
Le S-score mesure le chevauchement (overlap) entre la densité de probabilité (PDF) des observations et celle du modèle.

$$S\_{score} \= \\sum\_{1}^{n} \\min(Z\_{modèle}, Z\_{obs})$$

Un score proche de 1 signifie que le modèle reproduit parfaitement la distribution statistique, y compris les queues de distribution (les événements extrêmes). Utiliser cette métrique démontre une compréhension supérieure des enjeux climatiques.23 Nous compléterons cela par une analyse spectrale (PSD) pour prouver la préservation des structures à haute fréquence spatiales.15

---

## **4\. Stratégie de Visualisation et Dashboard "Impact"**

L'excellence scientifique ne suffit pas ; elle doit être communiquée. Le jury ne jugera pas seulement le code, mais l'expérience. Nous proposons un dashboard immersif basé sur une stack React moderne.

### **4.1 Stack Technique : React 19 \+ Deck.gl**

Pourquoi pas Leaflet ou OpenLayers?  
Les librairies cartographiques classiques manipulent le DOM (Document Object Model). Elles saturent dès quelques milliers de points. Pour visualiser des millions de pixels de température ou des milliers de stations, elles sont inadaptées.  
La Solution : Deck.gl (WebGL2) :  
Deck.gl utilise le GPU pour le rendu. Cela permet d'afficher des datasets massifs avec une fluidité totale (60 FPS).26

* **Intégration React :** Utilisation du composant \<DeckGL /\> comme enfant direct de l'application React, synchronisé avec une "Base Map" vectorielle via react-map-gl (wrapper pour MapLibre GL JS).28  
* **Gestion d'État :** Zustand sera préféré à Redux pour sa légèreté et sa performance dans la gestion des mises à jour fréquentes de l'état du viewport (zoom, pan, tilt).

### **4.2 Composants de Visualisation Clés**

| Composant Deck.gl | Usage Spécifique et Justification | Référence |
| :---- | :---- | :---- |
| **HeatmapLayer** | Visualisation de l'intensité de l'ICU. Permet une agrégation dynamique (Kernel Density Estimation) côté GPU. Idéal pour montrer les "hotspots" de chaleur. | 30 |
| **ScreenGridLayer** | Alternative à la Heatmap pour une visualisation plus "brute" et grilée des données, utile pour montrer la résolution réelle du modèle downscalé. | 31 |
| **H3HexagonLayer** | Agrégation des données socio-économiques ou climatiques sur une grille hexagonale H3 (Uber). Standard industriel pour la comparabilité spatiale. | 32 |
| **TripsLayer** | Animation des flux de vent ou de transport. Effet visuel "Wow" garantissant l'attention du jury lors de la démo. | 33 |

Optimisation des Rasters (GeoTIFF) :  
Le chargement de GeoTIFFs lourds (plusieurs Mo) peut bloquer le navigateur. Nous utiliserons loaders.gl pour parser les données binaires et, si nécessaire, un serveur de tuiles dynamiques (backend Python léger ou Tippecanoe) pour ne servir que les tuiles visibles à l'écran (TileLayer de Deck.gl).34

### **4.3 Expérience Utilisateur : Scrollytelling Interactif**

Plutôt qu'un dashboard où l'utilisateur est perdu face à des boutons, nous guiderons le jury à travers une narration interactive.  
Implémentation avec react-scrollama :

* L'écran est divisé : une colonne de texte narratif à gauche ("Le 14 août à 14h, le centre-ville surchauffe...") et la carte 3D à droite.  
* Au fur et à mesure du défilement (scroll), des "triggers" déclenchent des actions sur la carte : changement de couche (NDVI \-\> Température), mouvement de caméra (Zoom sur un parc), animation temporelle.  
* Utilisation de FlyToInterpolator de Deck.gl pour des transitions cinématographiques fluides entre les points d'intérêt.36

---

## **5\. Roadmap Exhaustive : Sprint Final (01 Déc \- 20 Déc)**

Cette roadmap est conçue pour maximiser l'efficacité de l'équipe et assurer des livrables incrémentaux chaque semaine.

### **Phase 1 : Consolidation des Données et Baseline (Semaine 1 \- Imminente)**

*Objectif : Sécuriser les flux de données et avoir une première version fonctionnelle (MVP).*

| Date | Chantier Backend / Data Science | Chantier Frontend / Viz | Livrable Jour |
| :---- | :---- | :---- | :---- |
| **01 Déc** | Script ETL robuste : Téléchargement et alignement temporel ERA5/Sentinel-2/ECA\&D. Stockage structuré (NetCDF/Zarr). | Init React 19 \+ Vite \+ Tailwind. Setup MapLibre \+ Deck.gl. Affichage fond de carte custom (Dark Mode). | Pipeline Data v1. Carte Hello World. |
| **02 Déc** | **Algorithme Gap-Filling (Random Forest)** : Entraînement sur Sentinel-2 pour combler les nuages. Production des cartes NDVI complètes. | Dev composant StationLayer (Scatterplot) pour visualiser les stations ECA\&D avec Tooltips interactifs. | Rasters NDVI propres. Viz Stations. |
| **03 Déc** | **Baseline Model** : Implémentation interpolation bicubique \+ correction altitudinale. Calcul RMSE baseline (Benchmark Pentagen). | Intégration graphiques temporels (Recharts/Nivo) connectés aux stations sélctionnées sur la carte. | Baseline chiffrée. Dashboard Interactif v0.1. |
| **04 Déc** | Extraction des mailles GADM et calcul des indicateurs par zone (moyennes spatiales). Optimisation vecteurs (GeoArrow). | Implémentation du sélecteur de dates (Timeline Slider) synchronisé avec les couches Deck.gl. | Agrégats spatiaux. Contrôles temporels. |
| **05 Déc** | **Setup Prithvi WxC** : Téléchargement poids Hugging Face (granite-geospatial-wxc). Test inférence simple. | Design System : Finalisation palette couleurs (Viridis/Magma pour chaleur) et typographie. | Env. IA prêt. UI cohérente. |
| **06 Déc** | Préparation dataset Fine-Tuning : Création des paires (LowRes, HighRes, Target). | Optimisation perfs : Chargement asynchrone des layers. | Dataset Train/Val prêt. |
| **07 Déc** | **Rendu Hebdomadaire Semaine 3** : Rapport d'avancement, Baseline Metrics, Démo MVP Dashboard. | **Rendu Hebdomadaire Semaine 3** : Capture vidéo des fonctionnalités de base. | **LIVRABLE SEMAINE 3** |

### **Phase 2 : Innovation et "Heavy Lifting" (Semaine 2\)**

*Objectif : Déployer l'IA avancée et le Scrollytelling.*

| Date | Chantier Backend / Data Science | Chantier Frontend / Viz | Livrable Jour |
| :---- | :---- | :---- | :---- |
| **08 Déc** | **Lancement Fine-Tuning Prithvi** (QLoRA). Focus sur la convergence de la Loss (Pixel \+ Perceptual). | Intégration react-scrollama. Rédaction du script narratif (Storyboarding). | Logs entraînement. Draft Scrollytelling. |
| **09 Déc** | Analyse 1ers résultats IA. Ajustement hyperparamètres. Validation croisée spatiale. | Codage des transitions FlyToInterpolator liées au scroll. Tests d'animations caméra. | Modèle Alpha. Transitions fluides. |
| **10 Déc** | Calculs métriques avancées : **Perkins Score** & Analyse Spectrale. Comparaison vs Baseline. | Intégration HeatmapLayer dynamique avec les nouvelles données IA. | Preuves de supériorité. Viz Heatmap. |
| **11 Déc** | Génération des produits finaux (Time Series complètes sur la période Hackathon). | Ajout composant "Swipe Map" (Comparaison Avant/Après ou ERA5/Prithvi). | Données Finales. Feature Swipe. |
| **12 Déc** | Analyse Physique (PINN validation) : Vérification cohérence UHI vs NDBI/NDVI. | Polissage UI : Animations CSS, Glassmorphism sur les panneaux de contrôle. | Validation Physique. UI Premium. |
| **13 Déc** | Export des résultats et figures pour le rapport final. | Tests cross-browser et performance (Lighthouse). | Assets Rapport. App Robuste. |
| **14 Déc** | **Rendu Hebdomadaire Semaine 4** : Résultats préliminaires IA, Démo Scrollytelling. | **Rendu Hebdomadaire Semaine 4** : Vidéo démo avancée. | **LIVRABLE SEMAINE 4** |

### **Phase 3 : Finalisation et Rendu Final (Semaine 3 du plan \- Semaine 5 réelle)**

*Objectif : Perfectionnement et Communication.*

| Date | Chantier Backend / Data Science | Chantier Frontend / Viz | Livrable Jour |
| :---- | :---- | :---- | :---- |
| **15 Déc** | Rédaction technique détaillée : Justification ViT vs CNN, Analyse Perkins. | Finalisation textes Scrollytelling. Vérification liens et sources. | Textes finaux. |
| **16 Déc** | Création Vidéo Démo "Marketing" (Capture 4K du dashboard). | Mise en production (Vercel/Netlify) \+ Backend API léger (FastAPI). | URL Prod. Vidéo. |
| **17 Déc** | Relecture finale. Vérification conformité critères Hackathon. | Derniers fixes bugs mineurs (glitches visuels). | Projet "Gold". |
| **18 Déc** | **SOUMISSION FINALE GENHACK 2025\.** | **SOUMISSION FINALE GENHACK 2025\.** | **PROJET SOUMIS.** |
| **19-20** | Préparation du Pitch Oral (Slides basés sur le Scrollytelling). |  | Support Présentation. |

---

## **6\. Détails Techniques d'Implémentation**

### **6.1 Fine-Tuning de Prithvi WxC (Code Snippet Conceptuel)**

L'implémentation utilisera la librairie granite-wxc. Voici la logique de la boucle d'entraînement adaptée :

Python

\# Concept de Fine-Tuning Prithvi WxC avec Loss Composite  
import torch  
from granite\_wxc.models import PrithviWxC  
from my\_losses import PerceptualLoss, PhysicalConsistencyLoss

\# Chargement du modèle pré-entraîné (Foundation Model)  
model \= PrithviWxC.from\_pretrained("ibm-nasa-geospatial/Prithvi-WxC-2.3B")  
\# Application de LoRA pour réduire la mémoire (QLoRA)  
model \= apply\_lora(model, rank=8)

optimizer \= torch.optim.AdamW(model.parameters(), lr=1e-4)  
perceptual\_criterion \= PerceptualLoss(net='vgg')  
physical\_criterion \= PhysicalConsistencyLoss()

def train\_step(batch):  
    \# Inputs: ERA5 (Low Res Condition), Sentinel (High Res Features)  
    era5, sentinel, target\_eca \= batch  
      
    \# Forward Pass  
    prediction \= model(era5, sentinel\_features=sentinel)  
      
    \# Calcul de la Loss Composite  
    loss\_mse \= torch.nn.functional.mse\_loss(prediction, target\_eca)  
    loss\_vgg \= perceptual\_criterion(prediction, target\_eca)  
    loss\_phys \= physical\_criterion(prediction, sentinel) \# Vérifie cohérence Albédo/Temp  
      
    total\_loss \= loss\_mse \+ 0.1 \* loss\_vgg \+ 0.05 \* loss\_phys  
      
    \# Backward  
    optimizer.zero\_grad()  
    total\_loss.backward()  
    optimizer.step()  
      
    return total\_loss

Ce code illustre l'intégration des concepts clés : utilisation du modèle de fondation, optimisation LoRA, et fonction de perte multi-objectifs pour garantir la fidélité perceptuelle et physique.19

### **6.2 Calcul de l'Intensité UHI (UHII)**

L'UHII ne doit pas être une simple différence avec une station rurale arbitraire.  
Méthodologie Robuste :

1. **Classification LCZ :** Utiliser Sentinel-2 pour classer les zones en "Local Climate Zones" (LCZ).  
2. **Référence Rurale Dynamique :** Pour chaque pixel urbain, l'algorithme cherche la température moyenne des pixels ruraux (LCZ D \- Low Plants) dans un rayon de 10-15 km, excluant l'eau et l'altitude (\> \+/- 50m de différence).  
3. **Calcul Vectorisé :** Utilisation de xarray et dask pour paralléliser ce calcul sur l'ensemble de la série temporelle.40  
   $$UHII(x,y,t) \= T(x,y,t) \- \\mu(T\_{rural\\\_buffer}(t))$$

---

## **Conclusion**

Ce rapport structure une réponse ambitieuse et scientifiquement rigoureuse aux défis du GenHack 2025\. En nous éloignant des méthodes de downscaling classiques (CNN/GANs) pour adopter les **Modèles de Fondation Climatiques (Prithvi WxC)** et en validant nos résultats par des métriques orientées vers les extrêmes (**Perkins Score**), nous construisons une solution techniquement inattaquable. Le couplage avec un dashboard **React/Deck.gl** immersif transforme ces données complexes en un récit intelligible et percutant. Cette stratégie, exécutée selon la roadmap proposée, positionne notre équipe non seulement comme un concurrent technique, mais comme un leader visionnaire dans l'application de l'IA aux risques climatiques.

#### **Sources des citations**

1. High-Resolution Early Warning Systems Using DL: Part I \- Elevation-Integrated Temperature and Precipitation SRGAN Downscaling (E-TEPS) \- Preprints.org, consulté le novembre 30, 2025, [https://www.preprints.org/manuscript/202408.1420](https://www.preprints.org/manuscript/202408.1420)  
2. Deep learning super-resolution for temperature data downscaling: a comprehensive study using residual networks \- Frontiers, consulté le novembre 30, 2025, [https://www.frontiersin.org/journals/climate/articles/10.3389/fclim.2025.1572428/full](https://www.frontiersin.org/journals/climate/articles/10.3389/fclim.2025.1572428/full)  
3. PrithviWxC Foundation Model Validation on Weather Downscaling for Cross Domain Learning \- CO Meeting Organizer, consulté le novembre 30, 2025, [https://meetingorganizer.copernicus.org/EGU25/EGU25-17360.html?pdf](https://meetingorganizer.copernicus.org/EGU25/EGU25-17360.html?pdf)  
4. ERA5-Land | ECMWF, consulté le novembre 30, 2025, [https://www.ecmwf.int/en/era5-land](https://www.ecmwf.int/en/era5-land)  
5. ERA5-Land hourly data from 1950 to present \- Climate Data Store, consulté le novembre 30, 2025, [https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land)  
6. Gap Filling Cloudy Sentinel-2 NDVI and NDWI Pixels with Multi-Frequency Denoised C-Band and L-Band Synthetic Aperture Radar (SAR), Texture, and Shallow Learning Techniques \- MDPI, consulté le novembre 30, 2025, [https://www.mdpi.com/2072-4292/14/17/4221](https://www.mdpi.com/2072-4292/14/17/4221)  
7. Reconstruction of a Monthly 1 km NDVI Time Series Product in China Using Random Forest Methodology \- MDPI, consulté le novembre 30, 2025, [https://www.mdpi.com/2072-4292/15/13/3353](https://www.mdpi.com/2072-4292/15/13/3353)  
8. Reconstructing systematically missing NDVI time series in cropland: A GAN-based approach using optical and SAR data | Request PDF \- ResearchGate, consulté le novembre 30, 2025, [https://www.researchgate.net/publication/397152050\_Reconstructing\_systematically\_missing\_NDVI\_time\_series\_in\_cropland\_A\_GAN-based\_approach\_using\_optical\_and\_SAR\_data](https://www.researchgate.net/publication/397152050_Reconstructing_systematically_missing_NDVI_time_series_in_cropland_A_GAN-based_approach_using_optical_and_SAR_data)  
9. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications, consulté le novembre 30, 2025, [https://essd.copernicus.org/articles/13/4349/2021/](https://essd.copernicus.org/articles/13/4349/2021/)  
10. Comparison of Reanalysis and Observational Precipitation Datasets Including ERA5 and WFDE5 \- MDPI, consulté le novembre 30, 2025, [https://www.mdpi.com/2073-4433/12/11/1462](https://www.mdpi.com/2073-4433/12/11/1462)  
11. Handling large geospatial datasets for dynamic WebGIS application with PostGIS, Mapbox, consulté le novembre 30, 2025, [https://gis.stackexchange.com/questions/482052/handling-large-geospatial-datasets-for-dynamic-webgis-application-with-postgis](https://gis.stackexchange.com/questions/482052/handling-large-geospatial-datasets-for-dynamic-webgis-application-with-postgis)  
12. Adversarial super-resolution of climatological wind and solar data | Request PDF, consulté le novembre 30, 2025, [https://www.researchgate.net/publication/342737730\_Adversarial\_super-resolution\_of\_climatological\_wind\_and\_solar\_data](https://www.researchgate.net/publication/342737730_Adversarial_super-resolution_of_climatological_wind_and_solar_data)  
13. A FOUNDATION MODEL FOR WEATHER AND CLIMATE \- OpenReview, consulté le novembre 30, 2025, [https://openreview.net/pdf/f3f68ab2ffb0f0258e67c2d0f1a9f361d78aad55.pdf](https://openreview.net/pdf/f3f68ab2ffb0f0258e67c2d0f1a9f361d78aad55.pdf)  
14. Prithvi-weather-climate: Advancing Our Understanding of the Atmosphere | NASA Earthdata, consulté le novembre 30, 2025, [https://www.earthdata.nasa.gov/news/blog/prithvi-weather-climate-advancing-our-understanding-atmosphere](https://www.earthdata.nasa.gov/news/blog/prithvi-weather-climate-advancing-our-understanding-atmosphere)  
15. Prithvi WxC: Foundation Model for Weather and Climate \- arXiv, consulté le novembre 30, 2025, [https://arxiv.org/html/2409.13598v1](https://arxiv.org/html/2409.13598v1)  
16. Physics-Informed and Explainable Graph Neural Networks for Generalizable Urban Building Energy Modeling \- MDPI, consulté le novembre 30, 2025, [https://www.mdpi.com/2076-3417/15/16/8854](https://www.mdpi.com/2076-3417/15/16/8854)  
17. DeepUrbanDownscale: A physics informed deep learning framework for high-resolution urban surface temperature estimation via 3D point clouds | Request PDF \- ResearchGate, consulté le novembre 30, 2025, [https://www.researchgate.net/publication/357394405\_DeepUrbanDownscale\_A\_physics\_informed\_deep\_learning\_framework\_for\_high-resolution\_urban\_surface\_temperature\_estimation\_via\_3D\_point\_clouds](https://www.researchgate.net/publication/357394405_DeepUrbanDownscale_A_physics_informed_deep_learning_framework_for_high-resolution_urban_surface_temperature_estimation_via_3D_point_clouds)  
18. Session PM7 \- CO Meeting Organizer, consulté le novembre 30, 2025, [https://meetingorganizer.copernicus.org/ICUC12/session/54439](https://meetingorganizer.copernicus.org/ICUC12/session/54439)  
19. ibm-granite/granite-geospatial-wxc-downscaling \- Hugging Face, consulté le novembre 30, 2025, [https://huggingface.co/ibm-granite/granite-geospatial-wxc-downscaling](https://huggingface.co/ibm-granite/granite-geospatial-wxc-downscaling)  
20. granite-wxc \- Repository for IBM weather downscaling model \- GitHub, consulté le novembre 30, 2025, [https://github.com/IBM/granite-wxc](https://github.com/IBM/granite-wxc)  
21. \[2506.22447\] Vision Transformers for Multi-Variable Climate Downscaling: Emulating Regional Climate Models with a Shared Encoder and Multi-Decoder Architecture \- arXiv, consulté le novembre 30, 2025, [https://arxiv.org/abs/2506.22447](https://arxiv.org/abs/2506.22447)  
22. (PDF) Vision Transformers for Multi-Variable Climate Downscaling: Emulating Regional Climate Models with a Shared Encoder and Multi-Decoder Architecture \- ResearchGate, consulté le novembre 30, 2025, [https://www.researchgate.net/publication/393183867\_Vision\_Transformers\_for\_Multi-Variable\_Climate\_Downscaling\_Emulating\_Regional\_Climate\_Models\_with\_a\_Shared\_Encoder\_and\_Multi-Decoder\_Architecture](https://www.researchgate.net/publication/393183867_Vision_Transformers_for_Multi-Variable_Climate_Downscaling_Emulating_Regional_Climate_Models_with_a_Shared_Encoder_and_Multi-Decoder_Architecture)  
23. Perkins skill score across the domain for (top) daily precipitation and... \- ResearchGate, consulté le novembre 30, 2025, [https://www.researchgate.net/figure/Perkins-skill-score-across-the-domain-for-top-daily-precipitation-and-bottom-daily\_fig3\_281707759](https://www.researchgate.net/figure/Perkins-skill-score-across-the-domain-for-top-daily-precipitation-and-bottom-daily_fig3_281707759)  
24. CCdownscaling: an open-source Python package for multivariable statistical climate model downscaling V1.0 \- EGUsphere, consulté le novembre 30, 2025, [https://egusphere.copernicus.org/preprints/2022/egusphere-2022-282/egusphere-2022-282.pdf](https://egusphere.copernicus.org/preprints/2022/egusphere-2022-282/egusphere-2022-282.pdf)  
25. Selecting and Downscaling a Set of Climate Models for Projecting Climatic Change for Impact Assessment in the Upper Indus Basin (UIB) \- MDPI, consulté le novembre 30, 2025, [https://www.mdpi.com/2225-1154/6/4/89](https://www.mdpi.com/2225-1154/6/4/89)  
26. Home | deck.gl, consulté le novembre 30, 2025, [https://deck.gl/](https://deck.gl/)  
27. Performance Optimization | deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/developer-guide/performance](https://deck.gl/docs/developer-guide/performance)  
28. Using deck.gl with React, consulté le novembre 30, 2025, [https://deck.gl/docs/get-started/using-with-react](https://deck.gl/docs/get-started/using-with-react)  
29. DeckGL Integration | React Google Maps \- GitHub Pages, consulté le novembre 30, 2025, [https://visgl.github.io/react-google-maps/docs/guides/deckgl-integration](https://visgl.github.io/react-google-maps/docs/guides/deckgl-integration)  
30. HeatmapLayer | deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer](https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer)  
31. What's New | deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/whats-new](https://deck.gl/docs/whats-new)  
32. HeatmapTileLayer \- Deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/api-reference/carto/heatmap-tile-layer](https://deck.gl/docs/api-reference/carto/heatmap-tile-layer)  
33. Animations and Transitions | deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/developer-guide/animations-and-transitions](https://deck.gl/docs/developer-guide/animations-and-transitions)  
34. RasterTileLayer \- Deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/api-reference/carto/raster-tile-layer](https://deck.gl/docs/api-reference/carto/raster-tile-layer)  
35. Frameworks of vis.gl, consulté le novembre 30, 2025, [https://vis.gl/frameworks](https://vis.gl/frameworks)  
36. react-scrollama \- NPM, consulté le novembre 30, 2025, [https://www.npmjs.com/package/react-scrollama](https://www.npmjs.com/package/react-scrollama)  
37. Scrollytelling Project – @lachlanjc/edu, consulté le novembre 30, 2025, [https://edu.lachlanjc.com/2022-09-26\_ind\_scrollytelling\_project](https://edu.lachlanjc.com/2022-09-26_ind_scrollytelling_project)  
38. FlyToInterpolator \- Deck.gl, consulté le novembre 30, 2025, [https://deck.gl/docs/api-reference/core/fly-to-interpolator](https://deck.gl/docs/api-reference/core/fly-to-interpolator)  
39. A Probabilistic U-Net Approach to Downscaling Climate Simulations \- arXiv, consulté le novembre 30, 2025, [https://arxiv.org/html/2511.03197v1](https://arxiv.org/html/2511.03197v1)  
40. I automated the entire Urban Heat Island analysis workflow \- from satellite data to ML predictions in one Python script : r/gis \- Reddit, consulté le novembre 30, 2025, [https://www.reddit.com/r/gis/comments/1mm4ugh/i\_automated\_the\_entire\_urban\_heat\_island\_analysis/](https://www.reddit.com/r/gis/comments/1mm4ugh/i_automated_the_entire_urban_heat_island_analysis/)  
41. 09 Exercises 1: Intro and Global Temperature Analysis, consulté le novembre 30, 2025, [https://uwgda-jupyterbook.readthedocs.io/en/latest/modules/09\_NDarrays\_xarray\_ERA5/09\_NDarrays\_xarray\_ERA5\_Part1\_exercises.html](https://uwgda-jupyterbook.readthedocs.io/en/latest/modules/09_NDarrays_xarray_ERA5/09_NDarrays_xarray_ERA5_Part1_exercises.html)