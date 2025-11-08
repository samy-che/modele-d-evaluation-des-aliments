# Corrections des Métriques et Matrice de Confusion

## 🎯 Problèmes Identifiés et Corrigés

### 1. **Création des répertoires de sortie**

**Problème** : Les répertoires `reports/` et `excel/` n'étaient pas créés avant la sauvegarde des fichiers, causant des erreurs `FileNotFoundError`.

**Correction** : Ajout de la création explicite des sous-répertoires dans `app/eval.py` :

```python
# Créer les sous-répertoires
reports_path = output_path / "reports"
reports_path.mkdir(parents=True, exist_ok=True)

excel_path_dir = output_path / "excel"
excel_path_dir.mkdir(parents=True, exist_ok=True)
```

### 2. **Mapping des labels ELECTRE vers Nutri-Score**

**Problème** : La matrice de confusion tentait de comparer directement les labels `A, B, C, D, E` (Nutri-Score) avec `A', B', C', D', E'` (ELECTRE), causant des problèmes de dimension et d'alignement.

**Correction** : Ajout d'un mapping pour convertir les labels ELECTRE au format Nutri-Score :

```python
# Dans __init__
self.electre_to_nutri = {
    'A\'': 'A', 'B\'': 'B', 'C\'': 'C', 'D\'': 'D', 'E\'': 'E'
}

# Dans compute_confusion_matrix
electre_mapped = electre_values.map(self.electre_to_nutri)
cm = confusion_matrix(nutriscore_values, electre_mapped, labels=nutri_unique)
```

### 3. **Affichage des labels dans la matrice de confusion**

**Problème** : Les labels affichés sur les axes n'étaient pas cohérents avec les données de la matrice.

**Correction** : Amélioration de la fonction `plot_confusion_matrix` pour afficher correctement les labels :

```python
# Utiliser les mêmes labels de base
electre_labels = metadata.get('electre_labels', nutri_labels)

# Ajouter l'apostrophe pour l'affichage ELECTRE
display_electre_labels = [f"{label}'" if not label.endswith("'") else label 
                          for label in electre_labels]
```

### 4. **Affichage des visualisations dans Streamlit**

**Problème** : L'interface Streamlit affichait seulement les chemins des fichiers générés sans afficher les images.

**Correction** : Ajout de l'affichage direct des images dans `app/ui_streamlit.py` :

```python
# Afficher la matrice de confusion
confusion_path = files.get('confusion_matrix', '')
if confusion_path and os.path.exists(confusion_path):
    st.write("**Matrice de Confusion**")
    st.image(confusion_path, use_container_width=True)

# Afficher le résumé des métriques
metrics_path = files.get('metrics_summary', '')
if metrics_path and os.path.exists(metrics_path):
    st.write("**Résumé des Métriques**")
    st.image(metrics_path, use_container_width=True)
```

## ✅ Résultats

### Métriques Calculées

Le système calcule maintenant correctement les métriques suivantes :

1. **Accuracy** : Correspondance exacte entre Nutri-Score et ELECTRE
2. **F1-Score Macro** : Moyenne non pondérée du F1-Score pour chaque classe
3. **F1-Score Weighted** : Moyenne pondérée du F1-Score selon la fréquence des classes
4. **MAE (Mean Absolute Error)** : Erreur moyenne en termes de rangs
5. **Accuracy avec tolérance ±1** : Correspondance à 1 niveau près
6. **Accuracy avec tolérance ±2** : Correspondance à 2 niveaux près
7. **Corrélation de Spearman** : Corrélation entre les rangs
8. **P-value de Spearman** : Significativité statistique

### Visualisations Générées

1. **Matrice de Confusion** (`outputs/reports/confusion_matrix.png`)
   - Heatmap avec annotations
   - Labels correctement alignés (Nutri-Score en lignes, ELECTRE en colonnes)
   - Nombre total de produits affiché

2. **Résumé des Métriques** (`outputs/reports/metrics_summary.png`)
   - 4 graphiques en sous-plots :
     - Métriques principales (Accuracy, F1-Scores)
     - Accuracy avec tolérance
     - MAE (erreur absolue moyenne)
     - Corrélation de Spearman

3. **Dataset avec prédictions** (`outputs/excel/dataset_avec_preds.xlsx`)
   - Export Excel complet avec toutes les colonnes

## 🧪 Tests de Validation

Tous les tests passent avec succès :

```
✅ Test 1 : Calcul unitaire Nutri-Score
✅ Test 2 : Classification ELECTRE TRI
✅ Test 3 : Traitement dataset complet
✅ Test 4 : Comparaison et sorties
✅ Test 5 : Conversions d'unités
✅ Test 6 : Robustesse
```

### Exemple de résultats sur le dataset de test :

- **Produits analysés** : 62
- **Comparaisons valides** : 62
- **Accuracy** : 0.629
- **F1-Score macro** : 0.567
- **MAE** : 0.468
- **Corrélation de Spearman** : 0.711

## 📊 Utilisation

### En ligne de commande

```python
from app.eval import compare_nutriscore_electre
import pandas as pd

# Charger vos données avec les colonnes 'ns_label_calc' et 'electre_cat'
df = pd.read_excel('data/produits.xlsx')

# Générer le rapport complet
report = compare_nutriscore_electre(
    df, 
    nutriscore_col='ns_label_calc',
    electre_col='electre_cat',
    output_dir='outputs'
)

# Accéder aux métriques
print(report['metrics'])
```

### Via l'interface Streamlit

1. Charger un fichier de données
2. Calculer le Nutri-Score (bouton "Calculer Nutri-Score")
3. Calculer ELECTRE TRI (bouton "Classifier ELECTRE TRI")
4. Comparer les méthodes (bouton "📊 Comparer méthodes")
5. Les visualisations s'affichent automatiquement

## 🔧 Fichiers Modifiés

1. **`app/eval.py`** : Corrections du mapping, création des répertoires, alignement des labels
2. **`app/ui_streamlit.py`** : Ajout de l'affichage des images dans l'interface

## 📝 Notes Techniques

- La matrice de confusion compare toujours Nutri-Score (référence) vs ELECTRE (prédiction)
- Les labels ELECTRE (`A', B', C', D', E'`) sont convertis en format Nutri-Score (`A, B, C, D, E`) pour la comparaison
- L'affichage visuel conserve les apostrophes pour différencier clairement les deux méthodes
- Toutes les métriques gèrent correctement les valeurs manquantes ou invalides
