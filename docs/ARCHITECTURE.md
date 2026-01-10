# Architecture du Projet

## 📋 Vue d'ensemble

Ce projet implémente un système d'évaluation nutritionnelle des produits alimentaires en combinant deux méthodes :
- **Nutri-Score** : Système de notation officiel français (A à E)
- **ELECTRE TRI** : Méthode d'aide à la décision multicritère

## 🏗️ Structure du Projet

```
modele-d-evaluation-des-aliments/
│
├── app/                          # Code source principal
│   ├── __init__.py
│   ├── electre_tri.py           # Implémentation ELECTRE TRI
│   ├── nutriscore.py            # Calcul Nutri-Score officiel
│   ├── normalize.py             # Normalisation des données
│   ├── eval.py                  # Évaluation et comparaison
│   ├── io.py                    # Lecture/écriture fichiers Excel
│   ├── api_openfoodfacts.py     # Interface API Open Food Facts
│   ├── ui_streamlit.py          # Point d'entrée interface web
│   │
│   ├── ui/                      # Modules interface utilisateur
│   │   ├── __init__.py
│   │   ├── setup.py            # Configuration Streamlit
│   │   ├── sidebar.py          # Barre latérale
│   │   ├── components.py       # Composants réutilisables
│   │   ├── cache_utils.py      # Gestion du cache
│   │   └── tabs/               # Onglets de l'interface
│   │       ├── home.py         # Page d'accueil
│   │       ├── unitary.py      # Calcul unitaire
│   │       └── dataset.py      # Traitement par lots
│   │
│   └── utils/                   # Utilitaires
│       └── paths.py            # Gestion des chemins
│
├── config/                      # Fichiers de configuration
│   ├── columns.yml             # Mapping des colonnes Excel
│   └── electre.yml             # Paramètres ELECTRE TRI
│
├── data/                        # Données d'entrée
│   └── open_food_facts_cereales_clean.csv
│
├── outputs/                     # Fichiers générés
│   ├── excel/                  # Exports Excel
│   └── reports/                # Rapports PDF/PNG
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md         # Ce fichier
│   ├── GUIDE_INSTALLATION.md   # Guide d'installation
│   ├── GUIDE_UTILISATION.md    # Guide utilisateur
│   ├── METHODES_CALCUL.md      # Détails des méthodes
│   └── API_REFERENCE.md        # Référence API
│
├── tests/                       # Tests unitaires
│   ├── test_complete_electre.py
│   ├── test_corrections.py
│   ├── test_metriques.py
│   └── test_validation.py
│
├── README.md                    # Documentation principale
└── requirements.txt             # Dépendances Python
```

## 🔄 Flux de Données

### 1. Chargement des Données

```
Fichier Excel/CSV → io.py → DataFrame normalisé
                      ↓
              Mapping colonnes (columns.yml)
                      ↓
              Validation structure
```

### 2. Normalisation

```
Données brutes → normalize.py
                    ↓
    Conversions d'unités:
    - kJ ↔ kcal
    - sodium ↔ sel
    - mg ↔ g
                    ↓
    Nettoyage des valeurs
                    ↓
    Données prêtes pour calcul
```

### 3. Calculs

```
                Données normalisées
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
   nutriscore.py              electre_tri.py
   (Score + Label)            (Catégorie A'-E')
        ↓                             ↓
        └──────────────┬──────────────┘
                       ↓
                   eval.py
           (Comparaison + Métriques)
```

### 4. Présentation

```
Résultats
    ↓
ui_streamlit.py
    ↓
┌───┴───┐
│ Tabs  │
├───────┤
│ Home  │ → Présentation du projet
│Unitary│ → Calcul pour 1 produit
│Dataset│ → Traitement par lots
└───────┘
```

## 🧩 Modules Principaux

### `electre_tri.py` - Méthode ELECTRE TRI

**Objectif** : Classer les produits en catégories (A' à E') selon une approche multicritère.

