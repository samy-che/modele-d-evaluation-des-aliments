# API Reference - Documentation Complète

## 📖 Vue d'ensemble

Ce document détaille toutes les fonctions et classes publiques du projet.
Utilisez cette référence pour intégrer le code dans vos propres applications.

---

## Module `nutriscore.py`

### Classe `NutriScoreCalculator`

Calculateur Nutri-Score avec algorithme officiel complet.

#### Initialisation

```python
from app.nutriscore import NutriScoreCalculator

calculator = NutriScoreCalculator(
    point_tables=None,  # Tables de barèmes personnalisées (optionnel)
    thresholds=None     # Seuils de labels personnalisés (optionnel)
)
```

#### Méthode `compute_score_and_label()`

Calcule le score et le label Nutri-Score complets.

**Signature** :
```python
def compute_score_and_label(
    energy_kj: float,
    saturated_fat_g: float,
    sugars_g: float,
    sodium_or_salt_value: float,
    fiber_g: float,
    protein_g: float,
    fruits_veg_percent: float,
    category: str = "general"
) -> Tuple[int, str, Dict]
```

**Paramètres** :
- `energy_kj` : Énergie en kJ/100g
- `saturated_fat_g` : Graisses saturées en g/100g
- `sugars_g` : Sucres en g/100g
- `sodium_or_salt_value` : Sodium (mg) ou sel (g) /100g
- `fiber_g` : Fibres en g/100g
- `protein_g` : Protéines en g/100g
- `fruits_veg_percent` : % fruits/légumes/légumineuses
- `category` : `"general"`, `"cheese"`, ou `"beverage"`

**Retourne** :
- `int` : Score Nutri-Score (-15 à 40+)
- `str` : Label (A, B, C, D, E)
- `Dict` : Détails de calcul

**Exemple** :
```python
calculator = NutriScoreCalculator()

score, label, details = calculator.compute_score_and_label(
    energy_kj=1650,
    saturated_fat_g=3.2,
    sugars_g=25,
    sodium_or_salt_value=0.9,
    fiber_g=5.5,
    protein_g=8,
    fruits_veg_percent=0,
    category="general"
)

print(f"Score: {score}, Label: {label}")
# Output: Score: 11, Label: C
```

#### Méthode `apply_to_dataframe()`

Applique le calcul Nutri-Score à un DataFrame complet.

**Signature** :
```python
def apply_to_dataframe(
    df: pd.DataFrame,
    colmap: Optional[Dict[str, str]] = None,
    default_category: str = "general"
) -> pd.DataFrame
```

**Paramètres** :
- `df` : DataFrame avec données nutritionnelles
- `colmap` : Mapping personnalisé des noms de colonnes
- `default_category` : Catégorie par défaut

**Retourne** :
- `pd.DataFrame` : DataFrame enrichi avec colonnes `ns_score_calc` et `ns_label_calc`

**Exemple** :
```python
import pandas as pd

df = pd.DataFrame({
    'energy_100g': [1650, 1200, 2000],
    'saturated_fat_100g': [3.2, 1.5, 5.0],
    'sugars_100g': [25, 8, 30],
    'sodium_100g': [900, 400, 1200],
    'proteins_100g': [8, 12, 6],
    'fiber_100g': [5.5, 7, 2],
    'fruits_veg_nuts_percent': [0, 60, 0]
})

calculator = NutriScoreCalculator()
df_with_nutriscore = calculator.apply_to_dataframe(df)

print(df_with_nutriscore[['ns_score_calc', 'ns_label_calc']])
```

### Fonctions Utilitaires

#### `compute_nutriscore_single()`

Fonction simplifiée pour calcul unitaire.

**Signature** :
```python
def compute_nutriscore_single(
    energy_kj: float = 0,
    saturated_fat_g: float = 0,
    sugars_g: float = 0,
    sodium_mg_or_salt_g: float = 0,
    fiber_g: float = 0,
    protein_g: float = 0,
    fruits_veg_nuts_percent: float = 0,
    category: str = "general"
) -> dict
```

**Retourne** :
```python
{
    "score": 11,
    "label": "C",
    "details": {...}
}
```

#### `apply_nutriscore()`

Fonction rapide pour DataFrame.

**Signature** :
```python
def apply_nutriscore(
    df: pd.DataFrame,
    category_col: str = None
) -> pd.DataFrame
```

---

## Module `electre_tri.py`

### Classe `ElectreTri`

Implémentation ELECTRE TRI-B avec profils limites.

