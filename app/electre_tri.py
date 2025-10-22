"""
Module d'implémentation ELECTRE TRI pour le classement des produits alimentaires.
Implémente les variantes pessimiste et optimiste avec profils limites.
"""

import pandas as pd
import numpy as np
import yaml
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configuration du logging
logger = logging.getLogger(__name__)

class ElectreTri:
    """Classe d'implémentation ELECTRE TRI-B avec profils limites."""
    
    def __init__(self, config_path: str = "config/electre.yml"):
        """
        Initialise ELECTRE TRI avec les paramètres de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration ELECTRE
        """
        self.config_path = Path(config_path)
        self.params = self._load_config()
        self._validate_config()
        self._normalize_weights()
        
    def _load_config(self) -> Dict:
        """Charge la configuration ELECTRE depuis le fichier YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration ELECTRE chargée depuis {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Fichier de configuration ELECTRE non trouvé : {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erreur de parsing YAML : {e}")
            raise
    
    def _validate_config(self):
        """Valide la cohérence de la configuration."""
        required_sections = ['weights', 'directions', 'profiles', 'lambda']
        
        for section in required_sections:
            if section not in self.params:
                raise ValueError(f"Section manquante dans la config ELECTRE : {section}")
        
        # Vérifier que les critères sont cohérents
        criteria = set(self.params['weights'].keys())
        
        for section in ['directions', 'profiles']:
            if section == 'profiles':
                # Pour les profils, vérifier chaque profil limite
                for profile_name, profile_values in self.params['profiles'].items():
                    profile_criteria = set(profile_values.keys())
                    if not criteria.issubset(profile_criteria):
                        missing = criteria - profile_criteria
                        logger.warning(f"Critères manquants dans profil {profile_name} : {missing}")
            else:
                section_criteria = set(self.params[section].keys())
                if not criteria.issubset(section_criteria):
                    missing = criteria - section_criteria
                    logger.warning(f"Critères manquants dans section {section} : {missing}")
        
        # Vérifier lambda
        lambda_val = self.params['lambda']
        if not (0 < lambda_val <= 1):
            raise ValueError(f"Lambda doit être entre 0 et 1, reçu : {lambda_val}")
    
    def _normalize_weights(self):
        """Normalise les poids pour qu'ils somment à 1."""
        weights = self.params['weights']
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            raise ValueError("La somme des poids ne peut pas être nulle")
        
        # Normaliser
        for criterion in weights:
            weights[criterion] = weights[criterion] / total_weight
        
        logger.info(f"Poids normalisés : {weights}")
    
    def _compute_concordance_index(self, 
                                  alternative: Dict[str, float], 
                                  profile: Dict[str, float], 
                                  criterion: str) -> float:
        """
        Calcule l'indice de concordance partielle pour un critère (version simplifiée binaire).
        
        Args:
            alternative: Valeurs de l'alternative
            profile: Valeurs du profil limite
            criterion: Nom du critère
            
        Returns:
            Indice de concordance binaire (0 ou 1)
        """
        if criterion not in alternative or criterion not in profile:
            logger.warning(f"Critère {criterion} manquant")
            return 0.0
        
        alt_val = alternative[criterion]
        prof_val = profile[criterion]
        direction = self.params['directions'][criterion]
        
        # Valeurs manquantes
        if pd.isna(alt_val) or pd.isna(prof_val):
            return 0.0
        
        # Logique binaire simplifiée (sans seuils)
        if direction == 1:  # Critère à maximiser (bénéfice)
            return 1.0 if alt_val >= prof_val else 0.0
        else:  # Critère à minimiser (coût)
            return 1.0 if alt_val <= prof_val else 0.0

    def _compute_global_concordance(self, 
                                   alternative: Dict[str, float], 
                                   profile: Dict[str, float]) -> float:
        """
        Calcule l'indice de concordance global de la relation S(a,b).
        
        Args:
            alternative: Valeurs de l'alternative
            profile: Valeurs du profil limite
            
        Returns:
            Indice de concordance global (0 à 1)
        """
        criteria = list(self.params['weights'].keys())
        
        # Calcul de l'indice de concordance globale (somme pondérée)
        concordance_sum = 0.0
        total_weight = 0.0
        
        for criterion in criteria:
            if criterion in alternative and criterion in profile:
                weight = self.params['weights'][criterion]
                concordance = self._compute_concordance_index(alternative, profile, criterion)
                concordance_sum += weight * concordance
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return concordance_sum / total_weight
    
    def _outrank_relation(self, 
                         alternative: Dict[str, float], 
                         profile: Dict[str, float]) -> bool:
        """
        Détermine s'il y a surclassement entre alternative et profil.
        
        Args:
            alternative: Valeurs de l'alternative  
            profile: Valeurs du profil limite
            
        Returns:
            True si surclassement (S(a,b))
        """
        concordance = self._compute_global_concordance(alternative, profile)
        lambda_threshold = self.params['lambda']
        
        return concordance >= lambda_threshold
    
    def _classify_pessimistic(self, alternative: Dict[str, float]) -> str:
        """
        Classification pessimiste : compare a aux profils dans l'ordre décroissant.
        
        Args:
            alternative: Valeurs de l'alternative à classer
            
        Returns:
            Classe assignée (A', B', C', D', E')
        """
        profiles = self.params['profiles']
        # Profils triés par ordre décroissant (du meilleur au pire), excluant b1
        # Supposant que b4 > b3 > b2 > b1 (b4 = meilleur, b1 = pire)
        profile_names_desc = [name for name in sorted(profiles.keys(), reverse=True) if name != 'b1']
        
        # Classes correspondantes selon la logique ELECTRE TRI
        # Si H S bk, alors H appartient à la classe Ck+1
        classes = ['A\'', 'B\'', 'C\'', 'D\'', 'E\'']
        
        for i, profile_name in enumerate(profile_names_desc):
            profile = profiles[profile_name]
            
            # Test si a surclasse le profil b_i
            if self._outrank_relation(alternative, profile):
                # a surclasse b_i, donc a appartient à la classe correspondante
                return classes[i]
        
        # a ne surclasse aucun profil, donc classe la plus basse
        return 'E\''
    
    def _classify_optimistic(self, alternative: Dict[str, float]) -> str:
        """
        Classification optimiste : compare les profils à a dans l'ordre croissant.
        
        Args:
            alternative: Valeurs de l'alternative à classer
            
        Returns:
            Classe assignée (A', B', C', D', E')
        """
        profiles = self.params['profiles']
        # Profils triés par ordre croissant (du pire au meilleur), excluant b1
        # b2, b3, b4 (on ignore b1 car c'est la borne inférieure)
        profile_names_asc = [name for name in sorted(profiles.keys()) if name != 'b1']
        
        # Classes correspondantes selon la logique ELECTRE TRI optimiste
        # Si bk S H, alors H appartient à la classe Ck-1
        classes = ['E\'', 'D\'', 'C\'', 'B\'', 'A\'']
        
        for i, profile_name in enumerate(profile_names_asc):
            profile = profiles[profile_name]
            
            # Test si le profil b_i surclasse a
            if self._outrank_relation(profile, alternative):
                # b_i surclasse a, donc a appartient à la classe correspondante
                return classes[i]
        
        # Aucun profil ne surclasse a, donc classe la plus haute
        return 'A\''
    
    def classify_alternative(self, 
                           alternative: Dict[str, float], 
                           variant: str = "pessimistic") -> str:
        """
        Classe une alternative selon ELECTRE TRI.
        
        Args:
            alternative: Dictionnaire {critère: valeur}
            variant: "pessimistic" ou "optimistic"
            
        Returns:
            Classe assignée (A', B', C', D', E')
        """
        if variant == "pessimistic":
            return self._classify_pessimistic(alternative)
        elif variant == "optimistic":
            return self._classify_optimistic(alternative)
        else:
            raise ValueError(f"Variante inconnue : {variant}. Utiliser 'pessimistic' ou 'optimistic'")
    
    def classify_dataframe_row(self, 
                             row: pd.Series, 
                             variant: str = "pessimistic") -> str:
        """
        Classe une ligne de DataFrame.
        
        Args:
            row: Ligne du DataFrame
            variant: Variante ELECTRE TRI
            
        Returns:
            Classe assignée
        """
        # Extraire les valeurs des critères
        alternative = {}
        criteria = list(self.params['weights'].keys())
        
        for criterion in criteria:
            if criterion in row.index:
                value = row[criterion]
                # Ignorer les valeurs manquantes (ou les traiter selon stratégie)
                if not pd.isna(value):
                    alternative[criterion] = float(value)
                else:
                    # Stratégie pour valeurs manquantes : valeur neutre ou ignorer
                    logger.debug(f"Valeur manquante pour critère {criterion}")
                    alternative[criterion] = 0.0  # Ou une autre stratégie
        
        if not alternative:
            logger.warning("Aucun critère valide pour la classification")
            return 'N/A'
        
        try:
            return self.classify_alternative(alternative, variant)
        except Exception as e:
            logger.error(f"Erreur classification : {e}")
            return 'ERROR'


