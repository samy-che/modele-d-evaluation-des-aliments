# Méthodes de Calcul - Documentation Technique

## 📚 Vue d'ensemble

Ce document détaille les algorithmes et formules utilisés pour :
1. **Nutri-Score** - Système officiel français
2. **ELECTRE TRI-B** - Méthode d'aide à la décision multicritère
3. **Normalisation des données**
4. **Métriques de comparaison**

---

## 1️⃣ Nutri-Score - Calcul Officiel

### Principe Général

Le Nutri-Score évalue la qualité nutritionnelle d'un produit sur une échelle de A (meilleur) à E (moins bon).

**Formule générale** :
```
Score Nutri-Score = Points Défavorables - Points Favorables
```

### 1.1 Points Défavorables (Négatifs)

Les éléments à limiter dans l'alimentation :

#### Énergie (kJ/100g)

| Seuil (kJ) | Points |
|------------|--------|
| ≤ 335 | 0 |
| ≤ 670 | 1 |
| ≤ 1005 | 2 |
| ≤ 1340 | 3 |
| ≤ 1675 | 4 |
| ≤ 2010 | 5 |
| ≤ 2345 | 6 |
| ≤ 2680 | 7 |
| ≤ 3015 | 8 |
| ≤ 3350 | 9 |
| > 3350 | 10 |

**Note** : Si les données sont en kcal, conversion : `kJ = kcal × 4.184`

#### Acides Gras Saturés (g/100g)

| Seuil (g) | Points |
|-----------|--------|
| ≤ 1.0 | 0 |
| ≤ 2.0 | 1 |
| ≤ 3.0 | 2 |
| ≤ 4.0 | 3 |
| ≤ 5.0 | 4 |
| ≤ 6.0 | 5 |
| ≤ 7.0 | 6 |
| ≤ 8.0 | 7 |
| ≤ 9.0 | 8 |
| ≤ 10.0 | 9 |
| > 10.0 | 10 |

#### Sucres (g/100g)

| Seuil (g) | Points |
|-----------|--------|
| ≤ 3.4 | 0 |
| ≤ 6.8 | 1 |
| ≤ 10.0 | 2 |
| ≤ 14.0 | 3 |
| ≤ 17.0 | 4 |
| ≤ 20.0 | 5 |
| ≤ 24.0 | 6 |
| ≤ 27.0 | 7 |
| ≤ 31.0 | 8 |
| ≤ 34.0 | 9 |
| ≤ 37.0 | 10 |
| ≤ 41.0 | 11 |
| ≤ 44.0 | 12 |
| ≤ 48.0 | 13 |
| ≤ 51.0 | 14 |
| > 51.0 | 15 |

#### Sel (g/100g)

| Seuil (g) | Points |
|-----------|--------|
| ≤ 0.2 | 0 |
| ≤ 0.4 | 1 |
| ≤ 0.6 | 2 |
| ≤ 0.8 | 3 |
| ≤ 1.0 | 4 |
| ≤ 1.2 | 5 |
| ≤ 1.4 | 6 |
| ≤ 1.6 | 7 |
| ≤ 1.8 | 8 |
| ≤ 2.0 | 9 |
| ≤ 2.2 | 10 |
| ... | ... |
| > 4.0 | 20 |

**Note** : Si les données sont en sodium (mg), conversion : `sel (g) = sodium (mg) / 400`

### 1.2 Points Favorables (Positifs)

Les éléments bénéfiques dans l'alimentation :

#### Protéines (g/100g)

| Seuil (g) | Points |
|-----------|--------|
| ≤ 2.4 | 0 |
| ≤ 4.8 | 1 |
| ≤ 7.2 | 2 |
| ≤ 9.6 | 3 |
| ≤ 12.0 | 4 |
| ≤ 14.0 | 5 |
| ≤ 17.0 | 6 |
| > 17.0 | 7 |

#### Fibres (g/100g)

