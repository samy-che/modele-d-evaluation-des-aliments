# Documentation du Projet

Bienvenue dans la documentation complète du projet **Modèle d'Évaluation des Aliments**.

## 📚 Guides Disponibles

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md)
**Description** : Structure complète du projet, organisation des modules et flux de données.

**Contenu** :
- Vue d'ensemble de l'architecture
- Structure des dossiers et fichiers
- Description détaillée de chaque module
- Diagrammes de flux
- Points d'extension et personnalisation

**À lire si vous voulez** :
- Comprendre l'organisation du code
- Contribuer au projet
- Étendre les fonctionnalités

---

### 🛠️ [GUIDE_INSTALLATION.md](GUIDE_INSTALLATION.md)
**Description** : Instructions complètes pour installer et configurer le projet.

**Contenu** :
- Prérequis système
- Installation pas à pas
- Configuration de l'environnement virtuel
- Vérification de l'installation
- Résolution des problèmes courants

**À lire si vous** :
- Installez le projet pour la première fois
- Rencontrez des problèmes d'installation
- Devez déployer sur un nouveau système

---

### 📖 [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)
**Description** : Manuel d'utilisation de l'interface Streamlit et des fonctionnalités.

**Contenu** :
- Guide de démarrage rapide
- Utilisation de l'interface web
- Calcul unitaire et par lots
- Interprétation des résultats
- Cas d'usage pratiques
- Résolution de problèmes

**À lire si vous** :
- Utilisez l'application pour la première fois
- Voulez analyser des produits alimentaires
- Cherchez à comprendre les résultats

---

### 🧮 [METHODES_CALCUL.md](METHODES_CALCUL.md)
**Description** : Documentation technique détaillée des algorithmes et formules.

**Contenu** :
- Calcul Nutri-Score officiel
- Méthode ELECTRE TRI-B
- Normalisation des données
- Métriques de comparaison
- Exemples de calcul pas à pas
- Références scientifiques

**À lire si vous** :
- Voulez comprendre les méthodes en profondeur
- Devez valider les calculs
- Souhaitez adapter les algorithmes

---

### 🔧 [API_REFERENCE.md](API_REFERENCE.md)
**Description** : Référence complète de l'API pour l'utilisation programmatique.

**Contenu** :
- Documentation de toutes les classes
- Signatures des fonctions
- Paramètres et types de retour
- Exemples de code
- Bonnes pratiques de développement

**À lire si vous** :
- Intégrez le code dans vos applications
- Développez de nouvelles fonctionnalités
- Créez des scripts personnalisés

---

## 🚀 Par où commencer ?

### Pour les utilisateurs

1. **Installation** : [GUIDE_INSTALLATION.md](GUIDE_INSTALLATION.md)
2. **Utilisation** : [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)
3. **Comprendre les résultats** : [METHODES_CALCUL.md](METHODES_CALCUL.md)

### Pour les développeurs

1. **Installation** : [GUIDE_INSTALLATION.md](GUIDE_INSTALLATION.md)
2. **Architecture** : [ARCHITECTURE.md](ARCHITECTURE.md)
3. **API** : [API_REFERENCE.md](API_REFERENCE.md)
4. **Méthodes** : [METHODES_CALCUL.md](METHODES_CALCUL.md)

### Pour les chercheurs

1. **Méthodes** : [METHODES_CALCUL.md](METHODES_CALCUL.md)
2. **Architecture** : [ARCHITECTURE.md](ARCHITECTURE.md)
3. **API** : [API_REFERENCE.md](API_REFERENCE.md)

---

## 📝 Structure de la Documentation

```
docs/
├── README.md                  # Ce fichier (index)
├── ARCHITECTURE.md           # Architecture du projet
├── GUIDE_INSTALLATION.md     # Guide d'installation
├── GUIDE_UTILISATION.md      # Guide utilisateur
├── METHODES_CALCUL.md        # Documentation technique
└── API_REFERENCE.md          # Référence API
```

---

## 🔍 Recherche Rapide