**Composants clés** :
- `ElectreTri` : Classe principale
- `_load_config()` : Charge les paramètres depuis YAML
- `_compute_concordance()` : Calcule les indices de concordance
- `pessimistic_sorting()` : Procédure de tri pessimiste
- `optimistic_sorting()` : Procédure de tri optimiste

**Principe** :
1. Définition de profils limites (seuils entre catégories)
2. Comparaison du produit aux profils
3. Classification selon concordance globale

### `nutriscore.py` - Calcul Nutri-Score

**Objectif** : Calculer le score et le label Nutri-Score officiel.

**Composants clés** :
- `DEFAULT_POINT_TABLES` : Barèmes officiels 2025
- `_get_points_from_table()` : Attribution des points
- `compute_nutriscore()` : Calcul du score final
- `get_nutriscore_label()` : Détermination du label A-E

**Principe** :
1. Points défavorables : énergie + graisses saturées + sucres + sel
2. Points favorables : protéines + fibres + fruits/légumes
3. Score final = défavorables - favorables
4. Conversion score → label (A à E)

### `normalize.py` - Normalisation des Données

**Objectif** : Uniformiser les données pour garantir la cohérence des calculs.

**Composants clés** :
- `DataNormalizer` : Classe de normalisation
- `parse_energy_string()` : Parse chaînes d'énergie
- `parse_weight_string()` : Parse poids avec unités
- `normalize_dataframe()` : Normalise tout le DataFrame

**Transformations** :
- Énergie : kcal → kJ (× 4.184)
- Sodium : mg → sel en g (× 0.0025)
- Graisses saturées : mg → g
- Sucres : harmonisation des formats
- Fibres : gestion valeurs manquantes

### `eval.py` - Évaluation et Comparaison

**Objectif** : Comparer Nutri-Score et ELECTRE TRI, générer des métriques.

**Composants clés** :
- `NutriScoreElectreEvaluator` : Classe d'évaluation
- `compute_confusion_matrix()` : Matrice de confusion
- `compute_metrics()` : Précision, F1-score, MAE
- `generate_comparison_report()` : Rapport visuel complet

**Métriques calculées** :
- Exactitude (accuracy)
- Score F1 (macro)
- Erreur absolue moyenne (MAE)
- Distribution des classifications
- Concordance par catégorie

### `io.py` - Gestion des Fichiers

**Objectif** : Charger et sauvegarder les données avec mapping automatique.

**Composants clés** :
- `ExcelDataLoader` : Lecture fichiers Excel
- `_load_column_config()` : Charge mapping colonnes
- `_find_column_match()` : Trouve correspondances
- `save_results()` : Export résultats

**Fonctionnalités** :
- Détection automatique des colonnes
- Support multi-noms (synonymes)
- Validation structure
- Export Excel avec formatage

### `ui_streamlit.py` - Interface Web

**Objectif** : Interface utilisateur interactive pour calculs et visualisations.

**Structure** :
- `setup_page_and_logging()` : Configuration Streamlit
- `render_sidebar()` : Paramètres ELECTRE
- Onglet **Accueil** : Documentation
- Onglet **Calcul Unitaire** : 1 produit
- Onglet **Dataset** : Traitement par lots

**Fonctionnalités** :
- Saisie manuelle des valeurs nutritionnelles
- Import fichiers Excel/CSV
- Recherche Open Food Facts
- Visualisations interactives
- Export résultats

## ⚙️ Fichiers de Configuration

### `config/electre.yml`

Définit les paramètres ELECTRE TRI :

```yaml
# Poids des critères (importance relative)
weights:
  energy: 0.15
  saturated_fat: 0.15
  sugars: 0.20
  salt: 0.15
  protein: 0.10
  fiber: 0.10
  fruits_veg: 0.15

# Direction d'optimisation (min/max)
directions:
  energy: min
  saturated_fat: min
  # ...

# Profils limites (seuils entre catégories)
profiles:
  b1:  # Limite A'/B'
    energy: 1000
    # ...
  b2:  # Limite B'/C'
    energy: 1500
    # ...

# Seuil de concordance (0-1)
lambda: 0.75
```

