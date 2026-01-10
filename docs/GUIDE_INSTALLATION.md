# Guide d'Installation

## 📋 Prérequis

### Système d'exploitation
- **Windows** 10/11
- **macOS** 10.14+
- **Linux** (Ubuntu 20.04+, Debian, Fedora, etc.)

### Logiciels requis

#### Python
- **Version minimale** : Python 3.10
- **Version recommandée** : Python 3.11 ou 3.12

**Vérifier votre version Python** :
```bash
python --version
# ou
python3 --version
```

**Installer Python** :
- **Windows** : [python.org/downloads](https://www.python.org/downloads/)
- **macOS** : `brew install python@3.11` ou via python.org
- **Linux** : `sudo apt install python3.11 python3-pip` (Ubuntu/Debian)

#### Pip (gestionnaire de paquets)
Normalement installé avec Python. Vérification :
```bash
pip --version
# ou
pip3 --version
```

#### Git (optionnel, pour cloner le dépôt)
```bash
git --version
```

Installation si nécessaire :
- **Windows** : [git-scm.com](https://git-scm.com/)
- **macOS** : `brew install git`
- **Linux** : `sudo apt install git`

## 📥 Téléchargement du Projet

### Méthode 1 : Clonage Git (recommandé)

```bash
# Cloner le dépôt
git clone <URL_DU_DEPOT>

# Naviguer dans le répertoire
cd modele-d-evaluation-des-aliments
```

### Méthode 2 : Téléchargement ZIP

1. Télécharger l'archive ZIP du projet
2. Extraire dans un répertoire de votre choix
3. Ouvrir un terminal dans ce répertoire

## 🔧 Installation des Dépendances

### Étape 1 : Créer un Environnement Virtuel (Recommandé)

Un environnement virtuel isole les dépendances du projet.

#### Sur Windows
```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate
```

#### Sur macOS/Linux
```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate
```

**Vérification** : Le prompt du terminal devrait afficher `(.venv)` au début.

### Étape 2 : Mettre à Jour Pip

```bash
# Assurer que pip est à jour
pip install --upgrade pip
```

### Étape 3 : Installer les Dépendances

```bash
# Installer toutes les dépendances depuis requirements.txt
pip install -r requirements.txt
```

**Temps estimé** : 1-3 minutes selon votre connexion internet.

### Étape 4 : Vérifier l'Installation

```bash
# Test rapide des imports
python -c "import pandas, numpy, streamlit, yaml, sklearn; print('✅ Installation réussie !')"
```

Si aucune erreur n'apparaît, l'installation est complète.

## 📦 Dépendances Installées

Le fichier `requirements.txt` installe les bibliothèques suivantes :

| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| `pandas` | >= 2.0.0 | Manipulation de données tabulaires |
| `numpy` | >= 1.24.0 | Calculs numériques |
| `streamlit` | >= 1.28.0 | Interface web interactive |
| `pyyaml` | >= 6.0 | Lecture fichiers de configuration |
| `scikit-learn` | >= 1.3.0 | Métriques d'évaluation |
| `matplotlib` | >= 3.7.0 | Visualisations graphiques |
| `seaborn` | >= 0.12.0 | Visualisations statistiques |
| `openpyxl` | >= 3.1.0 | Lecture/écriture fichiers Excel |
| `requests` | >= 2.31.0 | Requêtes API Open Food Facts |

## 🗂️ Structure des Répertoires

Après installation, votre projet devrait avoir cette structure :

```
modele-d-evaluation-des-aliments/
├── .venv/                    # Environnement virtuel (créé)
├── app/                      # Code source
├── config/                   # Fichiers de configuration
├── data/                     # Données d'entrée
├── docs/                     # Documentation
├── outputs/                  # Résultats générés
│   ├── excel/               # Exports Excel
│   └── reports/             # Rapports graphiques
├── tests/                    # Tests unitaires
├── README.md
└── requirements.txt
```

## ✅ Validation de l'Installation

### Test 1 : Modules Python

```bash
# Tester les imports principaux
python -c "
from app.nutriscore import compute_nutriscore
from app.electre_tri import ElectreTri
from app.normalize import DataNormalizer
print('✅ Tous les modules sont accessibles')
"
```

### Test 2 : Configuration

```bash
# Vérifier les fichiers de configuration
python -c "
import yaml
from pathlib import Path

config_electre = Path('config/electre.yml')
config_columns = Path('config/columns.yml')

assert config_electre.exists(), 'electre.yml manquant'
assert config_columns.exists(), 'columns.yml manquant'

print('✅ Fichiers de configuration présents')
"
```

### Test 3 : Interface Streamlit

```bash
# Lancer l'interface (doit ouvrir dans le navigateur)
streamlit run app/ui_streamlit.py
```

Si une page web s'ouvre à `http://localhost:8501`, l'installation est complète !

**Arrêter Streamlit** : `Ctrl+C` dans le terminal

## 🔧 Résolution de Problèmes

### Erreur : "Python n'est pas reconnu..."

**Windows** : Ajouter Python au PATH système
1. Rechercher "Variables d'environnement"
2. Éditer la variable `Path`
3. Ajouter le chemin d'installation de Python

**Alternative** : Utiliser `py` au lieu de `python`
```bash
py --version
py -m venv .venv
```

### Erreur : "pip install failed"

**Problème réseau** :
```bash
# Utiliser un timeout plus long
pip install -r requirements.txt --timeout 120
```

**Problème de permissions** (Linux/macOS) :
```bash
# NE PAS utiliser sudo dans un environnement virtuel
# Si nécessaire :
pip install --user -r requirements.txt
```

### Erreur : "ModuleNotFoundError"

L'environnement virtuel n'est pas activé.

**Solution** :
```bash
# Activer l'environnement
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Vérifier
which python  # doit pointer vers .venv
```

### Erreur : "streamlit: command not found"

Streamlit non installé ou pas dans le PATH.

**Solution** :
```bash
# Réinstaller Streamlit
pip install --force-reinstall streamlit

# Lancer avec Python
python -m streamlit run app/ui_streamlit.py
```

### Erreur YAML : "yaml.scanner.ScannerError"

Fichier de configuration mal formaté.

**Solution** :
1. Ouvrir `config/electre.yml` ou `config/columns.yml`
2. Vérifier l'indentation (espaces, pas de tabulations)
3. Valider la syntaxe YAML sur [yamllint.com](http://www.yamllint.com/)

### Problème : Interface Streamlit ne s'ouvre pas

**Vérifier le port** :
```bash
# Port 8501 peut-être occupé
streamlit run app/ui_streamlit.py --server.port 8502
```

**Ouvrir manuellement** :
- Navigateur : `http://localhost:8501`

## 🔄 Mise à Jour du Projet

### Mise à jour du code

```bash
# Si Git est utilisé
git pull origin main

# Réinstaller les dépendances (au cas où)
pip install -r requirements.txt --upgrade
```

### Mise à jour des dépendances

```bash
# Mettre à jour toutes les bibliothèques
pip install --upgrade -r requirements.txt

# Ou individuellement
pip install --upgrade pandas streamlit
```

## 🗑️ Désinstallation

### Supprimer l'environnement virtuel

```bash
# Désactiver l'environnement
deactivate

# Supprimer le dossier .venv
# Windows
rmdir /s .venv

# macOS/Linux
rm -rf .venv
```

### Supprimer le projet

Supprimer simplement le dossier du projet.

## 📞 Support

En cas de problème persistant :

1. **Vérifier la documentation** : `docs/`
2. **Consulter les logs** : messages d'erreur détaillés
3. **Tests unitaires** : `pytest tests/` pour diagnostic

## ⚡ Installation Rapide (Résumé)

```bash
# 1. Cloner/télécharger le projet
git clone <URL_DU_DEPOT>
cd modele-d-evaluation-des-aliments

# 2. Créer environnement virtuel
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OU
.venv\Scripts\activate      # Windows

# 3. Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Vérifier installation
python -c "import streamlit; print('✅ OK')"

# 5. Lancer l'application
streamlit run app/ui_streamlit.py
```

## 🎓 Prochaines Étapes

Une fois l'installation terminée :
1. Lire [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)
2. Explorer [METHODES_CALCUL.md](METHODES_CALCUL.md)
3. Consulter [API_REFERENCE.md](API_REFERENCE.md) pour le développement

---

**Date de mise à jour** : Décembre 2025  
**Version** : 1.0
