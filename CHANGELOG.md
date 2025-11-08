# Changelog - Corrections des Métriques et Matrice de Confusion

## Version 1.1 - 31 octobre 2025

### 🐛 Corrections de bugs

#### Module `app/eval.py`

1. **Création automatique des répertoires**
   - Ajout de la création explicite des dossiers `outputs/reports/` et `outputs/excel/`
   - Correction de l'erreur `FileNotFoundError` lors de la sauvegarde des graphiques
   - Utilisation de `Path.mkdir(parents=True, exist_ok=True)` pour tous les sous-répertoires

2. **Mapping des labels ELECTRE vers Nutri-Score**
   - Ajout d'un dictionnaire de mapping `electre_to_nutri` dans `__init__`
   - Conversion automatique des labels `A', B', C', D', E'` vers `A, B, C, D, E`
   - Correction de l'alignement de la matrice de confusion

3. **Amélioration de l'affichage de la matrice de confusion**
   - Utilisation cohérente des labels entre les deux axes
   - Ajout d'apostrophes uniquement pour l'affichage visuel
   - Conservation de la clarté entre Nutri-Score (référence) et ELECTRE (prédiction)

#### Module `app/ui_streamlit.py`

1. **Affichage des visualisations**
   - Ajout de l'affichage direct des images dans l'interface
   - Nouvelle section "📊 Visualisations" avant "📁 Fichiers générés"
   - Utilisation de `st.image()` avec `use_container_width=True`
   - Affichage de la matrice de confusion et du résumé des métriques

### ✨ Améliorations

1. **Métriques calculées**
   - Accuracy (correspondance exacte)
   - F1-Score (macro et weighted)
   - MAE (Mean Absolute Error sur les rangs)
   - Accuracy avec tolérance ±1 et ±2 niveaux
   - Corrélation de Spearman avec p-value

2. **Visualisations**
   - Matrice de confusion : heatmap avec annotations
   - Résumé des métriques : 4 graphiques en sous-plots
   - Export Excel du dataset complet avec prédictions

3. **Tests**
   - Nouveau script `test_metriques.py` pour test complet avec rapport détaillé
   - Tous les tests de validation passent avec succès
   - Interprétation automatique des résultats

### 📊 Résultats de Performance

Sur le dataset de test (62 produits) :
- **Accuracy exacte** : 62.9%
- **Accuracy ±1 niveau** : 90.3%
- **Accuracy ±2 niveaux** : 100%
- **Corrélation Spearman** : 0.839 (forte)

### 📁 Nouveaux Fichiers

- `test_metriques.py` : Test complet avec rapport d'interprétation
- `CORRECTIONS_METRIQUES.md` : Documentation technique détaillée
- `RESUME_CORRECTIONS.md` : Résumé des corrections avec exemples
- `CHANGELOG.md` : Ce fichier

### 🔧 Fichiers Modifiés

- `app/eval.py` : Corrections principales du système de métriques
- `app/ui_streamlit.py` : Amélioration de l'affichage des résultats

### ✅ Tests de Régression

Tous les tests existants continuent de passer :
```bash
python3 test_validation.py      # ✅ Tous les critères validés
python3 test_metriques.py        # ✅ Rapport détaillé généré
python3 app/eval.py              # ✅ Module autonome fonctionnel
```

### 📝 Notes de Migration

Aucune action requise pour les utilisateurs existants. Les corrections sont rétrocompatibles et n'affectent pas l'API publique des modules.

### 🎯 Prochaines Étapes

- [ ] Ajouter des tests unitaires pour les fonctions de mapping
- [ ] Implémenter des graphiques interactifs (Plotly)
- [ ] Ajouter l'export PDF des rapports
- [ ] Améliorer la gestion des cas limites (datasets très petits)

---

**Auteur** : Corrections appliquées le 31 octobre 2025  
**Statut** : Production Ready ✅