### `config/columns.yml`

Mapping des noms de colonnes :

```yaml
Produit:
  - Produit
  - product_name
  - nom_produit

valeur energetique (KJ):
  - valeur energetique (KJ)
  - energy_kj
  - energie
  # ...
```

## 🔗 Dépendances entre Modules

```
io.py (base)
    ↓
normalize.py (dépend de: io)
    ↓
┌───┴───────────┐
↓               ↓
nutriscore.py   electre_tri.py
(dépend de:     (dépend de:
normalize)      normalize, config)
    ↓               ↓
    └───────┬───────┘
            ↓
        eval.py
    (dépend de: tous)
            ↓
    ui_streamlit.py
    (dépend de: tous)
```

## 🎯 Points d'Extension

### Ajouter un Nouveau Critère

1. Modifier `config/electre.yml` :
   - Ajouter le poids
   - Définir la direction
   - Ajouter aux profils

2. Modifier `normalize.py` :
   - Ajouter la normalisation si nécessaire

3. Modifier `electre_tri.py` :
   - Aucune modification requise (générique)

### Ajouter une Nouvelle Métrique

1. Modifier `eval.py` :
   - Ajouter méthode dans `NutriScoreElectreEvaluator`
   - Intégrer dans `compute_metrics()`

2. Modifier `ui/tabs/dataset.py` :
   - Afficher la nouvelle métrique

### Ajouter un Nouveau Format d'Export

1. Modifier `io.py` :
   - Créer nouvelle méthode `save_xxx()`

2. Modifier interface utilisateur :
   - Ajouter bouton d'export

## 🔐 Gestion des Erreurs

Le projet utilise le module `logging` Python :

```python
import logging
logger = logging.getLogger(__name__)

# Niveaux de log utilisés :
logger.info()     # Informations générales
logger.warning()  # Avertissements (non bloquants)
logger.error()    # Erreurs (bloquantes)
logger.debug()    # Détails techniques
```

**Stratégie** :
- Validation des entrées en amont
- Gestion des valeurs manquantes (NaN)
- Messages d'erreur explicites pour l'utilisateur
- Logs techniques pour le débogage

## 📊 Performance

**Temps de traitement moyen** :
- 1 produit : < 10 ms
- 100 produits : < 1 s
- 1000 produits : < 10 s

**Optimisations** :
- Calculs vectorisés avec NumPy/Pandas
- Cache Streamlit (`@st.cache_data`)
- Chargement paresseux des données
- Validation incrémentale

## 🧪 Tests

Tests unitaires dans `/tests/` :
- `test_complete_electre.py` : Tests ELECTRE TRI
- `test_metriques.py` : Validation métriques
- `test_validation.py` : Validation données

**Exécuter les tests** :
```bash
pytest tests/
```

## 📝 Conventions de Code

- **Style** : PEP 8
- **Docstrings** : Format Google
- **Type hints** : Python 3.10+
- **Imports** : Ordre alphabétique par groupe
- **Nommage** :
  - Variables : `snake_case`
  - Fonctions : `snake_case()`
  - Classes : `PascalCase`
  - Constantes : `UPPER_CASE`

## 🔄 Workflow Git (Recommandé)

```
main (production)
  ↓
develop (intégration)
  ↓
feature/nouvelle-fonctionnalite (développement)
```

## 📚 Ressources

- [Nutri-Score officiel](https://www.santepubliquefrance.fr/nutriscore)
- [ELECTRE methods](https://en.wikipedia.org/wiki/ELECTRE)
- [Streamlit docs](https://docs.streamlit.io)
- [Pandas docs](https://pandas.pydata.org/docs/)