| Seuil (g) | Points |
|-----------|--------|
| ≤ 3.0 | 0 |
| ≤ 4.1 | 1 |
| ≤ 5.2 | 2 |
| ≤ 6.3 | 3 |
| ≤ 7.4 | 4 |
| > 7.4 | 5 |

#### Fruits, Légumes, Légumineuses (%)

| Seuil (%) | Points |
|-----------|--------|
| < 40 | 0 |
| ≤ 60 | 1 |
| ≤ 80 | 2 |
| > 80 | 5 |

### 1.3 Calcul du Score Final

**Règle générale** :
```
Score = (Énergie + Graisses sat. + Sucres + Sel) 
        - (Protéines + Fibres + Fruits/légumes)
```

**Règle de dérogation** (produits avec ≥ 11 points défavorables) :
- Si fruits/légumes < 5 points : ne pas compter les protéines
- Sinon : règle générale

**Implémentation** :
```python
def compute_nutriscore(energy, sat_fat, sugars, salt, protein, fiber, fruits_veg):
    # Points défavorables
    neg_points = (
        get_points(energy, ENERGY_TABLE) +
        get_points(sat_fat, SAT_FAT_TABLE) +
        get_points(sugars, SUGARS_TABLE) +
        get_points(salt, SALT_TABLE)
    )
    
    # Points favorables
    pos_points = (
        get_points(protein, PROTEIN_TABLE) +
        get_points(fiber, FIBER_TABLE) +
        get_points(fruits_veg, FRUITS_TABLE)
    )
    
    # Règle de dérogation
    if neg_points >= 11 and fruits_veg < 5:
        # Ne pas compter les protéines
        pos_points -= get_points(protein, PROTEIN_TABLE)
    
    # Score final
    score = neg_points - pos_points
    return score
```

### 1.4 Conversion Score → Label

#### Pour les aliments solides

| Score | Label | Couleur |
|-------|-------|---------|
| -15 à 1 | A | 🟢 Vert foncé |
| 2 à 10 | B | 🟢 Vert clair |
| 11 à 18 | C | 🟡 Jaune |
| 19 à 25 | D | 🟠 Orange |
| ≥ 26 | E | 🔴 Rouge |

#### Pour les boissons

| Score | Label |
|-------|-------|
| -15 à 1 | A |
| 2 à 5 | B |
| 6 à 9 | C |
| 10 à 13 | D |
| ≥ 14 | E |

**Détection automatique** : Un produit est considéré comme boisson si :
- Énergie < 100 kJ/100g, ou
- Indication explicite dans les données

### 1.5 Exemple de Calcul Complet

**Produit** : Céréales au chocolat (pour 100g)

**Données** :
- Énergie : 1650 kJ
- Graisses saturées : 3.2 g
- Sucres : 25 g
- Sel : 0.9 g
- Protéines : 8 g
- Fibres : 5.5 g
- Fruits/légumes : 0%

**Calcul des points défavorables** :
```
Énergie (1650 kJ)       : 4 points (1340 < 1650 ≤ 1675)
Graisses sat. (3.2 g)   : 3 points (3.0 < 3.2 ≤ 4.0)
Sucres (25 g)           : 6 points (20 < 25 ≤ 24... → 24 < 25 ≤ 27)
Sel (0.9 g)             : 4 points (0.8 < 0.9 ≤ 1.0)
                          ─────────
Total défavorables      : 17 points
```

**Calcul des points favorables** :
```
Protéines (8 g)         : 3 points (7.2 < 8 ≤ 9.6)
Fibres (5.5 g)          : 3 points (5.2 < 5.5 ≤ 6.3)
Fruits/légumes (0%)     : 0 point  (< 40%)
                          ─────────
Total favorables        : 6 points
```

**Score final** :
```
Score = 17 - 6 = 11
Label = C (11 ∈ [11, 18])
```

---

## 2️⃣ ELECTRE TRI-B - Classification Multicritère

### Principe Général

ELECTRE TRI classe les produits dans des catégories prédéfinies (A' à E') en les comparant à des **profils limites**.

### 2.1 Concepts de Base

#### Profils Limites

Seuils séparant les catégories :