### Installation et Configuration
- [Installer Python](GUIDE_INSTALLATION.md#prérequis)
- [Créer un environnement virtuel](GUIDE_INSTALLATION.md#étape-1--créer-un-environnement-virtuel-recommandé)
- [Installer les dépendances](GUIDE_INSTALLATION.md#étape-3--installer-les-dépendances)
- [Lancer Streamlit](GUIDE_UTILISATION.md#lancer-lapplication)

### Utilisation
- [Calculer le Nutri-Score d'un produit](GUIDE_UTILISATION.md#méthode-1--saisie-manuelle)
- [Traiter un fichier Excel](GUIDE_UTILISATION.md#onglet-traitement-dataset)
- [Interpréter les résultats](GUIDE_UTILISATION.md#interprétation-des-résultats)
- [Exporter les résultats](GUIDE_UTILISATION.md#étape-5--exporter-les-résultats)

### Développement
- [Structure des modules](ARCHITECTURE.md#modules-principaux)
- [Ajouter un critère ELECTRE](ARCHITECTURE.md#ajouter-un-nouveau-critère)
- [Utiliser l'API Nutri-Score](API_REFERENCE.md#module-nutriscorepy)
- [Personnaliser ELECTRE TRI](API_REFERENCE.md#exemple-3--configuration-personnalisée-electre)

### Méthodes
- [Formule Nutri-Score](METHODES_CALCUL.md#11-points-défavorables-négatifs)
- [Algorithme ELECTRE TRI](METHODES_CALCUL.md#25-procédures-de-tri)
- [Normalisation des données](METHODES_CALCUL.md#31-conversions-dunités)
- [Métriques de comparaison](METHODES_CALCUL.md#4️⃣-métriques-de-comparaison)

---

## ❓ FAQ Rapide

### Questions Générales

**Q : Qu'est-ce que ce projet ?**  
R : Outil de comparaison entre Nutri-Score (officiel français) et ELECTRE TRI (méthode multicritère) pour l'évaluation nutritionnelle.

**Q : À qui s'adresse ce projet ?**  
R : Nutritionnistes, chercheurs, industriels, développeurs, ou toute personne intéressée par l'évaluation nutritionnelle.

**Q : Est-ce que le Nutri-Score calculé est officiel ?**  
R : Le calcul suit l'algorithme officiel 2025, mais pour un label officiel, consultez [santepubliquefrance.fr](https://www.santepubliquefrance.fr/nutriscore).

### Questions Techniques

**Q : Quelles sont les versions Python supportées ?**  
R : Python 3.10+. Voir [GUIDE_INSTALLATION.md](GUIDE_INSTALLATION.md#prérequis).

**Q : Comment personnaliser les poids ELECTRE ?**  
R : Modifier `config/electre.yml` ou utiliser le paramètre `custom_weights`. Voir [ARCHITECTURE.md](ARCHITECTURE.md#configelectreyml).

**Q : Puis-je utiliser ce code dans mon projet ?**  
R : Oui, consultez [API_REFERENCE.md](API_REFERENCE.md) pour l'intégration.

### Questions d'Utilisation

**Q : Comment charger mes propres données ?**  
R : Format Excel/CSV avec colonnes mappées dans `config/columns.yml`. Voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md#étape-1--charger-les-données).

**Q : Que faire si les colonnes ne correspondent pas ?**  
R : Ajouter des synonymes dans `config/columns.yml`. Voir [ARCHITECTURE.md](ARCHITECTURE.md#configcolumnsyml).

**Q : Pourquoi Nutri-Score et ELECTRE diffèrent ?**  
R : Approches différentes (score vs profils). Voir [METHODES_CALCUL.md](METHODES_CALCUL.md).

---

## 🛟 Aide et Support

### Problèmes d'installation
→ [GUIDE_INSTALLATION.md - Résolution de Problèmes](GUIDE_INSTALLATION.md#résolution-de-problèmes)

### Erreurs d'utilisation
→ [GUIDE_UTILISATION.md - Résolution de Problèmes](GUIDE_UTILISATION.md#résolution-de-problèmes)

### Questions sur les méthodes
→ [METHODES_CALCUL.md](METHODES_CALCUL.md)

### Développement
→ [API_REFERENCE.md](API_REFERENCE.md)

---

## 📊 Exemples Rapides

### Exemple 1 : Calcul Simple

```python
from app.nutriscore import compute_nutriscore_single

result = compute_nutriscore_single(
    energy_kj=1650,
    saturated_fat_g=3.2,
    sugars_g=25,
    sodium_mg_or_salt_g=900,
    fiber_g=5.5,
    protein_g=8,
    fruits_veg_nuts_percent=0
)

print(f"{result['label']} (score: {result['score']})")
```

Plus de détails : [API_REFERENCE.md - compute_nutriscore_single()](API_REFERENCE.md#compute_nutriscore_single)

### Exemple 2 : Classification ELECTRE

```python
from app.electre_tri import classify_single_product

product = {
    'energy': 1650,
    'saturated_fat': 3.2,
    'sugars': 25,
    'salt': 0.9,
    'protein': 8,
    'fiber': 5.5,
    'fruits_veg': 0
}

result = classify_single_product(product, variant="pessimistic")
print(f"Catégorie: {result['class']}")
```

Plus de détails : [API_REFERENCE.md - classify_single_product()](API_REFERENCE.md#classify_single_product)

---

## 🔗 Liens Utiles

### Ressources Externes

- [Nutri-Score officiel](https://www.santepubliquefrance.fr/nutriscore)
- [Open Food Facts](https://world.openfoodfacts.org/)
- [ELECTRE methods (Wikipedia)](https://en.wikipedia.org/wiki/ELECTRE)
- [Streamlit documentation](https://docs.streamlit.io/)

### Code Source

- [README.md principal](../README.md)
- [Fichiers de configuration](../config/)
- [Tests unitaires](../tests/)

---

## 📅 Historique des Versions

### Version 1.0 (Décembre 2025)
- Documentation complète créée
- 5 guides détaillés
- Exemples et cas d'usage
- API complètement documentée

---

## ✍️ Contribuer à la Documentation

Pour améliorer cette documentation :

1. Identifier la section à améliorer
2. Modifier le fichier Markdown correspondant
3. Tester les exemples de code
4. Soumettre les modifications

---

**Dernière mise à jour** : 31 Décembre 2025  
**Mainteneur** : Équipe du projet