def electre_sorting(df: pd.DataFrame, 
                   config_path: str = "config/electre.yml",
                   variant: str = "pessimistic") -> pd.Series:
    """
    Applique ELECTRE TRI à un DataFrame entier.
    
    Args:
        df: DataFrame avec les données
        config_path: Chemin vers la configuration ELECTRE
        variant: "pessimistic" ou "optimistic"
        
    Returns:
        Série avec les classes assignées
    """
    logger.info(f"Application ELECTRE TRI ({variant}) à {len(df)} alternatives")
    
    # Initialiser ELECTRE TRI
    electre = ElectreTri(config_path)
    
    # Appliquer la classification
    classifications = df.apply(
        lambda row: electre.classify_dataframe_row(row, variant), 
        axis=1
    )
    
    # Statistiques
    class_distribution = classifications.value_counts()
    logger.info(f"Distribution des classes ELECTRE TRI :")
    for class_name, count in class_distribution.items():
        logger.info(f"  {class_name}: {count} produits")
    
    return classifications


def classify_single_product(criteria_values: Dict[str, float],
                          config_path: str = "config/electre.yml", 
                          variant: str = "pessimistic") -> Dict[str, any]:
    """
    Classe un produit individuel avec ELECTRE TRI.
    
    Args:
        criteria_values: Dictionnaire {critère: valeur}
        config_path: Chemin vers la configuration
        variant: Variante ELECTRE TRI
        
    Returns:
        Dictionnaire avec classe et détails
    """
    electre = ElectreTri(config_path)
    
    try:
        assigned_class = electre.classify_alternative(criteria_values, variant)
        
        # Calculer les concordances globales pour information
        profiles = electre.params['profiles']
        concordances = {}
        
        for profile_name, profile_values in profiles.items():
            conc = electre._compute_global_concordance(criteria_values, profile_values)
            concordances[f"S(a,{profile_name})"] = round(conc, 3)
        
        return {
            'class': assigned_class,
            'variant': variant,
            'concordances': concordances,
            'lambda': electre.params['lambda']
        }
        
    except Exception as e:
        logger.error(f"Erreur classification individuelle : {e}")
        return {
            'class': 'ERROR',
            'error': str(e)
        }


if __name__ == "__main__":
    # Tests du module ELECTRE TRI
    print("=== Test ELECTRE TRI ===")
    
    # Test avec produit exemple
    test_product = {
        'energy_100g': 1500,  # kJ
        'saturated_fat_100g': 3.0,  # g
        'sugars_100g': 12.0,  # g
        'sodium_100g': 200,  # mg
        'proteins_100g': 8.0,  # g
        'fiber_100g': 2.5,  # g
        'fruits_veg_nuts_percent': 30,  # %
        'additives_count': 2
    }
    
    print("Produit test :", test_product)
    
    try:
        # Test pessimiste
        result_pess = classify_single_product(test_product, variant="pessimistic")
        print(f"\nClassification pessimiste : {result_pess['class']}")
        print(f"Concordances : {result_pess['concordances']}")
        
        # Test optimiste
        result_opt = classify_single_product(test_product, variant="optimistic")
        print(f"\nClassification optimiste : {result_opt['class']}")
        
    except Exception as e:
        print(f"Erreur de test : {e}")
    
    print("\nTests ELECTRE TRI terminés !")