```
A' ──[b1]── B' ──[b2]── C' ──[b3]── D' ──[b4]── E'
   excellent  bon     moyen   faible  très faible
```

**Exemple de profil b2 (limite B'/C')** :
```
Énergie         : 1500 kJ
Graisses sat.   : 3.0 g
Sucres          : 12.0 g
Sel             : 1.0 g
Protéines       : 8.0 g
Fibres          : 4.0 g
Fruits/légumes  : 40%
```

#### Direction des Critères

- **min** : À minimiser (moins = mieux)
  - Énergie, graisses saturées, sucres, sel

- **max** : À maximiser (plus = mieux)
  - Protéines, fibres, fruits/légumes

### 2.2 Indice de Concordance Partielle

Pour chaque critère, on évalue si le produit surclasse le profil.

**Critère à minimiser** (ex: énergie) :
```
           ⎧ 1  si produit ≤ profil  (bon)
c(a, b) = ⎨
           ⎩ 0  si produit > profil  (mauvais)
```

**Critère à maximiser** (ex: protéines) :
```
           ⎧ 1  si produit ≥ profil  (bon)
c(a, b) = ⎨
           ⎩ 0  si produit < profil  (mauvais)
```

**Implémentation** :
```python
def concordance_partial(value_a, value_b, direction):
    if pd.isna(value_a) or pd.isna(value_b):
        return 0.5  # Indécision si valeur manquante
    
    if direction == "min":
        return 1 if value_a <= value_b else 0
    else:  # direction == "max"
        return 1 if value_a >= value_b else 0
```

### 2.3 Indice de Concordance Globale

Moyenne pondérée des concordances partielles.

**Formule** :
```
         Σ(wi × ci)
C(a,b) = ──────────
            Σ wi
```

Où :
- `wi` = poids du critère i
- `ci` = concordance partielle du critère i

**Exemple** :

| Critère | Poids | Concordance | Contribution |
|---------|-------|-------------|--------------|
| Énergie | 0.15 | 1 | 0.15 |
| Graisses sat. | 0.15 | 0 | 0 |
| Sucres | 0.20 | 1 | 0.20 |
| Sel | 0.15 | 1 | 0.15 |
| Protéines | 0.10 | 0 | 0 |
| Fibres | 0.10 | 1 | 0.10 |
| Fruits/lég. | 0.15 | 0 | 0 |

```
C(a,b) = (0.15 + 0 + 0.20 + 0.15 + 0 + 0.10 + 0) / 1.0
       = 0.60 = 60%
```

### 2.4 Relation de Surclassement

Un produit **surclasse** un profil si :
```
C(a, b) ≥ λ
```

Où `λ` est le **seuil de concordance** (typiquement 0.75).

**Notation** :
- `a S b` : "a surclasse b" (a est meilleur ou équivalent à b)
- `b S a` : "b surclasse a" (a est moins bon que b)

### 2.5 Procédures de Tri

#### Procédure Pessimiste (Prudente)

**Principe** : Comparer du bas vers le haut.

**Algorithme** :
```
Pour chaque profil b4, b3, b2, b1 (de E vers A) :
    Si produit S profil :
        Assigner à la catégorie supérieure au profil
        Arrêter
    Sinon :
        Continuer
Si aucun profil surclassé :
    Assigner à la catégorie la plus basse (E')
```

**Exemple** :

Produit : `p`  
Profils : `b1 (A'/B'), b2 (B'/C'), b3 (C'/D'), b4 (D'/E')`

```
Test b4 : p S b4 ? Non → continuer
Test b3 : p S b3 ? Non → continuer  
Test b2 : p S b2 ? Oui → Catégorie C'
```

**Implémentation** :
```python
def pessimistic_sorting(product, profiles, lambda_threshold):
    # Parcourir du pire au meilleur
    for i in range(len(profiles) - 1, -1, -1):
        concordance = compute_concordance(product, profiles[i])
        if concordance >= lambda_threshold:
            # Produit surclasse ce profil → catégorie supérieure
            return categories[i + 1]
    
    # Aucun profil surclassé → pire catégorie
    return categories[0]  # E'
```

