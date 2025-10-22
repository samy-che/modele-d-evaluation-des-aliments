# Prototype Nutri-Score / ELECTRE TRI

## Description

Outil de comparaison entre le calcul officiel du Nutri-Score et la méthode de classement ELECTRE TRI pour l'évaluation nutritionnelle des produits alimentaires.

## Fonctionnalités

- ✅ **Calcul Nutri-Score officiel** : Implémentation complète avec les 7 composantes nutritionnelles
- ✅ **ELECTRE TRI-B simplifié** : Classification multicritère avec concordance binaire (variantes pessimiste/optimiste)  
- ✅ **Interface graphique Streamlit** : Calcul unitaire et traitement de datasets
- ✅ **Comparaison et évaluation** : Matrice de confusion, métriques de performance
- ✅ **Normalisation automatique** : Conversion kJ/kcal, sel/sodium, nettoyage des données
- ✅ **Configuration flexible** : Mapping des colonnes et paramètres ELECTRE modifiables

## Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de packages Python)

### Installation des dépendances

```bash
# Cloner/télécharger le projet et naviguer dans le répertoire
cd /chemin/vers/le/projet

# Installer les dépendances
pip install -r requirements.txt
```

### Vérification de l'installation

```bash
# Test des imports principaux
python -c "import pandas, numpy, streamlit, yaml, sklearn; print('✅ Toutes les dépendances sont installées')"
```

## Utilisation

### 1. Lancement de l'interface Streamlit

```bash
# Depuis le répertoire racine du projet
streamlit run app/ui_streamlit.py
```