#### Initialisation

```python
from app.electre_tri import ElectreTri

electre = ElectreTri(
    config_path="config/electre.yml"  # Chemin config (optionnel)
)
```

#### Méthode `classify_alternative()`

Classe une alternative selon ELECTRE TRI.

**Signature** :
```python
def classify_alternative(
    alternative: Dict[str, float],
    variant: str = "pessimistic"
) -> str
```

**Paramètres** :
- `alternative` : Dictionnaire `{critère: valeur}`
- `variant` : `"pessimistic"` ou `"optimistic"`

**Retourne** :
- `str` : Catégorie (A', B', C', D', E')

**Exemple** :
```python
electre = ElectreTri()

product = {
    'energy': 1650,
    'saturated_fat': 3.2,
    'sugars': 25,
    'salt': 0.9,
    'protein': 8,
    'fiber': 5.5,
    'fruits_veg': 0
}

category = electre.classify_alternative(product, variant="pessimistic")
print(f"Catégorie ELECTRE: {category}")
# Output: Catégorie ELECTRE: C'
```

### Fonctions Utilitaires

#### `electre_sorting()`

Applique ELECTRE TRI à un DataFrame complet.

**Signature** :
```python
def electre_sorting(
    df: pd.DataFrame,
    config_path: Optional[str] = None,
    variant: str = "pessimistic",
    lambda_threshold: Optional[float] = None,
    custom_weights: Optional[Dict[str, float]] = None
) -> pd.Series
```

**Paramètres** :
- `df` : DataFrame avec données
- `config_path` : Chemin configuration ELECTRE
- `variant` : Variante de tri
- `lambda_threshold` : Seuil de concordance (0-1)
- `custom_weights` : Poids personnalisés

**Retourne** :
- `pd.Series` : Série avec catégories assignées

**Exemple** :
```python
from app.electre_tri import electre_sorting

classifications = electre_sorting(
    df,
    variant="pessimistic",
    lambda_threshold=0.75,
    custom_weights={
        'energy': 0.20,
        'sugars': 0.25,
        'salt': 0.20,
        # ...
    }
)

df['electre_category'] = classifications
```

#### `classify_single_product()`

Classe un produit individuel avec détails.

**Signature** :
```python
def classify_single_product(
    criteria_values: Dict[str, float],
    config_path: Optional[str] = None,
    variant: str = "pessimistic",
    lambda_threshold: Optional[float] = None,
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, any]
```

**Retourne** :
```python
{
    'class': 'C\'',
    'variant': 'pessimistic',
    'concordances': {
        'S(a,b1)': 0.456,
        'S(a,b2)': 0.623,
        'S(a,b3)': 0.789,
        'S(a,b4)': 0.891
    },
    'lambda': 0.75
}
```

---

## Module `normalize.py`

### Classe `DataNormalizer`

Normalisation des données nutritionnelles.

#### Méthodes Statiques

##### `parse_energy_string()`

Parse une chaîne d'énergie avec unités.

**Signature** :
```python
@staticmethod
def parse_energy_string(energy_str: str) -> Tuple[float, str]
```

**Exemple** :
```python
from app.normalize import DataNormalizer

value, unit = DataNormalizer.parse_energy_string("433 kcal / 1,812 kj")
print(value, unit)  # 433.0, 'kcal'
```

##### `parse_weight_string()`

Parse une chaîne de poids avec unités.

**Signature** :
```python
@staticmethod
def parse_weight_string(
    weight_str: str,
    is_sodium: bool = False
) -> float
```

**Exemple** :
```python
weight = DataNormalizer.parse_weight_string("3,4 g")
print(weight)  # 3.4

sodium = DataNormalizer.parse_weight_string("800 mg", is_sodium=True)
print(sodium)  # 800.0 (en mg)
```

##### `normalize_dataframe()`

Normalise un DataFrame complet.

**Signature** :
```python
@staticmethod
def normalize_dataframe(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, Dict]
```

**Retourne** :
- `pd.DataFrame` : DataFrame normalisé
- `Dict` : Rapport de normalisation

**Exemple** :
```python
from app.normalize import DataNormalizer

df_normalized, report = DataNormalizer.normalize_dataframe(df)

print(report['conversions_applied'])
print(report['missing_values_filled'])
```

---

## Module `eval.py`

### Classe `NutriScoreElectreEvaluator`

Comparaison et évaluation Nutri-Score vs ELECTRE TRI.

#### Initialisation

```python
from app.eval import NutriScoreElectreEvaluator

evaluator = NutriScoreElectreEvaluator()
```

#### Méthode `compute_confusion_matrix()`

Calcule la matrice de confusion.

**Signature** :
```python
def compute_confusion_matrix(
    df: pd.DataFrame,
    nutriscore_col: str = 'ns_label_calc',
    electre_col: str = 'electre_cat'
) -> Tuple[np.ndarray, Dict[str, any]]
```

**Retourne** :
- `np.ndarray` : Matrice de confusion
- `Dict` : Métadonnées (labels, distributions, etc.)

**Exemple** :
```python
evaluator = NutriScoreElectreEvaluator()

cm, metadata = evaluator.compute_confusion_matrix(df)

print("Matrice de confusion:")
print(cm)
print(f"Total échantillons: {metadata['total_samples']}")
```

#### Méthode `compute_metrics()`

Calcule les métriques de performance.

**Signature** :
```python
def compute_metrics(
    df: pd.DataFrame,
    nutriscore_col: str = 'ns_label_calc',
    electre_col: str = 'electre_cat'
) -> Dict[str, float]
```

**Retourne** :
```python
{
    'accuracy': 0.785,
    'f1_score_macro': 0.742,
    'mae': 0.35,
    'kappa': 0.689
}
```

#### Méthode `generate_comparison_report()`

Génère un rapport visuel complet.

**Signature** :
```python
def generate_comparison_report(
    df: pd.DataFrame,
    output_path: str,
    nutriscore_col: str = 'ns_label_calc',
    electre_col: str = 'electre_cat'
) -> str
```

**Retourne** :
- `str` : Chemin du rapport généré (PNG ou PDF)

**Exemple** :
```python
report_path = evaluator.generate_comparison_report(
    df,
    output_path="outputs/reports/comparison_report.pdf"
)

print(f"Rapport généré: {report_path}")
```

---

## Module `io.py`

### Classe `ExcelDataLoader`

Chargement et mapping des données Excel.

#### Initialisation

```python
from app.io import ExcelDataLoader

loader = ExcelDataLoader(
    config_path="config/columns.yml"  # Config mapping (optionnel)
)
```

#### Méthode `load_excel_data()`

Charge un fichier Excel avec mapping automatique.

**Signature** :
```python
def load_excel_data(
    excel_path: str,
    sheet_name: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, str]]
```

**Retourne** :
- `pd.DataFrame` : Données avec colonnes mappées
- `Dict` : Mapping appliqué

**Exemple** :
```python
loader = ExcelDataLoader()

df, mapping_info = loader.load_excel_data(
    excel_path="data/produits.xlsx",
    sheet_name="Céréales"
)

print("Colonnes mappées:")
for target, source in mapping_info.items():
    print(f"  {source} → {target}")
```

---

## Module `api_openfoodfacts.py`

### Classe `OpenFoodFactsAPI`

Interface pour l'API Open Food Facts.

#### Méthode `search_product()`

Recherche un produit par code-barres ou nom.

**Signature** :
```python
def search_product(
    query: str,
    search_type: str = "barcode"
) -> Optional[Dict]
```

**Paramètres** :
- `query` : Code-barres ou nom de produit
- `search_type` : `"barcode"` ou `"name"`

**Retourne** :
- `Dict` : Données produit (ou `None` si non trouvé)

**Exemple** :
```python
from app.api_openfoodfacts import OpenFoodFactsAPI

api = OpenFoodFactsAPI()

# Recherche par code-barres
product = api.search_product("3017620422003", search_type="barcode")

if product:
    print(f"Produit: {product['product_name']}")
    print(f"Nutri-Score: {product['nutriscore_grade']}")
```

---

## Exemples d'Utilisation Complète

### Exemple 1 : Pipeline Complet

```python
from app.io import ExcelDataLoader
from app.normalize import DataNormalizer
from app.nutriscore import NutriScoreCalculator
from app.electre_tri import electre_sorting
from app.eval import NutriScoreElectreEvaluator

# 1. Charger les données
loader = ExcelDataLoader()
df, mapping = loader.load_excel_data("data/produits.xlsx")

# 2. Normaliser
df_normalized, report = DataNormalizer.normalize_dataframe(df)

# 3. Calculer Nutri-Score
calculator = NutriScoreCalculator()
df_with_nutri = calculator.apply_to_dataframe(df_normalized)

# 4. Calculer ELECTRE TRI
df_with_nutri['electre_cat'] = electre_sorting(
    df_with_nutri,
    variant="pessimistic"
)

# 5. Comparer
evaluator = NutriScoreElectreEvaluator()
metrics = evaluator.compute_metrics(df_with_nutri)

print(f"Exactitude: {metrics['accuracy']:.2%}")
```

### Exemple 2 : Calcul Unitaire Personnalisé

```python
from app.nutriscore import NutriScoreCalculator
from app.electre_tri import classify_single_product

# Données d'un produit
product_data = {
    'energy': 1500,
    'saturated_fat': 2.5,
    'sugars': 15,
    'salt': 0.8,
    'protein': 7,
    'fiber': 5,
    'fruits_veg': 0
}

# Nutri-Score
calculator = NutriScoreCalculator()
ns_score, ns_label, ns_details = calculator.compute_score_and_label(
    energy_kj=product_data['energy'],
    saturated_fat_g=product_data['saturated_fat'],
    sugars_g=product_data['sugars'],
    sodium_or_salt_value=product_data['salt'],
    fiber_g=product_data['fiber'],
    protein_g=product_data['protein'],
    fruits_veg_percent=product_data['fruits_veg']
)

# ELECTRE TRI
electre_result = classify_single_product(
    criteria_values=product_data,
    variant="pessimistic",
    lambda_threshold=0.75
)

# Affichage
print(f"Nutri-Score: {ns_label} (score: {ns_score})")
print(f"ELECTRE TRI: {electre_result['class']}")
print(f"Concordance: {electre_result['concordances']}")
```

### Exemple 3 : Configuration Personnalisée ELECTRE

```python
from app.electre_tri import electre_sorting

# Poids personnalisés (importance relative)
custom_weights = {
    'energy': 0.10,          # Moins d'importance
    'saturated_fat': 0.15,
    'sugars': 0.30,          # Plus d'importance
    'salt': 0.15,
    'protein': 0.10,
    'fiber': 0.10,
    'fruits_veg': 0.10
}

# Application avec seuil lambda strict
classifications = electre_sorting(
    df,
    variant="pessimistic",
    lambda_threshold=0.80,      # Plus strict (défaut: 0.75)
    custom_weights=custom_weights
)

# Distribution des catégories
print(classifications.value_counts())
```

---

## Types de Données

### Critères ELECTRE TRI

```python
{
    'energy': float,              # kJ/100g
    'saturated_fat': float,       # g/100g
    'sugars': float,              # g/100g
    'salt': float,                # g/100g
    'protein': float,             # g/100g
    'fiber': float,               # g/100g
    'fruits_veg': float          # %
}
```

### Résultat Nutri-Score Détaillé

```python
{
    "score": int,                # Score numérique
    "label": str,                # A, B, C, D, E
    "details": {
        "negative_points": int,
        "positive_points": int,
        "final_score": int,
        "negative_detail": {
            "energy_points": int,
            "saturated_fat_points": int,
            "sugars_points": int,
            "salt_points": int
        },
        "positive_detail": {
            "fiber_points": int,
            "protein_points": int,
            "fruits_veg_points": int,
            "protein_rule_applied": bool
        }
    }
}
```

---

## Codes d'Erreur

| Code | Signification |
|------|---------------|
| `N/A` | Données insuffisantes pour le calcul |
| `ERROR` | Erreur durant le calcul |
| `None` | Valeur manquante |

---

## Bonnes Pratiques

### Gestion des Erreurs

```python
try:
    score, label, details = calculator.compute_score_and_label(...)
except ValueError as e:
    print(f"Erreur de validation: {e}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

### Validation des Données

```python
import pandas as pd

def validate_nutritional_data(df):
    """Valide que les données sont dans les plages acceptables."""
    checks = {
        'energy': (0, 4000),
        'saturated_fat': (0, 100),
        'sugars': (0, 100),
        'salt': (0, 10),
        'protein': (0, 100),
        'fiber': (0, 50),
        'fruits_veg': (0, 100)
    }
    
    for col, (min_val, max_val) in checks.items():
        if col in df.columns:
            invalid = df[(df[col] < min_val) | (df[col] > max_val)]
            if len(invalid) > 0:
                print(f"Attention: {len(invalid)} valeurs aberrantes pour {col}")
```

### Performance

```python
# Pour de grands datasets, utiliser le traitement par lots
chunk_size = 1000

for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i+chunk_size]
    chunk_processed = calculator.apply_to_dataframe(chunk)
    # Sauvegarder ou traiter le chunk
```

---

**Date de mise à jour** : Décembre 2025  
**Version** : 1.0