#### Procédure Optimiste (Favorable)

**Principe** : Comparer du haut vers le bas.

**Algorithme** :
```
Pour chaque profil b1, b2, b3, b4 (de A vers E) :
    Si profil S produit :
        Assigner à la catégorie inférieure au profil
        Arrêter
    Sinon :
        Continuer
Si aucun profil surclasse le produit :
    Assigner à la catégorie la plus haute (A')
```

**Exemple** :

```
Test b1 : b1 S p ? Oui → Catégorie B'
```

### 2.6 Exemple de Calcul Complet

**Produit** : Céréales au chocolat

**Valeurs** :
- Énergie : 1650 kJ
- Graisses saturées : 3.2 g
- Sucres : 25 g
- Sel : 0.9 g
- Protéines : 8 g
- Fibres : 5.5 g
- Fruits/légumes : 0%

**Profil b2 (limite B'/C')** :
- Énergie : 1500 kJ (min)
- Graisses saturées : 3.0 g (min)
- Sucres : 12.0 g (min)
- Sel : 1.0 g (min)
- Protéines : 8.0 g (max)
- Fibres : 4.0 g (max)
- Fruits/légumes : 40% (max)

**Concordances partielles** :

| Critère | Produit | Profil | Direction | Surclasse? | Concordance |
|---------|---------|--------|-----------|------------|-------------|
| Énergie | 1650 | 1500 | min | Non | 0 |
| Graisses sat. | 3.2 | 3.0 | min | Non | 0 |
| Sucres | 25 | 12 | min | Non | 0 |
| Sel | 0.9 | 1.0 | min | Oui | 1 |
| Protéines | 8 | 8 | max | Oui | 1 |
| Fibres | 5.5 | 4.0 | max | Oui | 1 |
| Fruits/lég. | 0 | 40 | max | Non | 0 |

**Concordance globale** :
```
C(p, b2) = (0×0.15 + 0×0.15 + 0×0.20 + 1×0.15 + 1×0.10 + 1×0.10 + 0×0.15) / 1.0
         = (0.15 + 0.10 + 0.10) / 1.0
         = 0.35 = 35%
```

**Décision** :
```
C(p, b2) = 35% < λ (75%)
→ Produit ne surclasse PAS b2
→ Continue avec b3...
```

**Résultat final (procédure pessimiste)** :
```
Test b3 : C(p, b3) = 55% < 75% → Non
Test b4 : C(p, b4) = 80% ≥ 75% → Oui
→ Catégorie D'
```

---

## 3️⃣ Normalisation des Données

### 3.1 Conversions d'Unités

#### Énergie

**kJ → kcal** :
```
kcal = kJ / 4.184
```

**kcal → kJ** :
```
kJ = kcal × 4.184
```

**Détection automatique** :
- Valeur > 500 → probablement kJ
- Valeur < 500 → probablement kcal

#### Sodium/Sel

**Sodium (mg) → Sel (g)** :
```
sel (g) = sodium (mg) / 400
```

**Sel (g) → Sodium (mg)** :
```
sodium (mg) = sel (g) × 400
```

**Facteur de conversion** : Basé sur NaCl (58.44 g/mol)
- Na = 22.99 g/mol
- Cl = 35.45 g/mol
- Ratio = 58.44 / 22.99 ≈ 2.54
- En pratique : facteur 400 (incluant autres sels)

#### Graisses/Sucres

**mg → g** :
```
g = mg / 1000
```

**g → mg** :
```
mg = g × 1000
```

### 3.2 Nettoyage des Données

#### Gestion des Valeurs Manquantes

**Stratégie** :
1. Fibres manquantes → 0 (conservateur)
2. Fruits/légumes manquants → 0 (conservateur)
3. Autres critères manquants → NaN (exclusion)

**Implémentation** :
```python
def clean_missing_values(df):
    df['fiber'] = df['fiber'].fillna(0)
    df['fruits_veg'] = df['fruits_veg'].fillna(0)
    # Autres colonnes : conserver NaN pour validation
    return df
```

