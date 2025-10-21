"""
Module de normalisation des données nutritionnelles.
Gère les conversions d'unités et le nettoyage des données.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

class DataNormalizer:
    """Classe pour normaliser les données nutritionnelles."""
    
    @staticmethod
    def parse_energy_string(energy_str: str) -> Tuple[float, str]:
        """
        Parse une chaîne d'énergie comme '433 kcal / 1,812 kj' et extrait la valeur et l'unité.
        
        Args:
            energy_str: Chaîne contenant énergie avec unités
            
        Returns:
            Tuple (valeur, unité)
        """
        if pd.isna(energy_str):
            return np.nan, 'kJ'
        
        energy_str = str(energy_str).lower().replace(' ', '').replace(',', '.')
        
        # Chercher kcal en premier
        if 'kcal' in energy_str:
            # Extraire le nombre avant 'kcal'
            import re
            match = re.search(r'(\d+\.?\d*)\s*kcal', energy_str)
            if match:
                return float(match.group(1)), 'kcal'
        
        # Chercher kj
        if 'kj' in energy_str:
            import re
            match = re.search(r'(\d+\.?\d*)\s*kj', energy_str)
            if match:
                return float(match.group(1)), 'kJ'
        
        # Essayer de parser comme nombre pur
        try:
            return float(energy_str), 'kJ'  # Supposer kJ par défaut
        except ValueError:
            logger.warning(f"Impossible de parser l'énergie : {energy_str}")
            return np.nan, 'kJ'
    
    @staticmethod
    def parse_weight_string(weight_str: str, is_sodium: bool = False) -> float:
        """
        Parse une chaîne comme '3,4 g' ou '112mg' et extrait la valeur numérique.
        
        Args:
            weight_str: Chaîne avec poids et unité
            is_sodium: True si c'est du sodium (garder en mg)
            
        Returns:
            Valeur numérique extraite
        """
        if pd.isna(weight_str):
            return np.nan
        
        weight_str = str(weight_str).lower().replace(' ', '').replace(',', '.')
        
        # Extraire tous les nombres de la chaîne
        import re
        numbers = re.findall(r'(\d+\.?\d*)', weight_str)
        
        if numbers:
            value = float(numbers[0])
            
            # Gestion des unités
            if 'mg' in weight_str:
                if is_sodium:
                    # Garder en mg pour le sodium
                    return value
                else:
                    # Convertir mg -> g pour les autres
                    return value / 1000
            elif 'g' in weight_str and not 'mg' in weight_str:
                if is_sodium:
                    # Convertir g -> mg pour le sodium
                    return value * 1000
                else:
                    # Garder en g
                    return value
            else:
                # Pas d'unité détectée, supposer l'unité par défaut
                return value
        else:
            logger.warning(f"Impossible de parser le poids : {weight_str}")
            return np.nan
    
    @staticmethod
    def parse_percentage_string(percent_str: str) -> float:
        """
        Parse une chaîne de pourcentage comme '0.219 %' ou '0.16'.
        
        Args:
            percent_str: Chaîne avec pourcentage
            
        Returns:
            Valeur numérique (0-100)
        """
        if pd.isna(percent_str):
            return np.nan
        
        percent_str = str(percent_str).replace(' ', '').replace(',', '.')
        
        import re
        # Chercher un nombre avec ou sans %
        match = re.search(r'(\d+\.?\d*)', percent_str)
        
        if match:
            value = float(match.group(1))
            
            # Si la valeur est très petite (< 1) et pas de %, c'est probablement une fraction
            if value < 1 and '%' not in percent_str:
                value = value * 100
            
            return min(100, max(0, value))  # Clipper entre 0 et 100
        else:
            logger.warning(f"Impossible de parser le pourcentage : {percent_str}")
            return np.nan

    @staticmethod
    def detect_energy_unit(energy_series: pd.Series) -> str:
        """
        Détecte si les valeurs d'énergie sont en kJ ou kcal.
        
        Args:
            energy_series: Série des valeurs d'énergie
            
        Returns:
            'kJ' ou 'kcal'
        """
        # Supprimer les valeurs nulles pour l'analyse
        valid_values = energy_series.dropna()
        
        if len(valid_values) == 0:
            logger.warning("Aucune valeur d'énergie valide pour détecter l'unité")
            return 'kJ'  # Par défaut
        
        # Calculer la médiane pour éviter les outliers
        median_value = valid_values.median()
        
        # Heuristique : si la médiane < 1000, probablement en kcal
        # Sinon probablement en kJ
        if median_value < 1000:
            logger.info(f"Unité détectée : kcal (médiane = {median_value:.1f})")
            return 'kcal'
        else:
            logger.info(f"Unité détectée : kJ (médiane = {median_value:.1f})")
            return 'kJ'
    
    @staticmethod
    def kcal_to_kj(kcal_value: float) -> float:
        """
        Convertit kcal en kJ.
        
        Args:
            kcal_value: Valeur en kcal
            
        Returns:
            Valeur en kJ (1 kcal = 4.184 kJ)
        """
        if pd.isna(kcal_value):
            return np.nan
        return kcal_value * 4.184
    
    @staticmethod
    def salt_to_sodium(salt_g: float) -> float:
        """
        Convertit sel (g) en sodium (mg).
        
        Args:
            salt_g: Valeur de sel en grammes
            
        Returns:
            Valeur de sodium en mg (sel_g × 400)
        """
        if pd.isna(salt_g):
            return np.nan
        return salt_g * 400
    
    @staticmethod
    def normalize_energy(df: pd.DataFrame, 
                        energy_col: str = 'energy_100g',
                        force_unit: Optional[str] = None) -> pd.DataFrame:
        """
        Normalise les valeurs d'énergie en kJ.
        
        Args:
            df: DataFrame à normaliser
            energy_col: Nom de la colonne énergie
            force_unit: Force une unité spécifique ('kJ' ou 'kcal')
            
        Returns:
            DataFrame avec énergie normalisée en kJ
        """
        df = df.copy()
        
        if energy_col not in df.columns:
            logger.warning(f"Colonne {energy_col} non trouvée")
            return df
        
        # Parser les chaînes d'énergie
        logger.info(f"Parsing des valeurs d'énergie dans {energy_col}")
        
        def parse_and_convert_energy(energy_str):
            value, unit = DataNormalizer.parse_energy_string(energy_str)
            if pd.isna(value):
                return np.nan
            
            # Convertir en kJ si nécessaire
            if unit == 'kcal':
                return DataNormalizer.kcal_to_kj(value)
            else:
                return value
        
        df[energy_col] = df[energy_col].apply(parse_and_convert_energy)
        
        logger.info(f"Énergie normalisée en kJ pour {energy_col}")
        return df
    
    @staticmethod
    def normalize_sodium(df: pd.DataFrame,
                        sodium_col: str = 'sodium_100g',
                        salt_col: Optional[str] = 'salt_100g') -> pd.DataFrame:
        """
        Normalise les valeurs de sodium/sel.
        
        Args:
            df: DataFrame à normaliser
            sodium_col: Nom de la colonne sodium
            salt_col: Nom de la colonne sel (optionnel)
            
        Returns:
            DataFrame avec sodium normalisé en mg
        """
        df = df.copy()
        
        # Si pas de colonne sodium mais colonne sel disponible
        if sodium_col not in df.columns and salt_col and salt_col in df.columns:
            logger.info(f"Conversion sel -> sodium : {salt_col} -> {sodium_col}")
            df[sodium_col] = df[salt_col].apply(DataNormalizer.salt_to_sodium)
        elif sodium_col in df.columns:
            # Vérifier si les valeurs sont probablement en grammes (très petites)
            valid_sodium = df[sodium_col].dropna()
            if len(valid_sodium) > 0:
                median_sodium = valid_sodium.median()
                if median_sodium < 10:  # Probablement en grammes
                    logger.info(f"Conversion sel(g) -> sodium(mg) pour {sodium_col}")
                    df[sodium_col] = df[sodium_col].apply(DataNormalizer.salt_to_sodium)
        
        return df
    
    @staticmethod
    def clean_percentage_values(df: pd.DataFrame, 
                              percent_col: str = 'fruits_veg_nuts_percent') -> pd.DataFrame:
        """
        Nettoie les valeurs de pourcentage (0-100).
        
        Args:
            df: DataFrame à nettoyer
            percent_col: Nom de la colonne pourcentage
            
        Returns:
            DataFrame avec pourcentages nettoyés
        """
        df = df.copy()
        
        if percent_col not in df.columns:
            logger.warning(f"Colonne {percent_col} non trouvée")
            return df
        
        original_count = len(df)
        
        # Clipper les valeurs entre 0 et 100
        df[percent_col] = df[percent_col].clip(0, 100)
        
        # Compter les modifications
        out_of_range_count = len(df) - original_count
        if out_of_range_count > 0:
            logger.info(f"Valeurs de pourcentage ajustées : {out_of_range_count}")
        
        return df
    
    @staticmethod
    def clean_negative_values(df: pd.DataFrame, 
                            numeric_columns: list = None) -> pd.DataFrame:
        """
        Nettoie les valeurs négatives en les mettant à 0 ou NaN.
        
        Args:
            df: DataFrame à nettoyer
            numeric_columns: Liste des colonnes à nettoyer (par défaut toutes les nutritionnelles)
            
        Returns:
            DataFrame avec valeurs négatives nettoyées
        """
        df = df.copy()
        
        if numeric_columns is None:
            numeric_columns = [
                'energy_100g', 'saturated_fat_100g', 'sugars_100g', 
                'sodium_100g', 'proteins_100g', 'fiber_100g',
                'fruits_veg_nuts_percent'
            ]
        
        negative_counts = {}
        
        for col in numeric_columns:
            if col in df.columns:
                # Compter les valeurs négatives
                negative_mask = df[col] < 0
                negative_count = negative_mask.sum()
                
                if negative_count > 0:
                    negative_counts[col] = negative_count
                    # Remplacer par 0 (ou NaN selon préférence)
                    df.loc[negative_mask, col] = 0
                    logger.warning(f"Valeurs négatives dans {col} remplacées par 0 : {negative_count}")
        
        if negative_counts:
            total_negative = sum(negative_counts.values())
            logger.info(f"Total valeurs négatives nettoyées : {total_negative}")
        
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, 
                             strategy: str = 'drop_row',
                             threshold: float = 0.7) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Gère les valeurs manquantes selon différentes stratégies.
        
        Args:
            df: DataFrame à traiter
            strategy: 'drop_row', 'drop_column', 'fill_zero', 'fill_median'
            threshold: Seuil pour drop_column (proportion de valeurs non-nulles requises)
            
        Returns:
            Tuple (DataFrame traité, statistiques des suppressions)
        """
        df = df.copy()
        original_rows = len(df)
        stats = {'dropped_rows': 0, 'dropped_columns': 0, 'filled_values': 0}
        
        # Colonnes critiques pour le Nutri-Score
        critical_columns = [
            'energy_100g', 'saturated_fat_100g', 'sugars_100g', 
            'sodium_100g', 'proteins_100g', 'fiber_100g'
        ]
        
        if strategy == 'drop_row':
            # Supprimer les lignes avec des valeurs manquantes dans les colonnes critiques
            available_critical = [col for col in critical_columns if col in df.columns]
            df_clean = df.dropna(subset=available_critical)
            stats['dropped_rows'] = original_rows - len(df_clean)
            df = df_clean
            
        elif strategy == 'drop_column':
            # Supprimer les colonnes avec trop de valeurs manquantes
            for col in df.columns:
                non_null_ratio = df[col].count() / len(df)
                if non_null_ratio < threshold and col not in critical_columns:
                    df = df.drop(columns=[col])
                    stats['dropped_columns'] += 1
                    
        elif strategy == 'fill_zero':
            # Remplir avec 0
            for col in critical_columns:
                if col in df.columns:
                    missing_count = df[col].isnull().sum()
                    if missing_count > 0:
                        df[col] = df[col].fillna(0)
                        stats['filled_values'] += missing_count
                        
        elif strategy == 'fill_median':
            # Remplir avec la médiane
            for col in critical_columns:
                if col in df.columns:
                    missing_count = df[col].isnull().sum()
                    if missing_count > 0:
                        median_val = df[col].median()
                        df[col] = df[col].fillna(median_val)
                        stats['filled_values'] += missing_count
        
        # Log des résultats
        if stats['dropped_rows'] > 0:
            logger.info(f"Lignes supprimées pour valeurs manquantes : {stats['dropped_rows']}")
        if stats['dropped_columns'] > 0:
            logger.info(f"Colonnes supprimées pour valeurs manquantes : {stats['dropped_columns']}")
        if stats['filled_values'] > 0:
            logger.info(f"Valeurs manquantes remplies : {stats['filled_values']}")
        
        return df, stats
    
    @staticmethod
    def parse_all_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse toutes les colonnes numériques pour extraire les valeurs des chaînes.
        
        Args:
            df: DataFrame à parser
            
        Returns:
            DataFrame avec colonnes parsées
        """
        df_parsed = df.copy()
        
        # Colonnes à parser selon leur type
        numeric_columns = {
            'energy_100g': 'energy',
            'saturated_fat_100g': 'weight',
            'sugars_100g': 'weight', 
            'sodium_100g': 'weight',
            'proteins_100g': 'weight',
            'fiber_100g': 'weight',
            'fruits_veg_nuts_percent': 'percentage'
        }
        
        for col, parse_type in numeric_columns.items():
            if col in df_parsed.columns:
                logger.info(f"Parsing colonne {col} comme {parse_type}")
                
                if parse_type == 'energy':
                    # Déjà géré par normalize_energy
                    continue
                elif parse_type == 'weight':
                    is_sodium = (col == 'sodium_100g')
                    df_parsed[col] = df_parsed[col].apply(lambda x: DataNormalizer.parse_weight_string(x, is_sodium))
                elif parse_type == 'percentage':
                    df_parsed[col] = df_parsed[col].apply(DataNormalizer.parse_percentage_string)
                
                # Compter les valeurs réussies
                valid_count = df_parsed[col].notna().sum()
                logger.info(f"  -> {valid_count}/{len(df_parsed)} valeurs parsées avec succès")
        
        return df_parsed
    
    @staticmethod
    def full_normalization(df: pd.DataFrame, 
                          energy_unit: Optional[str] = None,
                          missing_strategy: str = 'drop_row') -> Tuple[pd.DataFrame, Dict[str, any]]:
        """
        Applique toutes les normalisations nécessaires.
        
        Args:
            df: DataFrame à normaliser
            energy_unit: Unité d'énergie forcée (None pour auto-détection)
            missing_strategy: Stratégie pour les valeurs manquantes
            
        Returns:
            Tuple (DataFrame normalisé, rapport de normalisation)
        """
        logger.info("Début de la normalisation complète des données")
        
        df_normalized = df.copy()
        report = {
            'original_rows': len(df),
            'steps_applied': [],
            'final_rows': 0,
            'issues_found': {}
        }
        
        # 0. Parsing des colonnes avec chaînes
        try:
            df_normalized = DataNormalizer.parse_all_numeric_columns(df_normalized)
            report['steps_applied'].append('string_parsing')
        except Exception as e:
            logger.error(f"Erreur parsing chaînes : {e}")
            report['issues_found']['parsing'] = str(e)
        
        # 1. Normalisation de l'énergie
        try:
            df_normalized = DataNormalizer.normalize_energy(df_normalized, force_unit=energy_unit)
            report['steps_applied'].append('energy_normalization')
        except Exception as e:
            logger.error(f"Erreur normalisation énergie : {e}")
            report['issues_found']['energy'] = str(e)
        
        # 2. Normalisation du sodium (pas besoin, déjà fait dans parsing)
        # Garder pour compatibilité mais sodium déjà converti en mg dans parse_weight_string
        report['steps_applied'].append('sodium_normalization_skipped')
        
        # 3. Nettoyage des pourcentages (déjà fait dans parsing)
        report['steps_applied'].append('percentage_cleaning_during_parsing')
        
        # 4. Nettoyage des valeurs négatives
        try:
            df_normalized = DataNormalizer.clean_negative_values(df_normalized)
            report['steps_applied'].append('negative_values_cleaning')
        except Exception as e:
            logger.error(f"Erreur nettoyage valeurs négatives : {e}")
            report['issues_found']['negative_values'] = str(e)
        
        # 5. Gestion des valeurs manquantes
        try:
            df_normalized, missing_stats = DataNormalizer.handle_missing_values(
                df_normalized, strategy=missing_strategy
            )
            report['steps_applied'].append('missing_values_handling')
            report['missing_stats'] = missing_stats
        except Exception as e:
            logger.error(f"Erreur gestion valeurs manquantes : {e}")
            report['issues_found']['missing_values'] = str(e)
        
        report['final_rows'] = len(df_normalized)
        report['rows_removed'] = report['original_rows'] - report['final_rows']
        
        logger.info(f"Normalisation terminée : {report['original_rows']} -> {report['final_rows']} lignes")
        
        return df_normalized, report


def normalize_data(df: pd.DataFrame, 
                  energy_unit: Optional[str] = None,
                  missing_strategy: str = 'drop_row') -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Fonction utilitaire pour normaliser les données.
    
    Args:
        df: DataFrame à normaliser
        energy_unit: Unité d'énergie forcée
        missing_strategy: Stratégie pour les valeurs manquantes
        
    Returns:
        Tuple (DataFrame normalisé, rapport)
    """
    return DataNormalizer.full_normalization(df, energy_unit, missing_strategy)


if __name__ == "__main__":
    # Test du module
    import sys
    sys.path.append('.')
    from app.io import load_data
    
    try:
        # Charger les données
        df, _, _ = load_data()
        print(f"Données chargées : {len(df)} lignes")
        
        # Normaliser
        df_norm, report = normalize_data(df)
        print(f"Données normalisées : {len(df_norm)} lignes")
        print(f"Étapes appliquées : {report['steps_applied']}")
        
        if report['issues_found']:
            print(f"Problèmes trouvés : {report['issues_found']}")
            
    except Exception as e:
        print(f"Erreur de test : {e}")