"""
Module de calcul du Nutri-Score officiel.
Implémente l'algorithme officiel de calcul du score et du label Nutri-Score.
"""

import pandas as pd
import numpy as np
import logging
from typing import Union, Tuple

# Configuration du logging
logger = logging.getLogger(__name__)

class NutriScoreCalculator:
    """Classe pour calculer le Nutri-Score selon l'algorithme officiel."""
    
    # Tables de points officielles pour les éléments à limiter (négatifs)
    ENERGY_POINTS = [
        (335, 0), (670, 1), (1005, 2), (1340, 3), (1675, 4),
        (2010, 5), (2345, 6), (2680, 7), (3015, 8), (3350, 9), (float('inf'), 10)
    ]
    
    SATURATED_FAT_POINTS = [
        (1, 0), (2, 1), (3, 2), (4, 3), (5, 4),
        (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (float('inf'), 10)
    ]
    
    SUGARS_POINTS = [
        (4.5, 0), (9, 1), (13.5, 2), (18, 3), (22.5, 4),
        (27, 5), (31, 6), (36, 7), (40, 8), (45, 9), (float('inf'), 10)
    ]
    
    SODIUM_POINTS = [
        (90, 0), (180, 1), (270, 2), (360, 3), (450, 4),
        (540, 5), (630, 6), (720, 7), (810, 8), (900, 9), (float('inf'), 10)
    ]
    
    # Tables de points pour les éléments favorables (positifs)
    FIBER_POINTS = [
        (0.9, 0), (1.9, 1), (2.8, 2), (3.7, 3), (4.7, 4), (float('inf'), 5)
    ]
    
    PROTEIN_POINTS = [
        (1.6, 0), (3.2, 1), (4.8, 2), (6.4, 3), (8.0, 4), (float('inf'), 5)
    ]
    
    FRUITS_VEG_POINTS = [
        (40, 0), (60, 1), (80, 2), (float('inf'), 5)
    ]
    
    # Tables de conversion score -> label
    SOLID_FOOD_THRESHOLDS = [
        (-1, 'A'), (2, 'B'), (10, 'C'), (18, 'D'), (float('inf'), 'E')
    ]
    
    BEVERAGE_THRESHOLDS = [
        (1, 'A'), (5, 'B'), (9, 'C'), (13, 'D'), (float('inf'), 'E')
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
        if pd.isna(value):
            return 0
        
        for threshold, points in points_table:
            if value <= threshold:
                return points
        
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
        points_detail = {}
        
        # Points énergie
        energy_points = NutriScoreCalculator._get_points_from_table(
            energy_kj, NutriScoreCalculator.ENERGY_POINTS
        )
        points_detail['energy'] = energy_points
        
        # Points AG saturés
        sat_fat_points = NutriScoreCalculator._get_points_from_table(
            saturated_fat_g, NutriScoreCalculator.SATURATED_FAT_POINTS
        )
        points_detail['saturated_fat'] = sat_fat_points
        
        # Points sucres
        sugar_points = NutriScoreCalculator._get_points_from_table(
            sugars_g, NutriScoreCalculator.SUGARS_POINTS
        )
        points_detail['sugars'] = sugar_points
        
        # Points sodium
        sodium_points = NutriScoreCalculator._get_points_from_table(
            sodium_mg, NutriScoreCalculator.SODIUM_POINTS
        )
        points_detail['sodium'] = sodium_points
        
        total_negative = energy_points + sat_fat_points + sugar_points + sodium_points
        
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
        points_detail = {}
        
        # Points fibres
        fiber_points = NutriScoreCalculator._get_points_from_table(
            fiber_g, NutriScoreCalculator.FIBER_POINTS
        )
        points_detail['fiber'] = fiber_points
        
        # Points fruits/légumes/noix
        fruits_points = NutriScoreCalculator._get_points_from_table(
            fruits_veg_nuts_percent, NutriScoreCalculator.FRUITS_VEG_POINTS
        )
        points_detail['fruits_veg_nuts'] = fruits_points
        
        # Points protéines (avec règle spéciale)
        protein_points = NutriScoreCalculator._get_points_from_table(
            protein_g, NutriScoreCalculator.PROTEIN_POINTS
        )
        
        # Règle officielle : si points négatifs >= 11 ET fruits < 80%, 
        # ne pas compter les protéines
        if negative_points >= 11 and fruits_veg_nuts_percent < 80:
            protein_points = 0
            points_detail['protein'] = 0
            points_detail['protein_rule_applied'] = True
            logger.debug(f"Règle protéines appliquée : points négatifs={negative_points}, "
                        f"fruits={fruits_veg_nuts_percent}%")
        else:
            points_detail['protein'] = protein_points
            points_detail['protein_rule_applied'] = False
        
        total_positive = fiber_points + protein_points + fruits_points
        
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
        # Validation des données
        values = [energy_kj, saturated_fat_g, sugars_g, sodium_mg, 
                 fiber_g, protein_g, fruits_veg_nuts_percent]
        
        if any(pd.isna(val) for val in values):
            missing_values = [name for name, val in zip(
                ['energy', 'saturated_fat', 'sugars', 'sodium', 
                 'fiber', 'protein', 'fruits_veg_nuts'], values
            ) if pd.isna(val)]
            logger.warning(f"Valeurs manquantes pour le calcul Nutri-Score : {missing_values}")
        
        # Calcul des points négatifs
        negative_points, negative_detail = NutriScoreCalculator.compute_negative_points(
            energy_kj, saturated_fat_g, sugars_g, sodium_mg
        )
        
        # Calcul des points positifs
        positive_points, positive_detail = NutriScoreCalculator.compute_positive_points(
            fiber_g, protein_g, fruits_veg_nuts_percent, negative_points
        )
        
        # Score final
        final_score = negative_points - positive_points
        
        # Détail complet
        calculation_detail = {
            'negative_points': negative_points,
            'positive_points': positive_points,
            'final_score': final_score,
            'negative_detail': negative_detail,
            'positive_detail': positive_detail
        }
        
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
        if pd.isna(score):
            return 'N/A'
        
        # Choisir les seuils selon le type d'aliment
        thresholds = (NutriScoreCalculator.SOLID_FOOD_THRESHOLDS if is_solid 
                     else NutriScoreCalculator.BEVERAGE_THRESHOLDS)
        
        for threshold, label in thresholds:
            if score <= threshold:
                return label
        
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
        try:
            # Extraction des valeurs
            energy = row.get('energy_100g', np.nan)
            saturated_fat = row.get('saturated_fat_100g', np.nan)
            sugars = row.get('sugars_100g', np.nan)
            sodium = row.get('sodium_100g', np.nan)
            fiber = row.get('fiber_100g', np.nan)
            protein = row.get('proteins_100g', np.nan)
            fruits_veg = row.get('fruits_veg_nuts_percent', np.nan)
            
            # Calcul du score
            score, details = NutriScoreCalculator.compute_nutriscore_score(
                energy, saturated_fat, sugars, sodium, fiber, protein, fruits_veg
            )
            
            # Conversion en label
            label = NutriScoreCalculator.score_to_label(score, is_solid)
            
            return {
                'ns_score_calc': score,
                'ns_label_calc': label,
                'ns_calculation_details': details
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul Nutri-Score pour ligne : {e}")
            return {
                'ns_score_calc': np.nan,
                'ns_label_calc': 'ERROR',
                'ns_calculation_details': {'error': str(e)}
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
    logger.info(f"Application du calcul Nutri-Score à {len(df)} produits")
    
    df_result = df.copy()
    
    # Application ligne par ligne
    nutriscore_results = df.apply(
        lambda row: NutriScoreCalculator.compute_nutriscore_row(row, is_solid), 
        axis=1
    )
    
    # Extraction des résultats
    df_result['ns_score_calc'] = nutriscore_results.apply(lambda x: x['ns_score_calc'])
    df_result['ns_label_calc'] = nutriscore_results.apply(lambda x: x['ns_label_calc'])
    
    # Statistiques
    valid_scores = df_result['ns_score_calc'].dropna()
    if len(valid_scores) > 0:
        logger.info(f"Nutri-Score calculé pour {len(valid_scores)} produits")
        logger.info(f"Distribution des labels : {df_result['ns_label_calc'].value_counts().to_dict()}")
        logger.info(f"Score moyen : {valid_scores.mean():.1f}, médiane : {valid_scores.median():.1f}")
    else:
        logger.warning("Aucun score Nutri-Score calculé")
    
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
    score, details = NutriScoreCalculator.compute_nutriscore_score(
        energy_kj, saturated_fat_g, sugars_g, sodium_mg, 
        fiber_g, protein_g, fruits_veg_nuts_percent
    )
    
    label = NutriScoreCalculator.score_to_label(score, is_solid)
    
    return {
        'score': score,
        'label': label,
        'details': details
    }


if __name__ == "__main__":
    # Tests du module
    print("=== Test du calcul Nutri-Score ===")
    
    # Test avec des valeurs d'exemple
    test_cases = [
        {
            'name': 'Produit A (excellent)',
            'energy_kj': 300,
            'saturated_fat_g': 0.5,
            'sugars_g': 2.0,
            'sodium_mg': 50,
            'fiber_g': 3.0,
            'protein_g': 5.0,
            'fruits_veg_nuts_percent': 60
        },
        {
            'name': 'Produit E (mauvais)',
            'energy_kj': 2500,
            'saturated_fat_g': 15.0,
            'sugars_g': 40.0,
            'sodium_mg': 1000,
            'fiber_g': 0.1,
            'protein_g': 2.0,
            'fruits_veg_nuts_percent': 0
        }
    ]
    
    for test_case in test_cases:
        name = test_case.pop('name')
        result = compute_nutriscore_single(**test_case)
        
        print(f"\n{name}:")
        print(f"  Score: {result['score']}")
        print(f"  Label: {result['label']}")
        print(f"  Points négatifs: {result['details']['negative_points']}")
        print(f"  Points positifs: {result['details']['positive_points']}")
    
    print("\nTests terminés avec succès !")