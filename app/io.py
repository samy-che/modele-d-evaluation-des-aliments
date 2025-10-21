"""
Module de lecture et de gestion des données Excel avec mapping des colonnes.
"""

import pandas as pd
import yaml
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelDataLoader:
    """Classe pour charger et mapper les données Excel selon la configuration."""
    
    def __init__(self, config_path: str = "config/columns.yml"):
        """
        Initialise le loader avec le fichier de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration YAML
        """
        self.config_path = Path(config_path)
        self.column_mapping = self._load_column_config()
    
    def _load_column_config(self) -> Dict[str, List[str]]:
        """Charge la configuration de mapping des colonnes."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration de colonnes chargée depuis {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Fichier de configuration non trouvé : {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erreur de parsing YAML : {e}")
            raise
    
    def _find_column_match(self, df_columns: List[str], target_column: str) -> Optional[str]:
        """
        Trouve la correspondance d'une colonne cible dans les colonnes du DataFrame.
        
        Args:
            df_columns: Liste des colonnes du DataFrame
            target_column: Nom de la colonne cible à chercher
            
        Returns:
            Nom de la colonne trouvée ou None
        """
        possible_names = self.column_mapping.get(target_column, [target_column])
        
        # Recherche exacte d'abord
        for col_name in possible_names:
            if col_name in df_columns:
                return col_name
        
        # Recherche insensible à la casse
        df_columns_lower = [col.lower() for col in df_columns]
        for col_name in possible_names:
            col_lower = col_name.lower()
            if col_lower in df_columns_lower:
                idx = df_columns_lower.index(col_lower)
                return df_columns[idx]
        
        return None
    
    def load_excel_data(self, 
                       excel_path: str, 
                       sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Charge les données Excel et applique le mapping des colonnes.
        
        Args:
            excel_path: Chemin vers le fichier Excel
            sheet_name: Nom de la feuille (None pour la première)
            
        Returns:
            Tuple (DataFrame avec colonnes mappées, dictionnaire de mapping appliqué)
        """
        try:
            # Lecture du fichier Excel
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_path)
            
            logger.info(f"Données chargées : {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Application du mapping
            mapped_df, mapping_info = self._apply_column_mapping(df)
            
            return mapped_df, mapping_info
            
        except FileNotFoundError:
            logger.error(f"Fichier Excel non trouvé : {excel_path}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement d'Excel : {e}")
            raise
    
    def _apply_column_mapping(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Applique le mapping des colonnes au DataFrame.
        
        Args:
            df: DataFrame original
            
        Returns:
            Tuple (DataFrame mappé, dictionnaire de mapping appliqué)
        """
        mapped_df = df.copy()
        mapping_info = {}
        missing_columns = []
        
        # Colonnes requises pour le calcul Nutri-Score
        required_columns = [
            'product_name', 'energy_100g', 'saturated_fat_100g', 
            'sugars_100g', 'sodium_100g', 'proteins_100g', 
            'fiber_100g', 'fruits_veg_nuts_percent'
        ]
        
        # Colonnes optionnelles
        optional_columns = ['nutriscore_label', 'nutriscore_score', 'additives_count']
        
        all_columns = required_columns + optional_columns
        
        for target_col in all_columns:
            found_col = self._find_column_match(df.columns.tolist(), target_col)
            
            if found_col:
                if found_col != target_col:
                    # Renommer la colonne
                    mapped_df = mapped_df.rename(columns={found_col: target_col})
                    mapping_info[target_col] = found_col
                    logger.info(f"Colonne mappée : '{found_col}' -> '{target_col}'")
                else:
                    mapping_info[target_col] = found_col
            else:
                if target_col in required_columns:
                    missing_columns.append(target_col)
                    logger.warning(f"Colonne requise manquante : {target_col}")
                else:
                    logger.info(f"Colonne optionnelle manquante : {target_col}")
        
        if missing_columns:
            logger.error(f"Colonnes requises manquantes : {missing_columns}")
            raise ValueError(f"Colonnes manquantes dans le dataset : {missing_columns}")
        
        # Garder seulement les colonnes mappées (les noms canoniques)
        columns_to_keep = list(mapping_info.keys())
        if 'id' in mapped_df.columns:
            columns_to_keep.append('id')
        
        # Filtrer pour ne garder que les colonnes qui existent réellement
        available_columns = [col for col in columns_to_keep if col in mapped_df.columns]
        
        # Ajouter quelques colonnes supplémentaires si disponibles
        extra_cols = [col for col in mapped_df.columns if col not in available_columns]
        if extra_cols:
            logger.info(f"Colonnes supplémentaires disponibles : {len(extra_cols)}")
            # Garder les colonnes supplémentaires qui pourraient être utiles
            available_columns.extend(extra_cols[:5])  # Limiter à 5 colonnes supplémentaires
        
        mapped_df = mapped_df[available_columns]
        
        return mapped_df, mapping_info
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Valide la qualité des données et retourne un rapport.
        
        Args:
            df: DataFrame à valider
            
        Returns:
            Dictionnaire avec les statistiques de qualité
        """
        report = {
            'total_rows': len(df),
            'missing_values': {},
            'invalid_values': {},
            'data_ranges': {}
        }
        
        # Colonnes nutritionnelles à vérifier
        numeric_columns = [
            'energy_100g', 'saturated_fat_100g', 'sugars_100g', 
            'sodium_100g', 'proteins_100g', 'fiber_100g'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Valeurs manquantes
                missing_count = df[col].isnull().sum()
                report['missing_values'][col] = missing_count
                
                # Valeurs négatives (invalides)
                if pd.api.types.is_numeric_dtype(df[col]):
                    negative_count = (df[col] < 0).sum()
                    report['invalid_values'][col] = negative_count
                    
                    # Plages de données
                    valid_data = df[col].dropna()
                    if len(valid_data) > 0:
                        report['data_ranges'][col] = {
                            'min': float(valid_data.min()),
                            'max': float(valid_data.max()),
                            'mean': float(valid_data.mean()),
                            'median': float(valid_data.median())
                        }
        
        # Vérification spéciale pour fruits_veg_nuts_percent (0-100)
        if 'fruits_veg_nuts_percent' in df.columns:
            col = 'fruits_veg_nuts_percent'
            missing_count = df[col].isnull().sum()
            report['missing_values'][col] = missing_count
            
            if pd.api.types.is_numeric_dtype(df[col]):
                out_of_range = ((df[col] < 0) | (df[col] > 100)).sum()
                report['invalid_values'][col] = out_of_range
        
        return report


def load_data(excel_path: str = "data/produits.xlsx", 
              config_path: str = "config/columns.yml") -> Tuple[pd.DataFrame, Dict[str, str], Dict[str, any]]:
    """
    Fonction utilitaire pour charger les données avec validation.
    
    Args:
        excel_path: Chemin vers le fichier Excel
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Tuple (DataFrame, mapping_info, quality_report)
    """
    loader = ExcelDataLoader(config_path)
    df, mapping_info = loader.load_excel_data(excel_path)
    quality_report = loader.validate_data_quality(df)
    
    # Log du rapport de qualité
    logger.info(f"Rapport de qualité des données :")
    logger.info(f"  - Lignes totales : {quality_report['total_rows']}")
    
    for col, missing in quality_report['missing_values'].items():
        if missing > 0:
            logger.warning(f"  - {col} : {missing} valeurs manquantes")
    
    for col, invalid in quality_report['invalid_values'].items():
        if invalid > 0:
            logger.warning(f"  - {col} : {invalid} valeurs invalides")
    
    return df, mapping_info, quality_report


if __name__ == "__main__":
    # Test du module
    try:
        df, mapping, quality = load_data()
        print(f"Données chargées avec succès : {len(df)} lignes")
        print(f"Colonnes mappées : {list(mapping.keys())}")
        print(f"Premières lignes :\n{df.head()}")
    except Exception as e:
        print(f"Erreur : {e}")