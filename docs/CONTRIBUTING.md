# Guide de Contribution

Merci de votre intérêt pour contribuer au projet **Modèle d'Évaluation des Aliments** !

## 📋 Table des Matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
3. [Standards de Code](#standards-de-code)
4. [Structure des Commits](#structure-des-commits)
5. [Tests](#tests)
6. [Documentation](#documentation)

---

## 🤝 Code de Conduite

Ce projet adhère aux principes suivants :
- Respect et courtoisie envers tous les contributeurs
- Communication constructive et bienveillante
- Ouverture aux critiques constructives
- Collaboration et partage des connaissances

---

## 💡 Comment Contribuer

### Types de Contributions

#### 🐛 Signaler un Bug

1. Vérifier que le bug n'a pas déjà été signalé
2. Créer un rapport détaillé incluant :
   - Description du problème
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Version Python et système d'exploitation
   - Messages d'erreur complets

**Exemple** :
```
Titre : Erreur de calcul Nutri-Score pour les boissons

Description :
Le calcul Nutri-Score pour les boissons retourne un label incorrect.

Étapes :
1. Charger un produit de type "beverage"
2. Calculer le Nutri-Score
3. Observer le label retourné

Attendu : Label "B" (score 4)
Observé : Label "C" (score 4)

Environnement :
- Python 3.11
- macOS 14
- Version projet : 1.0
```

#### ✨ Proposer une Fonctionnalité

1. Vérifier que la fonctionnalité n'existe pas déjà
2. Créer une proposition détaillée :
   - Cas d'usage
   - Bénéfices attendus
   - Approche technique envisagée
   - Impact sur l'existant

#### 🔧 Soumettre une Correction

1. **Fork** le projet
2. Créer une **branche** pour votre modification
3. Faire vos **modifications**
4. Ajouter des **tests** si nécessaire
5. Soumettre une **Pull Request**

---

## 📝 Standards de Code

### Style Python (PEP 8)

```python
# ✅ BON
def calculate_nutriscore(
    energy_kj: float,
    saturated_fat_g: float,
    sugars_g: float
) -> Tuple[int, str]:
    """
    Calcule le Nutri-Score d'un produit.
    
    Args:
        energy_kj: Énergie en kJ/100g
        saturated_fat_g: Graisses saturées en g/100g
        sugars_g: Sucres en g/100g
        
    Returns:
        Tuple (score, label)
    """
    # Logique de calcul
    pass

# ❌ MAUVAIS
def calc(e,s,su):
    # Pas de docstring, noms peu clairs
    pass
```

### Conventions de Nommage

```python
# Variables et fonctions : snake_case
energy_value = 1650
def compute_score():
    pass

# Classes : PascalCase
class NutriScoreCalculator:
    pass

# Constantes : UPPER_CASE
MAX_ENERGY_KJ = 4000
DEFAULT_LAMBDA = 0.75

# Privées : _prefix
def _internal_helper():
    pass
```

### Type Hints

```python
from typing import Dict, List, Optional, Tuple

# Toujours spécifier les types
def process_data(
    df: pd.DataFrame,
    config: Optional[Dict[str, any]] = None
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Documentation..."""
    pass
```

### Docstrings (Format Google)

```python
def compute_concordance(
    alternative: Dict[str, float],
    profile: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """
    Calcule l'indice de concordance globale.
    
    Cette fonction implémente la formule ELECTRE TRI pour évaluer
    dans quelle mesure une alternative surclasse un profil limite.
    
    Args:
        alternative: Valeurs des critères de l'alternative
        profile: Valeurs des critères du profil limite
        weights: Poids des critères (normalisés à 1)
        
    Returns:
        Indice de concordance entre 0 et 1
        
    Raises:
        ValueError: Si les poids ne somment pas à 1
        
    Example:
        >>> alt = {'energy': 1500, 'sugars': 10}
        >>> prof = {'energy': 1800, 'sugars': 12}
        >>> weights = {'energy': 0.5, 'sugars': 0.5}
        >>> compute_concordance(alt, prof, weights)
        0.75
    """
    # Implémentation
    pass
```

---

## 🔀 Structure des Commits

### Format des Messages

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

### Types de Commits

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Formatage, espaces (pas de changement de code)
- `refactor`: Refactorisation (pas de nouvelle fonctionnalité ni de bug)
- `test`: Ajout ou modification de tests
- `chore`: Maintenance (dépendances, config)

### Exemples

```bash
# Nouvelle fonctionnalité
feat(electre): ajouter variante ELECTRE TRI-C

Implémentation de la variante ELECTRE TRI-C avec procédure
de tri intermédiaire entre pessimiste et optimiste.

Closes #42

# Correction de bug
fix(nutriscore): corriger conversion sodium/sel

Le facteur de conversion était incorrect (400 au lieu de 2.5).
Mise à jour selon les standards officiels.

Fixes #38

# Documentation
docs(api): ajouter exemples pour classify_single_product

Ajout de 3 exemples d'utilisation avec différentes configurations.

# Refactorisation
refactor(normalize): simplifier parse_energy_string

Suppression de code dupliqué et amélioration de la lisibilité.
Aucun changement fonctionnel.
```

---

## 🧪 Tests

### Ajouter des Tests

Chaque nouvelle fonctionnalité doit inclure des tests.

```python
# tests/test_nutriscore.py
import pytest
from app.nutriscore import NutriScoreCalculator

class TestNutriScoreCalculator:
    """Tests pour le calculateur Nutri-Score."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.calculator = NutriScoreCalculator()
    
    def test_compute_score_basic(self):
        """Test calcul de base."""
        score, label, details = self.calculator.compute_score_and_label(
            energy_kj=1650,
            saturated_fat_g=3.2,
            sugars_g=25,
            sodium_or_salt_value=0.9,
            fiber_g=5.5,
            protein_g=8,
            fruits_veg_percent=0
        )
        
        assert score == 11
        assert label == "C"
    
    def test_protein_rule_applied(self):
        """Test application règle protéines."""
        # Produit avec ≥11 points défavorables
        score, label, details = self.calculator.compute_score_and_label(
            energy_kj=2500,
            saturated_fat_g=8,
            sugars_g=30,
            sodium_or_salt_value=2.0,
            fiber_g=1,
            protein_g=15,
            fruits_veg_percent=0
        )
        
        # Les protéines ne doivent pas être comptées
        assert details['positive_detail']['protein_rule_applied'] is True
        assert details['positive_detail']['protein_points'] == 0
    
    def test_missing_values(self):
        """Test gestion valeurs manquantes."""
        import numpy as np
        
        score, label, details = self.calculator.compute_score_and_label(
            energy_kj=1500,
            saturated_fat_g=np.nan,  # Valeur manquante
            sugars_g=10,
            sodium_or_salt_value=0.5,
            fiber_g=5,
            protein_g=8,
            fruits_veg_percent=0
        )
        
        # Le calcul doit réussir malgré la valeur manquante
        assert isinstance(score, int)
        assert label in ['A', 'B', 'C', 'D', 'E']
```

### Exécuter les Tests

```bash
# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_nutriscore.py

# Avec couverture
pytest --cov=app tests/

# Mode verbose
pytest -v tests/
```

### Couverture de Code

Viser au minimum 80% de couverture pour les nouvelles fonctionnalités.

```bash
# Générer rapport de couverture
pytest --cov=app --cov-report=html tests/

# Ouvrir le rapport
open htmlcov/index.html
```

---

## 📖 Documentation

### Documenter le Code

#### Modules

```python
"""
Module de calcul ELECTRE TRI.

Ce module implémente la méthode ELECTRE TRI-B pour la classification
multicritère des produits alimentaires.

Classes:
    ElectreTri: Classe principale de calcul

Fonctions:
    electre_sorting: Application à un DataFrame
    classify_single_product: Classification unitaire

Exemple:
    >>> from app.electre_tri import ElectreTri
    >>> electre = ElectreTri()
    >>> category = electre.classify_alternative({...})
"""
```

#### Classes

```python
class ElectreTri:
    """
    Implémentation ELECTRE TRI-B avec profils limites.
    
    Cette classe permet de classer des alternatives dans des catégories
    prédéfinies en utilisant la méthode ELECTRE TRI-B.
    
    Attributes:
        config_path: Chemin vers le fichier de configuration
        params: Paramètres chargés (poids, profils, lambda)
        
    Example:
        >>> electre = ElectreTri("config/electre.yml")
        >>> category = electre.classify_alternative(
        ...     {'energy': 1500, 'sugars': 10},
        ...     variant="pessimistic"
        ... )
        >>> print(category)
        'B'
    """
```

### Mettre à Jour la Documentation

Lors de modifications importantes :

1. **README.md** : Si changement d'installation ou d'utilisation
2. **docs/ARCHITECTURE.md** : Si nouvelle structure ou module
3. **docs/API_REFERENCE.md** : Si nouvelle API ou modification de signature
4. **docs/METHODES_CALCUL.md** : Si changement d'algorithme
5. **docs/GUIDE_UTILISATION.md** : Si nouvelle fonctionnalité utilisateur

---

## 🔄 Workflow de Contribution

### 1. Préparation

```bash
# Fork le projet sur votre compte
# Cloner votre fork
git clone https://github.com/<votre-username>/modele-d-evaluation-des-aliments.git
cd modele-d-evaluation-des-aliments

# Ajouter le dépôt original comme remote
git remote add upstream https://github.com/<original-repo>/modele-d-evaluation-des-aliments.git

# Créer environnement virtuel
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si existe
```

### 2. Développement

```bash
# Créer une branche pour votre fonctionnalité
git checkout -b feat/ma-nouvelle-fonctionnalite

# Faire vos modifications
# ...

# Vérifier le style de code
flake8 app/
black app/ --check

# Exécuter les tests
pytest tests/

# Commiter vos changements
git add .
git commit -m "feat(module): description de la fonctionnalité"
```

### 3. Soumission

```bash
# Mettre à jour depuis upstream
git fetch upstream
git rebase upstream/main

# Pousser vers votre fork
git push origin feat/ma-nouvelle-fonctionnalite

# Créer une Pull Request sur GitHub
```

### 4. Revue

- Répondre aux commentaires
- Faire les modifications demandées
- Mettre à jour la PR

```bash
# Faire les modifications
# ...

# Commiter
git add .
git commit -m "fix: correction selon revue de code"

# Pousser
git push origin feat/ma-nouvelle-fonctionnalite
```

---

## ✅ Checklist Avant Soumission

- [ ] Code respecte PEP 8
- [ ] Type hints ajoutés
- [ ] Docstrings complètes
- [ ] Tests ajoutés et passent
- [ ] Documentation mise à jour
- [ ] Pas de code commenté inutile
- [ ] Pas de print() de debug
- [ ] Messages de commit clairs
- [ ] Branch à jour avec upstream/main

---

## 🎨 Outils Recommandés

### Formatage Automatique

```bash
# Black (formatage)
pip install black
black app/

# isort (tri des imports)
pip install isort
isort app/
```

### Analyse Statique

```bash
# Flake8 (linting)
pip install flake8
flake8 app/

# mypy (vérification types)
pip install mypy
mypy app/
```

### Pre-commit Hooks

```bash
# Installer pre-commit
pip install pre-commit

# Configurer
pre-commit install

# Exécuter manuellement
pre-commit run --all-files
```

Fichier `.pre-commit-config.yaml` :
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

---

## 📞 Contact

Pour toute question sur la contribution :

- Ouvrir une **issue** pour discussions publiques
- Consulter la **documentation** existante
- Vérifier les **issues** et **PR** existantes

---

## 🏆 Reconnaissance

Tous les contributeurs sont reconnus dans le fichier CONTRIBUTORS.md.

Merci de contribuer au projet ! 🙏

---

**Date de mise à jour** : Décembre 2025  
**Version** : 1.0