#### Détection des Valeurs Aberrantes

**Plages normales** :

| Critère | Min | Max | Unité |
|---------|-----|-----|-------|
| Énergie | 0 | 4000 | kJ/100g |
| Graisses sat. | 0 | 100 | g/100g |
| Sucres | 0 | 100 | g/100g |
| Sel | 0 | 10 | g/100g |
| Protéines | 0 | 100 | g/100g |
| Fibres | 0 | 50 | g/100g |
| Fruits/lég. | 0 | 100 | % |

**Action** :
- Valeur hors plage → Avertissement + marquage
- Utilisateur peut valider ou corriger

---

## 4️⃣ Métriques de Comparaison

### 4.1 Matrice de Confusion

Comparaison des classifications Nutri-Score vs ELECTRE TRI.

**Format** :

|               | ELECTRE A' | ELECTRE B' | ELECTRE C' | ELECTRE D' | ELECTRE E' |
|---------------|-----------|-----------|-----------|-----------|-----------|
| **Nutri-Score A** | TP(A) | ... | ... | ... | ... |
| **Nutri-Score B** | ... | TP(B) | ... | ... | ... |
| **Nutri-Score C** | ... | ... | TP(C) | ... | ... |
| **Nutri-Score D** | ... | ... | ... | TP(D) | ... |
| **Nutri-Score E** | ... | ... | ... | ... | TP(E) |

**Lecture** :
- Diagonale : Accords (même catégorie)
- Hors diagonale : Désaccords

### 4.2 Exactitude (Accuracy)

Proportion de classifications identiques.

**Formule** :
```
              Nombre de produits avec même label
Accuracy = ─────────────────────────────────────
                  Nombre total de produits
```

**Exemple** :
```
100 produits
78 avec même label (A=A', B=B', etc.)
→ Accuracy = 78/100 = 78%
```

### 4.3 Score F1 (Macro)

Moyenne harmonique de la précision et du rappel, par catégorie.

**Pour chaque catégorie** :
```
              TP
Précision = ─────────
            TP + FP

            TP
Rappel = ─────────
         TP + FN

            2 × Précision × Rappel
F1 score = ─────────────────────────
           Précision + Rappel
```

**F1 Macro** :
```
           F1(A) + F1(B) + F1(C) + F1(D) + F1(E)
F1 Macro = ──────────────────────────────────────
                          5
```

### 4.4 Erreur Absolue Moyenne (MAE)

Distance moyenne entre les catégories.

**Mapping numérique** :
- A/A' = 1, B/B' = 2, C/C' = 3, D/D' = 4, E/E' = 5

**Formule** :
```
       Σ |Nutri-Score - ELECTRE|
MAE = ────────────────────────────
              n
```

**Exemple** :
```
Produit 1 : B vs B' → |2-2| = 0
Produit 2 : C vs B' → |3-2| = 1
Produit 3 : A vs A' → |1-1| = 0

MAE = (0 + 1 + 0) / 3 = 0.33
```

**Interprétation** :
- MAE < 0.5 : Très bonne concordance
- 0.5 ≤ MAE < 1.0 : Bonne concordance
- MAE ≥ 1.0 : Concordance faible

---

## 5️⃣ Références

### Nutri-Score

- Santé Publique France (2023). "Nutri-Score : système d'information nutritionnelle"
- Arrêté du 31 octobre 2017 fixant la forme de présentation complémentaire à la déclaration nutritionnelle recommandée

### ELECTRE TRI

- Roy, B., & Bouyssou, D. (1993). "Aide multicritère à la décision : Méthodes et cas"
- Mousseau, V., & Slowinski, R. (1998). "Inferring an ELECTRE TRI model from assignment examples"

### Normalisations

- Règlement (UE) n° 1169/2011 concernant l'information des consommateurs sur les denrées alimentaires

---

**Date de mise à jour** : Décembre 2025  
**Version** : 1.0
