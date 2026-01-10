# Guide d'Utilisation

## 🎯 Introduction

Ce guide vous explique comment utiliser l'outil d'évaluation nutritionnelle pour :
- Calculer le Nutri-Score d'un produit
- Classer des produits avec ELECTRE TRI
- Comparer les deux méthodes
- Analyser des datasets complets

## 🚀 Démarrage Rapide

### Lancer l'Application

```bash
# Activer l'environnement virtuel
source .venv/bin/activate  # macOS/Linux
# OU
.venv\Scripts\activate      # Windows

# Lancer Streamlit
streamlit run app/ui_streamlit.py
```

L'application s'ouvre automatiquement dans votre navigateur à `http://localhost:8501`.

## 📱 Interface Utilisateur

L'interface comprend 3 onglets principaux :

### 🏠 Onglet "Accueil"

**Contenu** :
- Présentation du projet
- Documentation des méthodes
- Exemples d'utilisation
- Liens utiles

**Utilisation** :
- Lecture seule
- Point de départ pour comprendre le projet

---

### 🧮 Onglet "Calcul Unitaire"

**Objectif** : Évaluer un seul produit alimentaire.

#### Méthode 1 : Saisie Manuelle

1. **Entrer les informations du produit** :
   ```
   Nom du produit : Céréales au chocolat
   ```

2. **Renseigner les valeurs nutritionnelles** (pour 100g/100ml) :
   - **Énergie** : 1500 kJ
   - **Graisses saturées** : 2.5 g
   - **Sucres** : 15 g
   - **Sel** : 0.8 g
   - **Protéines** : 7 g
   - **Fibres** : 5 g
   - **Fruits/légumes** : 0 %

3. **Cliquer sur "Calculer"**

4. **Résultats affichés** :
   - 📊 **Nutri-Score** : Score + Label (A-E)
   - 🎯 **ELECTRE TRI** : Catégorie (A'-E')
   - 📈 **Graphiques** : Visualisation des scores
   - 📋 **Détails** : Décomposition des calculs

#### Méthode 2 : Recherche Open Food Facts

1. **Activer la recherche** :
   - Cocher "Rechercher dans Open Food Facts"

2. **Entrer un code-barres ou nom** :
   ```
   Code-barres : 3017620422003
   OU
   Nom : Nutella
   ```

3. **Sélectionner un produit** :
   - Liste de résultats affichée
   - Cliquer sur le produit souhaité

4. **Données importées automatiquement** :
   - Valeurs nutritionnelles pré-remplies
   - Nutri-Score officiel (si disponible)

5. **Calculer et comparer** :
   - Calcul ELECTRE TRI
   - Comparaison avec Nutri-Score officiel

#### Exemple Complet : Céréales

```
Produit : Special K Original
─────────────────────────────
Énergie       : 1567 kJ
Graisses sat. : 0.3 g
Sucres        : 17 g
Sel           : 0.75 g
Protéines     : 14 g
Fibres        : 3.5 g
Fruits/légumes: 0 %

RÉSULTATS :
─────────────────────────────
Nutri-Score   : C (score: 4)
ELECTRE TRI   : C' (pessimiste)
Concordance   : 85%
```

---

### 📊 Onglet "Traitement Dataset"

**Objectif** : Analyser un fichier Excel/CSV avec plusieurs produits.

#### Étape 1 : Charger les Données

**Format de fichier attendu** :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| Produit | Nom du produit | "Corn Flakes" |
| valeur energetique (KJ) | Énergie en kJ | 1550 |
| quantite acides gras satures (g) | Graisses saturées | 0.5 |
| quantite de sucres (g) | Sucres | 8.5 |
| quantite de Sodium (mg/g) | Sodium ou sel | 350 |
| quantite de proteines (g) | Protéines | 7.5 |
| quantite de Fibres (g) | Fibres | 3.0 |
| teneur en Fruits/Legumes/Fruits a coques | Fruits/légumes (%) | 0 |

**Charger le fichier** :
1. Cliquer sur "Browse files" ou glisser-déposer
2. Formats acceptés : `.xlsx`, `.xls`, `.csv`
3. Attendre la validation automatique

**Validation automatique** :
- ✅ Colonnes requises présentes
- ✅ Types de données corrects
- ⚠️ Valeurs manquantes signalées
- ⚠️ Valeurs aberrantes détectées

#### Étape 2 : Configuration ELECTRE

**Paramètres disponibles** (barre latérale) :

1. **Variante de tri** :
   - 🔽 **Pessimiste** (recommandé) : Classification prudente
   - 🔼 **Optimiste** : Classification favorable

2. **Seuil Lambda** (0.5 - 1.0) :
   - Niveau de concordance requis
   - **Défaut** : 0.75
   - Plus élevé = plus strict

3. **Poids des critères** :
   - Ajuster l'importance relative
   - Total doit égaler 100%
   
   ```
   Énergie      : 15% [────────]
   Graisses sat.: 15% [────────]
   Sucres       : 20% [██████████]  ← Plus important
   Sel          : 15% [────────]
   Protéines    : 10% [─────]
   Fibres       : 10% [─────]
   Fruits/lég.  : 15% [────────]
   ```