L'interface s'ouvrira automatiquement dans votre navigateur (généralement http://localhost:8501).

### 2. Utilisation en ligne de commande

#### Test des modules individuels

```bash
# Test du calcul Nutri-Score
python app/nutriscore.py

# Test ELECTRE TRI
python app/electre_tri.py

# Test du module d'évaluation
python app/eval.py
```

#### Chargement et traitement des données

```python
from app.io import load_data
from app.normalize import normalize_data
from app.nutriscore import apply_nutriscore
from app.electre_tri import electre_sorting

# Charger les données
df, mapping, quality = load_data("data/produits.xlsx")

# Normaliser
df_normalized, report = normalize_data(df)

# Calculer Nutri-Score
df_with_nutri = apply_nutriscore(df_normalized)

# Appliquer ELECTRE TRI
classifications = electre_sorting(df_with_nutri, variant="pessimistic")
```

## Structure du projet

```
├── app/                          # Code principal
│   ├── io.py                     # Chargement des données Excel
│   ├── normalize.py              # Normalisation des données
│   ├── nutriscore.py            # Calcul Nutri-Score officiel
│   ├── electre_tri.py           # Implémentation ELECTRE TRI
│   ├── eval.py                  # Comparaison et métriques
│   └── ui_streamlit.py          # Interface utilisateur
├── config/                       # Fichiers de configuration
│   ├── columns.yml              # Mapping des colonnes
│   └── electre.yml              # Paramètres ELECTRE TRI
├── data/                        # Données d'entrée
│   └── produits.xlsx           # Dataset principal (fourni)
├── outputs/                     # Fichiers de sortie
│   ├── reports/                # Graphiques (PNG)
│   └── excel/                  # Exports Excel
├── requirements.txt            # Dépendances Python
└── README.md                  # Ce fichier
```

## Interface Streamlit

### Onglet 1 : Calcul unitaire
- Saisie des 7 composantes nutritionnelles
- Conversion automatique kcal→kJ et sel→sodium
- Calcul Nutri-Score individuel
- Classification ELECTRE TRI avec paramètres ajustables

### Onglet 2 : Traitement dataset
- Chargement du fichier Excel (par défaut `data/produits.xlsx`)
- Recalcul Nutri-Score sur l'ensemble du dataset
- Application ELECTRE TRI (pessimiste/optimiste)
- Comparaison complète avec matrice de confusion et métriques
- Export des résultats

## Configuration

### Mapping des colonnes (`config/columns.yml`)

Permet d'adapter l'outil à différents formats de datasets en définissant des alias pour chaque colonne nutritionnelle requise.

Exemple :
```yaml
energy_100g:
  - energy_100g
  - energie_kj_100g
  - energy-kj_100g
```

### Paramètres ELECTRE TRI (`config/electre.yml`)

- **Poids des critères** : Importance relative de chaque composant nutritionnel
- **Profils limites** : Seuils pour les 5 classes (A', B', C', D', E')
- **Lambda** : Seuil de concordance pour le surclassement (0.5-1.0)
- **Directions** : Coût (-1) ou bénéfice (+1) pour chaque critère

#### Version simplifiée d'ELECTRE TRI

Cette implémentation utilise une version simplifiée d'ELECTRE TRI conforme aux spécifications du projet :

- **Concordance binaire** : Indices de concordance partielle en 0 ou 1 (sans seuils de préférence/indifférence)
- **Pas de discordance ni de véto** : Évaluation basée uniquement sur la concordance globale
- **Logique de classification corrigée** :
  - **Pessimiste** : Parcours des profils b4→b3→b2, affectation selon premier profil surclassé
  - **Optimiste** : Parcours des profils b2→b3→b4, affectation selon premier profil surclassant

## Sorties générées

### Fichiers automatiques
- `outputs/reports/confusion_matrix.png` : Matrice de confusion visualisée
- `outputs/reports/metrics_summary.png` : Résumé graphique des métriques
- `outputs/excel/dataset_avec_preds.xlsx` : Dataset enrichi avec prédictions
- `outputs/excel/classement_electre.xlsx` : Classement ELECTRE TRI seul

### Métriques calculées
- **Accuracy** : Concordance exacte entre Nutri-Score et ELECTRE TRI
- **F1-Score** : Macro et weighted
- **MAE** : Erreur absolue moyenne sur les rangs (A=1, B=2, etc.)
- **Corrélation de Spearman** : Corrélation des rangs
- **Tolérance** : Accuracy avec ±1 et ±2 niveaux d'écart

## Limitations et hypothèses

### Version ELECTRE TRI implémentée

Cette implémentation utilise une **version simplifiée d'ELECTRE TRI** :

- **Concordance binaire** : Les indices de concordance partielle sont calculés en 0 ou 1 uniquement
  - Critère à maximiser : `1 si valeur_alternative >= valeur_profil, sinon 0`
  - Critère à minimiser : `1 si valeur_alternative <= valeur_profil, sinon 0`
- **Absence de seuils** : Pas de seuils de préférence (p), d'indifférence (q) ou de véto (v)
- **Pas de discordance** : Seule la concordance globale (somme pondérée) est utilisée pour le surclassement
- **Classification corrigée** : Logic d'affectation aux classes respectant la théorie ELECTRE TRI

### Données manquantes
- **Critères critiques manquants** : La ligne est supprimée du traitement
- **Colonne additives_count** : Si absente, le critère est ignoré dans ELECTRE TRI
- **Stratégies configurables** : drop_row, fill_zero, fill_median

### Conversions automatiques
- **Énergie** : Détection automatique kJ/kcal, conversion vers kJ (1 kcal = 4.184 kJ)
- **Sodium** : Si colonne sel présente, conversion automatique (sel_g × 400 = sodium_mg)
- **Pourcentages** : Valeurs clippées entre 0 et 100%

### Mapping ELECTRE ↔ Nutri-Score
Par défaut, correspondance directe : A'→A, B'→B, C'→C, D'→D, E'→E pour les métriques.

## Dépannage

### Problèmes fréquents

1. **"Module not found"** : Vérifiez l'installation des dépendances avec `pip install -r requirements.txt`

2. **"Colonnes manquantes"** : Adaptez le fichier `config/columns.yml` aux noms de vos colonnes

3. **Interface Streamlit ne se lance pas** : 
   ```bash
   # Vérifiez que Streamlit est installé
   streamlit --version
   
   # Lancez depuis le bon répertoire
   cd /chemin/vers/projet
   streamlit run app/ui_streamlit.py
   ```

4. **Erreur de chargement Excel** : Vérifiez que le fichier `data/produits.xlsx` existe et contient les colonnes attendues

5. **Pas de graphiques générés** : Vérifiez que les répertoires `outputs/reports/` et `outputs/excel/` existent

### Support technique

En cas de problème :
1. Vérifiez les logs dans la console/terminal
2. Consultez les messages d'erreur de Streamlit
3. Validez le format de vos données d'entrée
4. Testez les modules individuellement avec les scripts de test intégrés

## Critères d'acceptation (démo)

✅ **Calcul unitaire** : L'interface calcule correctement le Nutri-Score à partir des 7 composantes  
✅ **Classification ELECTRE** : Application de la méthode ELECTRE TRI simplifiée sur produits individuels et datasets  
✅ **Comparaison automatique** : Génération de matrice de confusion et métriques en un clic  
✅ **Fichiers de sortie** : PNG des graphiques et Excel des résultats dans `outputs/`  
✅ **Robustesse** : Gestion des conversions d'unités et valeurs manquantes avec messages informatifs  
✅ **Conformité théorique** : Implémentation conforme à la version simplifiée d'ELECTRE TRI spécifiée  

---

*Prototype développé selon les spécifications du 19 octobre 2025*  
*Version ELECTRE TRI simplifiée mise à jour le 22 octobre 2025*