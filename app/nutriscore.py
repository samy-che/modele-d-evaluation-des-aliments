"""
Module de calcul du Nutri-Score officiel.
Implémente l'algorithme officiel de calcul du score et du label Nutri-Score.
"""

# Import des bibliothèques nécessaires
import pandas as pd  # Pour manipuler les données sous forme de DataFrames
import numpy as np   # Pour les calculs numériques et la gestion des valeurs NaN
import logging      # Pour enregistrer les logs et messages de débogage
from typing import Union, Tuple  # Pour les annotations de types

# Configuration du système de logging pour tracer l'exécution
logger = logging.getLogger(__name__)  # Créer un logger spécifique à ce module

class NutriScoreCalculator:
    """Classe pour calculer le Nutri-Score selon l'algorithme officiel."""
    
    # Tables de points officielles pour les éléments à limiter (négatifs)
    # Table des points pour l'énergie (kJ pour 100g) - plus c'est élevé, plus c'est pénalisé
    ENERGY_POINTS = [
        (335, 0), (670, 1), (1005, 2), (1340, 3), (1675, 4),     # Faible énergie = 0-4 pts
        (2010, 5), (2345, 6), (2680, 7), (3015, 8), (3350, 9), (float('inf'), 10)  # Haute énergie = 5-10 pts
    ]
    
    # Table des points pour les acides gras saturés (g pour 100g)
    SATURATED_FAT_POINTS = [
        (1, 0), (2, 1), (3, 2), (4, 3), (5, 4),    # Faible AG saturés = 0-4 pts
        (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (float('inf'), 10)  # Élevé AG saturés = 5-10 pts
    ]
    
    # Table des points pour les sucres (g pour 100g)
    SUGARS_POINTS = [
        (4.5, 0), (9, 1), (13.5, 2), (18, 3), (22.5, 4),    # Faible sucre = 0-4 pts
        (27, 5), (31, 6), (36, 7), (40, 8), (45, 9), (float('inf'), 10)  # Élevé sucre = 5-10 pts
    ]
    
    # Table des points pour le sodium (mg pour 100g)
    SODIUM_POINTS = [
        (90, 0), (180, 1), (270, 2), (360, 3), (450, 4),     # Faible sodium = 0-4 pts
        (540, 5), (630, 6), (720, 7), (810, 8), (900, 9), (float('inf'), 10)  # Élevé sodium = 5-10 pts
    ]
    
    # Tables de points pour les éléments favorables (positifs) - réduisent le score
    # Table des points pour les fibres (g pour 100g) - plus c'est élevé, mieux c'est
    FIBER_POINTS = [
        (0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4), (float('inf'), 5)  # 0-5 pts positifs
    ]
    
    # Table des points pour les protéines (g pour 100g) - plus c'est élevé, mieux c'est
    PROTEIN_POINTS = [
        (1.6, 0), (3.2, 1), (4.8, 2), (6.4, 3), (8.0, 4), (float('inf'), 5)  # 0-5 pts positifs
    ]
    
    # Table des points pour les fruits/légumes/noix (% du produit)
    FRUITS_VEG_POINTS = [
        (40, 0), (60, 1), (80, 2), (float('inf'), 5)  # 0, 1, 2 ou 5 pts positifs selon %
    ]
    
    # Tables de conversion score final -> label Nutri-Score
    # Seuils pour les aliments solides (plus stricts)
    SOLID_FOOD_THRESHOLDS = [
        (-1, 'A'), (2, 'B'), (10, 'C'), (18, 'D'), (float('inf'), 'E')  # Score ≤ -1=A, ≤2=B, etc.
    ]
    
    # Seuils pour les boissons (moins stricts car naturellement moins bonnes)
    BEVERAGE_THRESHOLDS = [
        (1, 'A'), (5, 'B'), (9, 'C'), (13, 'D'), (float('inf'), 'E')   # Score ≤1=A, ≤5=B, etc.
    ]
    
    @staticmethod
    def _get_points_from_table(value: float, points_table: list) -> int:
        """
        Obtient les points à partir d'une table de correspondance.
        
        Args:
            value: Valeur à évaluer
            points_table: Table de points [(seuil, points), ...]
            
        Returns:
            Nombre de points
        """
        # Gérer les valeurs manquantes en retournant 0 points
        if pd.isna(value):
            return 0
        
        # Parcourir la table de points pour trouver le bon intervalle
        for threshold, points in points_table:
            # Si la valeur est inférieure ou égale au seuil, retourner les points correspondants
            if value <= threshold:
                return points
        
        # Si aucun seuil n'est trouvé, retourner les points du dernier seuil (cas extrême)
        return points_table[-1][1]  # Valeur par défaut (dernière)
    
    @staticmethod
    def compute_negative_points(energy_kj: float, 
                               saturated_fat_g: float, 
                               sugars_g: float, 
                               sodium_mg: float) -> Tuple[int, dict]:
        """
        Calcule les points négatifs (éléments à limiter).
        
        Args:
            energy_kj: Énergie en kJ pour 100g
            saturated_fat_g: AG saturés en g pour 100g
            sugars_g: Sucres en g pour 100g
            sodium_mg: Sodium en mg pour 100g
            
        Returns:
            Tuple (total points négatifs, détail par composant)
        """
        # Dictionnaire pour stocker le détail des points par composant
        points_detail = {}
        
        # Calculer les points négatifs pour l'énergie en utilisant la table officielle
        energy_points = NutriScoreCalculator._get_points_from_table(
            energy_kj, NutriScoreCalculator.ENERGY_POINTS
        )
        points_detail['energy'] = energy_points  # Sauvegarder pour traçabilité
        
        # Calculer les points négatifs pour les acides gras saturés
        sat_fat_points = NutriScoreCalculator._get_points_from_table(
            saturated_fat_g, NutriScoreCalculator.SATURATED_FAT_POINTS
        )
        points_detail['saturated_fat'] = sat_fat_points  # Sauvegarder pour traçabilité
        
        # Calculer les points négatifs pour les sucres
        sugar_points = NutriScoreCalculator._get_points_from_table(
            sugars_g, NutriScoreCalculator.SUGARS_POINTS
        )
        points_detail['sugars'] = sugar_points  # Sauvegarder pour traçabilité
        
        # Calculer les points négatifs pour le sodium
        sodium_points = NutriScoreCalculator._get_points_from_table(
            sodium_mg, NutriScoreCalculator.SODIUM_POINTS
        )
        points_detail['sodium'] = sodium_points  # Sauvegarder pour traçabilité
        
        # Calculer le total des points négatifs (somme de tous les éléments défavorables)
        total_negative = energy_points + sat_fat_points + sugar_points + sodium_points
        
        # Retourner le total et le détail pour traçabilité
        return total_negative, points_detail
    
    @staticmethod
    def compute_positive_points(fiber_g: float, 
                               protein_g: float, 
                               fruits_veg_nuts_percent: float,
                               negative_points: int) -> Tuple[int, dict]:
        """
        Calcule les points positifs (éléments favorables).
        
        Args:
            fiber_g: Fibres en g pour 100g
            protein_g: Protéines en g pour 100g
            fruits_veg_nuts_percent: % fruits/légumes/noix
            negative_points: Points négatifs pour appliquer la règle des protéines
            
        Returns:
            Tuple (total points positifs, détail par composant)
        """
        # Dictionnaire pour stocker le détail des points par composant
        points_detail = {}
        
        # Calculer les points positifs pour les fibres (toujours comptabilisées)
        fiber_points = NutriScoreCalculator._get_points_from_table(
            fiber_g, NutriScoreCalculator.FIBER_POINTS
        )
        points_detail['fiber'] = fiber_points  # Sauvegarder pour traçabilité
        
        # Calculer les points positifs pour les fruits/légumes/noix (toujours comptabilisés)
        fruits_points = NutriScoreCalculator._get_points_from_table(
            fruits_veg_nuts_percent, NutriScoreCalculator.FRUITS_VEG_POINTS
        )
        points_detail['fruits_veg_nuts'] = fruits_points  # Sauvegarder pour traçabilité
        
        # Calculer les points protéines de base selon la table officielle
        protein_points = NutriScoreCalculator._get_points_from_table(
            protein_g, NutriScoreCalculator.PROTEIN_POINTS
        )
        
        # Appliquer la règle officielle spéciale pour les protéines
        # Si points négatifs >= 11 ET fruits/légumes < 80%, ne pas compter les protéines
        if negative_points >= 11 and fruits_veg_nuts_percent < 80:
            protein_points = 0  # Annuler les points protéines
            points_detail['protein'] = 0  # Sauvegarder la valeur finale
            points_detail['protein_rule_applied'] = True  # Indiquer que la règle est appliquée
            # Enregistrer l'application de la règle dans les logs pour traçabilité
            logger.debug(f"Règle protéines appliquée : points négatifs={negative_points}, "
                        f"fruits={fruits_veg_nuts_percent}%")
        else:
            # Garder les points protéines normaux si la règle ne s'applique pas
            points_detail['protein'] = protein_points
            points_detail['protein_rule_applied'] = False  # Indiquer que la règle n'est pas appliquée
        
        # Calculer le total des points positifs (fibres + protéines + fruits/légumes)
        total_positive = fiber_points + protein_points + fruits_points
        
        # Retourner le total et le détail pour traçabilité
        return total_positive, points_detail
    
    @staticmethod
    def compute_nutriscore_score(energy_kj: float,
                                saturated_fat_g: float,
                                sugars_g: float, 
                                sodium_mg: float,
                                fiber_g: float,
                                protein_g: float,
                                fruits_veg_nuts_percent: float) -> Tuple[int, dict]:
        """
        Calcule le score Nutri-Score complet.
        
        Args:
            energy_kj: Énergie en kJ pour 100g
            saturated_fat_g: AG saturés en g pour 100g
            sugars_g: Sucres en g pour 100g
            sodium_mg: Sodium en mg pour 100g
            fiber_g: Fibres en g pour 100g
            protein_g: Protéines en g pour 100g
            fruits_veg_nuts_percent: % fruits/légumes/noix
            
        Returns:
            Tuple (score final, détail du calcul)
        """
        # Regrouper toutes les valeurs d'entrée pour validation
        values = [energy_kj, saturated_fat_g, sugars_g, sodium_mg, 
                 fiber_g, protein_g, fruits_veg_nuts_percent]
        
        # Vérifier s'il y a des valeurs manquantes et les signaler
        if any(pd.isna(val) for val in values):
            # Identifier précisément quelles valeurs sont manquantes
            missing_values = [name for name, val in zip(
                ['energy', 'saturated_fat', 'sugars', 'sodium', 
                 'fiber', 'protein', 'fruits_veg_nuts'], values
            ) if pd.isna(val)]
            # Avertir de la présence de valeurs manquantes (peut affecter le calcul)
            logger.warning(f"Valeurs manquantes pour le calcul Nutri-Score : {missing_values}")
        
        # Étape 1 : Calculer les points négatifs (éléments défavorables)
        negative_points, negative_detail = NutriScoreCalculator.compute_negative_points(
            energy_kj, saturated_fat_g, sugars_g, sodium_mg
        )
        
        # Étape 2 : Calculer les points positifs (éléments favorables)
        # Passer negative_points pour appliquer la règle spéciale des protéines
        positive_points, positive_detail = NutriScoreCalculator.compute_positive_points(
            fiber_g, protein_g, fruits_veg_nuts_percent, negative_points
        )
        
        # Étape 3 : Calculer le score final (formule officielle : négatifs - positifs)
        final_score = negative_points - positive_points
        
        # Créer un dictionnaire détaillé pour traçabilité complète
        calculation_detail = {
            'negative_points': negative_points,      # Total des points négatifs
            'positive_points': positive_points,      # Total des points positifs
            'final_score': final_score,             # Score final calculé
            'negative_detail': negative_detail,      # Détail par composant négatif
            'positive_detail': positive_detail       # Détail par composant positif
        }
        
        # Retourner le score final et tous les détails de calcul
        return final_score, calculation_detail
    
    @staticmethod
    def score_to_label(score: int, is_solid: bool = True) -> str:
        """
        Convertit un score en label Nutri-Score (A à E).
        
        Args:
            score: Score Nutri-Score calculé
            is_solid: True pour aliments solides, False pour boissons
            
        Returns:
            Label Nutri-Score (A, B, C, D ou E)
        """
        # Gérer les scores manquants ou invalides
        if pd.isna(score):
            return 'N/A'
        
        # Sélectionner la table de seuils appropriée selon le type d'aliment
        # Les boissons ont des seuils plus permissifs que les aliments solides
        thresholds = (NutriScoreCalculator.SOLID_FOOD_THRESHOLDS if is_solid 
                     else NutriScoreCalculator.BEVERAGE_THRESHOLDS)
        
        # Parcourir les seuils pour trouver le label correspondant au score
        for threshold, label in thresholds:
            # Si le score est inférieur ou égal au seuil, assigner le label
            if score <= threshold:
                return label
        
        # Cas de sécurité : si aucun seuil n'est trouvé, retourner le pire label
        return 'E'  # Par défaut
    
    @staticmethod
    def compute_nutriscore_row(row: pd.Series, is_solid: bool = True) -> dict:
        """
        Calcule le Nutri-Score pour une ligne de DataFrame.
        
        Args:
            row: Ligne du DataFrame avec les colonnes nutritionnelles
            is_solid: Type d'aliment (solide ou boisson)
            
        Returns:
            Dictionnaire avec score, label et détails
        """
        # Bloc try-except pour gérer les erreurs potentielles
        try:
            # Extraire les valeurs nutritionnelles de la ligne avec noms de colonnes standardisés
            energy = row.get('energy_100g', np.nan)              # Énergie en kJ
            saturated_fat = row.get('saturated_fat_100g', np.nan) # AG saturés en g
            sugars = row.get('sugars_100g', np.nan)              # Sucres en g
            sodium = row.get('sodium_100g', np.nan)              # Sodium en mg
            fiber = row.get('fiber_100g', np.nan)                # Fibres en g
            protein = row.get('proteins_100g', np.nan)           # Protéines en g
            fruits_veg = row.get('fruits_veg_nuts_percent', np.nan) # % fruits/légumes/noix
            
            # Appeler la méthode principale de calcul du score Nutri-Score
            score, details = NutriScoreCalculator.compute_nutriscore_score(
                energy, saturated_fat, sugars, sodium, fiber, protein, fruits_veg
            )
            
            # Convertir le score numérique en label alphabétique (A-E)
            label = NutriScoreCalculator.score_to_label(score, is_solid)
            
            # Retourner un dictionnaire structuré avec tous les résultats
            return {
                'ns_score_calc': score,                    # Score numérique calculé
                'ns_label_calc': label,                    # Label alphabétique (A-E)
                'ns_calculation_details': details         # Détails complets du calcul
            }
            
        except Exception as e:
            # Gérer toute erreur survenant pendant le calcul
            logger.error(f"Erreur calcul Nutri-Score pour ligne : {e}")
            # Retourner un dictionnaire d'erreur avec valeurs par défaut
            return {
                'ns_score_calc': np.nan,           # Score invalide
                'ns_label_calc': 'ERROR',          # Label d'erreur
                'ns_calculation_details': {'error': str(e)}  # Message d'erreur détaillé
            }


def apply_nutriscore(df: pd.DataFrame, is_solid: bool = True) -> pd.DataFrame:
    """
    Applique le calcul Nutri-Score à un DataFrame entier.
    
    Args:
        df: DataFrame avec les données nutritionnelles
        is_solid: Type d'aliment pour tous les produits
        
    Returns:
        DataFrame avec colonnes ns_score_calc et ns_label_calc ajoutées
    """
    # Enregistrer le début du processus dans les logs
    logger.info(f"Application du calcul Nutri-Score à {len(df)} produits")
    
    # Créer une copie du DataFrame pour éviter de modifier l'original
    df_result = df.copy()
    
    # Appliquer le calcul Nutri-Score à chaque ligne du DataFrame
    nutriscore_results = df.apply(
        # Fonction lambda qui calcule le Nutri-Score pour chaque ligne
        lambda row: NutriScoreCalculator.compute_nutriscore_row(row, is_solid), 
        axis=1  # Appliquer sur les lignes (pas les colonnes)
    )
    
    # Extraire les scores calculés et les ajouter au DataFrame résultat
    df_result['ns_score_calc'] = nutriscore_results.apply(lambda x: x['ns_score_calc'])
    # Extraire les labels calculés et les ajouter au DataFrame résultat
    df_result['ns_label_calc'] = nutriscore_results.apply(lambda x: x['ns_label_calc'])
    
    # Calculer et afficher les statistiques sur les résultats
    valid_scores = df_result['ns_score_calc'].dropna()  # Récupérer seulement les scores valides
    if len(valid_scores) > 0:
        # Afficher les statistiques de succès
        logger.info(f"Nutri-Score calculé pour {len(valid_scores)} produits")
        # Afficher la distribution des labels (combien de A, B, C, D, E)
        logger.info(f"Distribution des labels : {df_result['ns_label_calc'].value_counts().to_dict()}")
        # Afficher les statistiques descriptives des scores
        logger.info(f"Score moyen : {valid_scores.mean():.1f}, médiane : {valid_scores.median():.1f}")
    else:
        # Avertir si aucun score n'a pu être calculé
        logger.warning("Aucun score Nutri-Score calculé")
    
    # Retourner le DataFrame enrichi avec les colonnes Nutri-Score
    return df_result


def compute_nutriscore_single(energy_kj: float = 0,
                             saturated_fat_g: float = 0,
                             sugars_g: float = 0,
                             sodium_mg: float = 0,
                             fiber_g: float = 0,
                             protein_g: float = 0,
                             fruits_veg_nuts_percent: float = 0,
                             is_solid: bool = True) -> dict:
    """
    Calcule le Nutri-Score pour des valeurs individuelles.
    
    Args:
        energy_kj: Énergie en kJ
        saturated_fat_g: AG saturés en g
        sugars_g: Sucres en g
        sodium_mg: Sodium en mg
        fiber_g: Fibres en g
        protein_g: Protéines en g
        fruits_veg_nuts_percent: % fruits/légumes/noix
        is_solid: Type d'aliment
        
    Returns:
        Dictionnaire avec score, label et détails
    """
    # Appeler la méthode principale de calcul du score avec toutes les valeurs nutritionnelles
    score, details = NutriScoreCalculator.compute_nutriscore_score(
        energy_kj, saturated_fat_g, sugars_g, sodium_mg, 
        fiber_g, protein_g, fruits_veg_nuts_percent
    )
    
    # Convertir le score numérique en label alphabétique
    label = NutriScoreCalculator.score_to_label(score, is_solid)
    
    # Retourner un dictionnaire structuré avec les résultats
    return {
        'score': score,      # Score numérique final
        'label': label,      # Label alphabétique (A-E)
        'details': details   # Détails complets du calcul
    }


if __name__ == "__main__":
    # Section de test du module (exécutée uniquement si le fichier est lancé directement)
    print("=== Test du calcul Nutri-Score ===")
    
    # Définir des cas de test avec des profils nutritionnels différents
    test_cases = [
        {
            'name': 'Produit A (excellent)',        # Produit avec profil nutritionnel favorable
            'energy_kj': 300,                       # Faible énergie
            'saturated_fat_g': 0.5,                 # Peu d'acides gras saturés
            'sugars_g': 2.0,                        # Peu de sucres
            'sodium_mg': 50,                        # Peu de sodium
            'fiber_g': 3.0,                         # Bonne teneur en fibres
            'protein_g': 5.0,                       # Bonne teneur en protéines
            'fruits_veg_nuts_percent': 60           # Bon pourcentage de fruits/légumes
        },
        {
            'name': 'Produit E (mauvais)',          # Produit avec profil nutritionnel défavorable
            'energy_kj': 2500,                      # Énergie élevée
            'saturated_fat_g': 15.0,                # Beaucoup d'acides gras saturés
            'sugars_g': 40.0,                       # Beaucoup de sucres
            'sodium_mg': 1000,                      # Beaucoup de sodium
            'fiber_g': 0.1,                         # Très peu de fibres
            'protein_g': 2.0,                       # Peu de protéines
            'fruits_veg_nuts_percent': 0            # Aucun fruit/légume
        }
    ]
    
    # Tester chaque cas et afficher les résultats
    for test_case in test_cases:
        # Extraire le nom du test et le retirer du dictionnaire des paramètres
        name = test_case.pop('name')
        # Calculer le Nutri-Score avec les paramètres restants
        result = compute_nutriscore_single(**test_case)
        
        # Afficher les résultats de manière structurée
        print(f"\n{name}:")
        print(f"  Score: {result['score']}")                              # Score numérique final
        print(f"  Label: {result['label']}")                              # Label alphabétique
        print(f"  Points négatifs: {result['details']['negative_points']}") # Total points défavorables
        print(f"  Points positifs: {result['details']['positive_points']}") # Total points favorables
    
    # Message de fin des tests
    print("\nTests terminés avec succès !")