#### Étape 3 : Lancer les Calculs

1. **Cliquer sur "Lancer l'analyse"**

2. **Barre de progression affichée** :
   ```
   ████████████████░░░░  80% (800/1000 produits)
   ```

3. **Temps estimé** :
   - 100 produits : ~1 seconde
   - 1000 produits : ~5-10 secondes

#### Étape 4 : Consulter les Résultats

**📋 Tableau de résultats** :

| Produit | Nutri-Score | ELECTRE | Concordance |
|---------|-------------|---------|-------------|
| Produit A | B (3) | B' | ✅ Accord |
| Produit B | C (8) | B' | ⚠️ Différence |
| Produit C | A (0) | A' | ✅ Accord |

**Filtres disponibles** :
- Par catégorie Nutri-Score
- Par catégorie ELECTRE
- Par niveau de concordance
- Par nom de produit

**📊 Visualisations** :

1. **Matrice de Confusion** :
   - Comparaison Nutri-Score vs ELECTRE
   - Heatmap colorée
   - Valeurs et pourcentages

2. **Distribution des Catégories** :
   - Histogrammes côte à côte
   - Nutri-Score vs ELECTRE
   - Comptage par catégorie

3. **Graphiques de Concordance** :
   - Taux d'accord global
   - Analyse par catégorie
   - Écarts moyens

**📈 Métriques de Performance** :

```
Exactitude (Accuracy)  : 78.5%
Score F1 (Macro)       : 0.742
Erreur Absolue Moyenne : 0.35 catégories
Coefficient Kappa      : 0.689
```

**Interprétation** :
- **Accuracy > 70%** : Bonne concordance
- **F1 > 0.7** : Équilibre précision/rappel satisfaisant
- **MAE < 0.5** : Écarts faibles entre méthodes

#### Étape 5 : Exporter les Résultats

**Format Excel** :
1. Cliquer sur "📥 Exporter Excel"
2. Fichier généré : `outputs/excel/resultats_YYYYMMDD_HHMMSS.xlsx`

**Contenu du fichier Excel** :
- Feuille 1 : Données complètes avec résultats
- Feuille 2 : Métriques de comparaison
- Feuille 3 : Matrice de confusion
- Formatage conditionnel par catégorie

**Format Rapport PDF** :
1. Cliquer sur "📄 Générer Rapport PDF"
2. Rapport complet avec :
   - Résumé exécutif
   - Graphiques haute résolution
   - Tableaux de métriques
   - Recommandations

---

## ⚙️ Configuration Avancée

### Modifier les Paramètres ELECTRE

Fichier : `config/electre.yml`

```yaml
# Poids des critères (doivent sommer à 1)
weights:
  energy: 0.15
  saturated_fat: 0.15
  sugars: 0.20          # Augmenter pour plus d'importance
  salt: 0.15
  protein: 0.10
  fiber: 0.10
  fruits_veg: 0.15

# Seuil de concordance
lambda: 0.75            # 0.5 (permissif) à 1.0 (strict)

# Profils limites (seuils entre catégories)
profiles:
  b1:  # Limite entre A' et B'
    energy: 1000        # kJ/100g
    saturated_fat: 1.5  # g/100g
    sugars: 8.0         # g/100g
    salt: 0.5           # g/100g
    protein: 12.0       # g/100g
    fiber: 6.0          # g/100g
    fruits_veg: 60      # %
  
  b2:  # Limite entre B' et C'
    energy: 1500
    saturated_fat: 3.0
    sugars: 12.0
    salt: 1.0
    protein: 8.0
    fiber: 4.0
    fruits_veg: 40
  
  # ... b3, b4 pour C'/D' et D'/E'
```

**Après modification** :
1. Sauvegarder le fichier
2. Relancer Streamlit
3. Les nouveaux paramètres sont actifs

### Personnaliser le Mapping des Colonnes

Fichier : `config/columns.yml`

```yaml
# Ajouter des synonymes pour vos colonnes
valeur energetique (KJ):
  - valeur energetique (KJ)
  - energy_kj
  - energie
  - energy (kJ)
  - mon_nom_energie        # ← Ajouter votre nom

quantite de sucres (g):
  - quantite de sucres (g)
  - sugars_g
  - sucres
  - sugar
  - mes_sucres             # ← Personnaliser
```

**Utilité** :
- Adapter à vos fichiers Excel existants
- Éviter de renommer les colonnes manuellement
- Supporter plusieurs formats de données

---

## 💡 Cas d'Usage

### Cas 1 : Évaluer une Nouvelle Recette

**Contexte** : Vous développez une nouvelle céréale.

**Étapes** :
1. Calculer les valeurs nutritionnelles (pour 100g)
2. Onglet "Calcul Unitaire"
3. Saisir les valeurs
4. Analyser les résultats
5. **Optimiser** : Ajuster la recette si score/catégorie non satisfaisant

