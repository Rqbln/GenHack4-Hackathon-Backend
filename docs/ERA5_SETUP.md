# 🌍 Configuration ERA5 - Copernicus CDS

Guide pour configurer l'accès aux données ERA5.

## 📋 Prérequis

### 1. Créer un compte Copernicus CDS

1. Aller sur : https://cds.climate.copernicus.eu/
2. Cliquer sur "Register" (en haut à droite)
3. Remplir le formulaire d'inscription
4. Confirmer l'email
5. Se connecter

### 2. Accepter les termes et conditions

1. Une fois connecté, aller sur : https://cds.climate.copernicus.eu/user
2. Descendre jusqu'à "Terms and conditions"
3. Cocher la case et accepter

### 3. ⚠️ Accepter la licence ERA5 dataset (OBLIGATOIRE)

**IMPORTANT** : Avant d'utiliser l'API, il faut accepter la licence du dataset ERA5 :

1. Aller sur : https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download
2. Scroller en bas jusqu'à la section **"Terms of use"**
3. Cliquer sur **"Accept Terms"** pour la licence CC-BY
4. Attendre 1-2 minutes que l'acceptation soit propagée au système API

> 💡 **Note** : Sans cette étape, les requêtes API retournent une erreur `403 Forbidden: required licences not accepted`

### 4. Récupérer l'API key

1. Aller sur votre page utilisateur : https://cds.climate.copernicus.eu/user
2. Copier votre **API Key** (longue chaîne de caractères avec des tirets)

---

## ⚙️ Configuration Locale

### Créer le fichier ~/.cdsapirc

```bash
# Créer le fichier de configuration
nano ~/.cdsapirc
```

### Contenu du fichier

```
url: https://cds.climate.copernicus.eu/api
key: VOTRE_API_KEY
```

**Remplacer `VOTRE_API_KEY`** par l'API Key copiée depuis votre profil CDS.

**Exemple** :
```
url: https://cds.climate.copernicus.eu/api
key: 1610840b-8925-4df9-a952-8276366bfd69
```

### Permissions

```bash
chmod 600 ~/.cdsapirc
```

---

## 🧪 Tester la Configuration

### Option 1 : Test Python direct

```bash
cd /root/GenHack4-Hackathon-Vertex
source venv/bin/activate
pip install cdsapi

python -c "import cdsapi; c = cdsapi.Client(); print('✅ CDS API configured correctly!')"
```

### Option 2 : Test avec le client ERA5

```bash
cd /root/GenHack4-Hackathon-Vertex
source venv/bin/activate

python src/era5_client.py
```

Cela téléchargera une petite zone test (Paris, 1 jour) pour vérifier que tout fonctionne.

---

## 🚀 Utilisation

### Télécharger des données ERA5

```python
from src.era5_client import ERA5Client

client = ERA5Client()

# Télécharger température pour Paris
files = client.download_era5(
    variables=["t2m"],
    bbox=[2.2, 48.8, 2.5, 48.9],  # Paris
    start_date="2022-07-15",
    end_date="2022-07-17",
    output_dir=Path("/tmp/era5_test")
)

# Convertir en GeoTIFF
for var, nc_file in files.items():
    tif_file = Path(f"/tmp/era5_test/{var}.tif")
    client.convert_to_geotiff(nc_file, tif_file, var)
```

### Lancer la pipeline avec données réelles

```bash
# Avec la config real data
docker run --rm \
  -v $(PWD)/configs:/app/configs \
  -v ~/.cdsapirc:/root/.cdsapirc \
  -v /tmp/genhack:/tmp/genhack \
  europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:latest \
  --config configs/paris_2022_real.yml
```

---

## 📊 Variables Disponibles

| Code | Description | Unité |
|------|-------------|-------|
| `t2m` | Température 2m | K (Kelvin) |
| `tx` | Température max | K |
| `tn` | Température min | K |
| `rh` | Humidité relative | % |
| `u10` | Vent U 10m | m/s |
| `v10` | Vent V 10m | m/s |
| `tp` | Précipitations | m |
| `sp` | Pression surface | Pa |

---

## ⚠️ Limitations

### Quota CDS

- **Limite de téléchargement** : ~2000 requêtes/jour
- **Taille max par requête** : ~100 MB
- **Files d'attente** : Possible pendant les heures de pointe

### Résolution ERA5

- **Spatiale** : ~25 km (0.25°)
- **Temporelle** : Horaire
- **Latence** : ~5 jours (données récentes)

### Temps de Téléchargement

- **1 variable, 1 jour, petite zone** : ~30 secondes
- **1 variable, 1 mois, grande zone** : ~5-10 minutes
- **Plusieurs variables, longue période** : Peut prendre plusieurs heures

---

## 🐛 Dépannage

### Erreur "Client not authorized"

```bash
# Vérifier que ~/.cdsapirc existe et contient l'API key
cat ~/.cdsapirc

# Vérifier les permissions
ls -la ~/.cdsapirc  # Devrait être 600
```

### Erreur "HTTPError 401"

- API key invalide ou expirée
- Recréer l'API key sur le site CDS
- Mettre à jour ~/.cdsapirc

### Erreur "Request too large"

- Réduire la période temporelle
- Réduire la zone géographique
- Télécharger les variables séparément

### Timeout

- CDS peut être lent aux heures de pointe
- Utiliser `timeout` dans les requêtes
- Retry avec backoff exponentiel

---

## 📚 Ressources

- **Documentation CDS** : https://cds.climate.copernicus.eu/api-how-to
- **ERA5 Documentation** : https://confluence.ecmwf.int/display/CKB/ERA5
- **Python API** : https://pypi.org/project/cdsapi/
- **Support** : https://support.ecmwf.int/

---

**Dernière mise à jour** : 10 novembre 2025