**Objectif** :
- Nutri-Score A ou B
- ELECTRE TRI A' ou B'

### Cas 2 : Comparer des Produits Concurrents

**Contexte** : Analyse de marché.

**Étapes** :
1. Créer un fichier Excel avec les produits
2. Ajouter les valeurs nutritionnelles
3. Charger dans "Traitement Dataset"
4. Analyser la distribution
5. Identifier les meilleurs/moins bons

**Insights** :
- Position de votre produit
- Benchmarking concurrentiel
- Opportunités d'amélioration

### Cas 3 : Audit d'une Gamme de Produits

**Contexte** : Révision d'un portfolio.

**Étapes** :
1. Exporter les données de tous vos produits
2. Traiter le dataset complet
3. Filtrer par catégorie
4. Générer le rapport PDF
5. Présenter aux équipes

**Décisions** :
- Reformuler produits E/D
- Mettre en avant produits A/B
- Stratégie marketing

---

## 🔍 Interprétation des Résultats

### Nutri-Score (A à E)

| Label | Score | Interprétation | Couleur |
|-------|-------|----------------|---------|
| A | -15 à 1 | Très bonne qualité | 🟢 Vert foncé |
| B | 2 à 10 | Bonne qualité | 🟢 Vert clair |
| C | 11 à 18 | Qualité moyenne | 🟡 Jaune |
| D | 19 à 25 | Qualité faible | 🟠 Orange |
| E | 26+ | Très faible qualité | 🔴 Rouge |

**Facteurs clés** :
- ➕ Fibres, protéines, fruits/légumes
- ➖ Énergie, graisses saturées, sucres, sel

### ELECTRE TRI (A' à E')

| Catégorie | Signification | Recommandation |
|-----------|---------------|----------------|
| A' | Excellent profil | Mettre en avant |
| B' | Bon profil | Acceptable |
| C' | Profil moyen | Amélioration possible |
| D' | Profil faible | Reformulation conseillée |
| E' | Profil très faible | Révision nécessaire |

**Différence avec Nutri-Score** :
- Approche multicritère
- Compensation limitée entre critères
- Profils limites configurables

### Concordance Nutri-Score ↔ ELECTRE

**Taux de concordance** :
- **> 80%** : Excellente cohérence
- **70-80%** : Bonne cohérence
- **60-70%** : Cohérence acceptable
- **< 60%** : Divergence significative

**En cas de divergence** :
1. Vérifier les données d'entrée
2. Examiner les critères ELECTRE
3. Analyser les seuils de profils
4. Considérer la nature du produit

---

## 🐛 Résolution de Problèmes

### Erreur : "Colonnes manquantes"

**Cause** : Format de fichier non conforme.

**Solution** :
1. Vérifier les noms de colonnes
2. Ajouter synonymes dans `config/columns.yml`
3. Ou renommer dans Excel

### Erreur : "Valeurs aberrantes"

**Cause** : Données en dehors des plages normales.

**Solution** :
1. Vérifier les unités (kJ vs kcal, mg vs g)
2. Corriger dans le fichier source
3. Utiliser la normalisation automatique

### Résultats inattendus

**Cause** : Paramètres ELECTRE non adaptés.

**Solution** :
1. Ajuster les poids dans la sidebar
2. Modifier le seuil lambda
3. Tester variante optimiste/pessimiste

### Performance lente

**Cause** : Dataset très volumineux.

**Solution** :
1. Fermer les autres applications
2. Traiter par lots (< 5000 produits)
3. Désactiver les graphiques complexes

---

## 📚 Ressources Complémentaires

- [ARCHITECTURE.md](ARCHITECTURE.md) : Structure du projet
- [METHODES_CALCUL.md](METHODES_CALCUL.md) : Détails des algorithmes
- [API_REFERENCE.md](API_REFERENCE.md) : Utilisation programmatique

---

## 💬 Bonnes Pratiques

### Saisie des Données

✅ **À faire** :
- Utiliser les valeurs pour 100g/100ml
- Vérifier les unités (kJ, g, mg, %)
- Compléter tous les champs obligatoires

❌ **À éviter** :
- Mélanger différentes portions
- Laisser des champs vides sans raison
- Utiliser des virgules au lieu de points

### Analyse des Résultats

✅ **À faire** :
- Comparer plusieurs méthodes
- Analyser les tendances globales
- Utiliser les filtres pour segmenter

❌ **À éviter** :
- Se fier uniquement à un indicateur
- Ignorer les divergences
- Sur-interpréter les petites différences

### Configuration ELECTRE

✅ **À faire** :
- Partir des paramètres par défaut
- Ajuster progressivement
- Documenter les modifications

❌ **À éviter** :
- Modifier tous les paramètres d'un coup
- Utiliser des poids extrêmes (0 ou 100%)
- Ignorer les messages d'avertissement

---

**Date de mise à jour** : Décembre 2025  
**Version** : 1.0
