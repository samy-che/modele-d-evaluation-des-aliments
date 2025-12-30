"""
Module d'implémentation ELECTRE TRI pour le classement des produits alimentaires.
Implémente les variantes pessimiste et optimiste avec profils limites.
"""

# Import des bibliothèques nécessaires
import pandas as pd  # Pour manipuler les données sous forme de DataFrames
import numpy as np   # Pour les calculs numériques et la gestion des valeurs NaN
import yaml         # Pour lire les fichiers de configuration YAML
import logging      # Pour enregistrer les logs et messages de débogage
from typing import Dict, List, Tuple, Optional  # Pour les annotations de types
from pathlib import Path  # Pour gérer les chemins de fichiers de manière portable
from app.utils.paths import get_config_path

# Configuration du système de logging pour tracer l'exécution
logger = logging.getLogger(__name__)  # Créer un logger spécifique à ce module

class ElectreTri:
    """Classe d'implémentation ELECTRE TRI-B avec profils limites."""
    
    def __init__(self, config_path: str = None):
        """
        Initialise ELECTRE TRI avec les paramètres de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration ELECTRE
        """
        # Convertir le chemin en objet Path pour une manipulation sûre
        self.config_path = Path(config_path or get_config_path("config/electre.yml"))
        # Charger les paramètres depuis le fichier de configuration
        self.params = self._load_config()
        # Valider que tous les paramètres requis sont présents et cohérents
        self._validate_config()
        # Normaliser les poids pour qu'ils somment à 1
        self._normalize_weights()
        
    def _load_config(self) -> Dict:
        """Charge la configuration ELECTRE depuis le fichier YAML."""
        try:
            # Ouvrir le fichier de configuration en mode lecture avec encodage UTF-8
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # Parser le contenu YAML et le convertir en dictionnaire Python
                config = yaml.safe_load(f)
            # Enregistrer un message de succès dans les logs
            logger.info(f"Configuration ELECTRE chargée depuis {self.config_path}")
            # Retourner la configuration chargée
            return config
        except FileNotFoundError:
            # Gérer le cas où le fichier de configuration n'existe pas
            logger.error(f"Fichier de configuration ELECTRE non trouvé : {self.config_path}")
            raise  # Relancer l'exception pour arrêter l'exécution
        except yaml.YAMLError as e:
            # Gérer les erreurs de syntaxe dans le fichier YAML
            logger.error(f"Erreur de parsing YAML : {e}")
            raise  # Relancer l'exception
    
    def _validate_config(self):
        """Valide la cohérence de la configuration."""
        # Liste des sections obligatoires dans la configuration ELECTRE
        required_sections = ['weights', 'directions', 'profiles', 'lambda']
        
        # Vérifier que toutes les sections requises sont présentes
        for section in required_sections:
            if section not in self.params:
                # Lever une exception si une section obligatoire manque
                raise ValueError(f"Section manquante dans la config ELECTRE : {section}")
        
        # Extraire l'ensemble des critères définis dans les poids
        criteria = set(self.params['weights'].keys())
        
        # Vérifier la cohérence des critères dans les autres sections
        for section in ['directions', 'profiles']:
            if section == 'profiles':
                # Pour les profils, vérifier chaque profil limite individuellement
                for profile_name, profile_values in self.params['profiles'].items():
                    # Obtenir les critères définis pour ce profil
                    profile_criteria = set(profile_values.keys())
                    # Vérifier que tous les critères des poids sont présents dans le profil
                    if not criteria.issubset(profile_criteria):
                        # Calculer les critères manquants
                        missing = criteria - profile_criteria
                        # Avertir mais ne pas arrêter (profil potentiellement incomplet)
                        logger.warning(f"Critères manquants dans profil {profile_name} : {missing}")
            else:
                # Pour les autres sections (directions), vérifier directement
                section_criteria = set(self.params[section].keys())
                if not criteria.issubset(section_criteria):
                    # Calculer les critères manquants
                    missing = criteria - section_criteria
                    # Avertir des critères manquants
                    logger.warning(f"Critères manquants dans section {section} : {missing}")
        
        # Valider le paramètre lambda (seuil de concordance)
        lambda_val = self.params['lambda']
        # Lambda doit être strictement positif et au maximum 1
        if not (0 < lambda_val <= 1):
            raise ValueError(f"Lambda doit être entre 0 et 1, reçu : {lambda_val}")
    
    def _normalize_weights(self):
        """Normalise les poids pour qu'ils somment à 1."""
        # Obtenir la référence vers les poids dans la configuration
        weights = self.params['weights']
        # Calculer la somme totale de tous les poids
        total_weight = sum(weights.values())
        
        # Vérifier que la somme n'est pas nulle (éviter division par zéro)
        if total_weight == 0:
            raise ValueError("La somme des poids ne peut pas être nulle")
        
        # Normaliser chaque poids en le divisant par la somme totale
        for criterion in weights:
            # Diviser chaque poids par la somme pour que le total soit 1
            weights[criterion] = weights[criterion] / total_weight
        
        # Enregistrer les poids normalisés dans les logs pour traçabilité
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
        # Vérifier que le critère existe dans l'alternative ET le profil
        if criterion not in alternative or criterion not in profile:
            # Avertir si le critère est manquant et retourner concordance nulle
            logger.warning(f"Critère {criterion} manquant")
            return 0.0
        
        # Extraire les valeurs du critère pour l'alternative et le profil
        alt_val = alternative[criterion]
        prof_val = profile[criterion]
        # Récupérer la direction du critère (1=maximiser, autre=minimiser)
        direction = self.params['directions'][criterion]
        
        # Gérer les valeurs manquantes (NaN) en retournant concordance nulle
        if pd.isna(alt_val) or pd.isna(prof_val):
            return 0.0
        
        # Appliquer la logique binaire simplifiée selon la direction du critère
        if direction == 1:  # Critère à maximiser (bénéfice) - plus c'est grand, mieux c'est
            # L'alternative domine si sa valeur >= valeur du profil
            return 1.0 if alt_val >= prof_val else 0.0
        else:  # Critère à minimiser (coût) - plus c'est petit, mieux c'est
            # L'alternative domine si sa valeur <= valeur du profil
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
        # Obtenir la liste de tous les critères définis dans les poids
        criteria = list(self.params['weights'].keys())
        
        # Initialiser les variables pour le calcul de la concordance globale
        concordance_sum = 0.0  # Somme pondérée des concordances partielles
        total_weight = 0.0     # Somme des poids des critères valides
        
        # Parcourir tous les critères pour calculer la concordance globale
        for criterion in criteria:
            # Vérifier que le critère est présent dans l'alternative ET le profil
            if criterion in alternative and criterion in profile:
                # Récupérer le poids normalisé du critère
                weight = self.params['weights'][criterion]
                # Calculer la concordance partielle pour ce critère
                concordance = self._compute_concordance_index(alternative, profile, criterion)
                # Ajouter la contribution pondérée à la somme totale
                concordance_sum += weight * concordance
                # Ajouter le poids à la somme des poids valides
                total_weight += weight
        
        # Éviter la division par zéro si aucun critère n'est valide
        if total_weight == 0:
            return 0.0
        
        # Retourner la concordance globale normalisée (moyenne pondérée)
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
        # Calculer l'indice de concordance globale entre l'alternative et le profil
        concordance = self._compute_global_concordance(alternative, profile)
        # Récupérer le seuil lambda de la configuration
        lambda_threshold = self.params['lambda']
        
        # Il y a surclassement si la concordance atteint ou dépasse le seuil lambda
        return concordance >= lambda_threshold
    
    def _classify_pessimistic(self, alternative: Dict[str, float]) -> str:
        """
        Classification pessimiste : compare a aux profils du meilleur (b1) au pire (b4).
        
        Dans ELECTRE TRI pessimiste :
        - Si a surclasse b1 (le plus exigeant) → classe A'
        - Si a surclasse b2 mais pas b1 → classe B'
        - Si a surclasse b3 mais pas b2 → classe C'
        - Si a surclasse b4 mais pas b3 → classe D'
        - Si a ne surclasse aucun profil → classe E'
        
        Args:
            alternative: Valeurs de l'alternative à classer
            
        Returns:
            Classe assignée (A', B', C', D', E')
        """
        # Récupérer tous les profils limites de la configuration
        profiles = self.params['profiles']
        
        # Définir l'ordre des profils du plus exigeant au moins exigeant
        profile_names_ordered = ['b1', 'b2', 'b3', 'b4']
        # Classes correspondantes dans le même ordre (A' = meilleure, E' = pire)
        classes = ['A\'', 'B\'', 'C\'', 'D\'', 'E\'']
        
        # Tester les profils dans l'ordre décroissant d'exigence (b1, b2, b3, b4)
        for i, profile_name in enumerate(profile_names_ordered):
            # Vérifier que le profil existe dans la configuration
            if profile_name not in profiles:
                continue  # Passer au profil suivant si celui-ci n'existe pas
                
            # Récupérer les valeurs du profil limite
            profile = profiles[profile_name]
            
            # Tester si l'alternative surclasse le profil b_i
            if self._outrank_relation(alternative, profile):
                # Si a surclasse b_i, alors a appartient à la classe i
                return classes[i]
        
        # Si a ne surclasse aucun profil, alors a appartient à la classe la plus basse
        return 'E\''
    
    def _classify_optimistic(self, alternative: Dict[str, float]) -> str:
        """
        Classification optimiste selon ELECTRE TRI.
        
        Procédure : pour chaque aliment H, faire croître les indices des profils
        jusqu'au premier indice k tel que bk S H ET NON(H S bk).
        L'aliment H est alors affecté à la catégorie Ck-1.
        
        Avec notre numérotation (b1=meilleur, b4=pire), on parcourt de b4 à b1.
        
        Args:
            alternative: Valeurs de l'alternative à classer
            
        Returns:
            Classe assignée (A', B', C', D', E')
        """
        # Récupérer tous les profils limites de la configuration
        profiles = self.params['profiles']
        
        # Parcourir du profil le moins exigeant au plus exigeant
        # Dans notre convention : b4 (pire) → b1 (meilleur)
        profile_names_ordered = ['b4', 'b3', 'b2', 'b1']
        # Classes correspondantes quand la condition est satisfaite
        # Si condition sur b4 → E', si sur b3 → D', etc.
        classes = ['E\'', 'D\'', 'C\'', 'B\'']
        
        for i, profile_name in enumerate(profile_names_ordered):
            if profile_name not in profiles:
                continue
                
            profile = profiles[profile_name]
            
            # Selon la description ELECTRE TRI :
            # Condition : bk S H ET NON(H S bk)
            # bk surclasse H : le profil est "au moins aussi bon" que l'alternative
            profile_outranks_alt = self._outrank_relation(profile, alternative)
            # H surclasse bk : l'alternative est "au moins aussi bonne" que le profil
            alt_outranks_profile = self._outrank_relation(alternative, profile)
            
            # Si bk surclasse H ET H ne surclasse pas bk → incomparabilité en faveur du profil
            if profile_outranks_alt and not alt_outranks_profile:
                return classes[i]
        
        # Si aucune condition n'est satisfaite, H appartient à la meilleure classe
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
        # Choisir la méthode de classification selon la variante demandée
        if variant == "pessimistic":
            # Utiliser la procédure pessimiste (plus conservatrice)
            return self._classify_pessimistic(alternative)
        elif variant == "optimistic":
            # Utiliser la procédure optimiste (plus généreuse)
            return self._classify_optimistic(alternative)
        else:
            # Lever une exception si la variante n'est pas reconnue
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
        # Initialiser le dictionnaire pour stocker les valeurs de l'alternative
        alternative = {}
        # Récupérer la liste des critères définis dans les poids
        criteria = list(self.params['weights'].keys())
        
        # Extraire les valeurs des critères depuis la ligne du DataFrame
        for criterion in criteria:
            # Vérifier si le critère existe dans la ligne
            if criterion in row.index:
                # Récupérer la valeur du critère
                value = row[criterion]
                # Traiter les valeurs manquantes
                if not pd.isna(value):
                    # Convertir en float si la valeur est valide
                    alternative[criterion] = float(value)
                else:
                    # Stratégie pour les valeurs manquantes : assigner 0 (ou autre stratégie)
                    logger.debug(f"Valeur manquante pour critère {criterion}")
                    alternative[criterion] = 0.0  # Stratégie configurable
        
        # Vérifier qu'au moins un critère est disponible
        if not alternative:
            logger.warning("Aucun critère valide pour la classification")
            return 'N/A'  # Retourner un code d'erreur spécial
        
        # Tenter de classifier l'alternative
        try:
            # Appeler la méthode de classification principale
            return self.classify_alternative(alternative, variant)
        except Exception as e:
            # Capturer toute erreur et retourner un code d'erreur
            logger.error(f"Erreur classification : {e}")
            return 'ERROR'


def electre_sorting(df: pd.DataFrame, 
                   config_path: Optional[str] = None,
                   variant: str = "pessimistic",
                   lambda_threshold: Optional[float] = None,
                   custom_weights: Optional[Dict[str, float]] = None) -> pd.Series:
    """
    Applique ELECTRE TRI à un DataFrame entier.
    
    Args:
        df: DataFrame avec les données
        config_path: Chemin vers la configuration ELECTRE
        variant: "pessimistic" ou "optimistic"
        lambda_threshold: Seuil lambda personnalisé (optionnel)
        custom_weights: Poids personnalisés des critères (optionnel)
        
    Returns:
        Série avec les classes assignées
    """
    config_path = config_path or get_config_path("config/electre.yml")

    # Enregistrer le début du processus de classification dans les logs
    logger.info(f"Application ELECTRE TRI ({variant}) à {len(df)} alternatives")
    
    # Créer une instance d'ELECTRE TRI avec la configuration spécifiée
    electre = ElectreTri(config_path)
    
    # Modifier le seuil lambda si un seuil personnalisé est fourni
    if lambda_threshold is not None:
        # Valider que le seuil lambda est dans l'intervalle valide
        if not (0 < lambda_threshold <= 1):
            raise ValueError(f"Lambda doit être entre 0 et 1, reçu : {lambda_threshold}")
        # Appliquer le nouveau seuil lambda
        electre.params['lambda'] = lambda_threshold
        logger.info(f"Lambda personnalisé appliqué : {lambda_threshold}")
    
    # Modifier les poids des critères si des poids personnalisés sont fournis
    if custom_weights is not None:
        # Calculer la somme totale des poids personnalisés
        total_weight = sum(custom_weights.values())
        # Vérifier que la somme est positive (éviter poids négatifs/nuls)
        if total_weight <= 0:
            raise ValueError("La somme des poids personnalisés doit être positive")
        
        # Normaliser les poids personnalisés pour qu'ils somment à 1
        normalized_weights = {k: v/total_weight for k, v in custom_weights.items()}
        # Mettre à jour les poids dans la configuration ELECTRE
        electre.params['weights'].update(normalized_weights)
        logger.info(f"Poids personnalisés appliqués : {normalized_weights}")
    
    # Appliquer la méthode ELECTRE TRI à chaque ligne du DataFrame
    classifications = df.apply(
        # Fonction lambda qui classe chaque ligne avec la variante spécifiée
        lambda row: electre.classify_dataframe_row(row, variant), 
        axis=1  # Appliquer sur les lignes (pas les colonnes)
    )
    
    # Calculer et afficher les statistiques de distribution des classes
    class_distribution = classifications.value_counts()
    logger.info(f"Distribution des classes ELECTRE TRI :")
    # Afficher le nombre de produits dans chaque classe
    for class_name, count in class_distribution.items():
        logger.info(f"  {class_name}: {count} produits")
    
    # Retourner la série contenant les classes assignées
    return classifications


def classify_single_product(criteria_values: Dict[str, float],
                          config_path: Optional[str] = None, 
                          variant: str = "pessimistic",
                          lambda_threshold: Optional[float] = None,
                          custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, any]:
    """
    Classe un produit individuel avec ELECTRE TRI.
    
    Args:
        criteria_values: Dictionnaire {critère: valeur}
        config_path: Chemin vers la configuration
        variant: Variante ELECTRE TRI
        lambda_threshold: Seuil lambda personnalisé (optionnel)
        custom_weights: Poids personnalisés des critères (optionnel)
        
    Returns:
        Dictionnaire avec classe et détails
    """
    config_path = config_path or get_config_path("config/electre.yml")
    # Créer une instance d'ELECTRE TRI avec la configuration spécifiée
    electre = ElectreTri(config_path)
    
    # Modifier le seuil lambda si un seuil personnalisé est fourni
    if lambda_threshold is not None:
        # Valider que le seuil lambda est dans l'intervalle valide
        if not (0 < lambda_threshold <= 1):
            raise ValueError(f"Lambda doit être entre 0 et 1, reçu : {lambda_threshold}")
        # Appliquer le nouveau seuil lambda
        electre.params['lambda'] = lambda_threshold
    
    # Modifier les poids des critères si des poids personnalisés sont fournis
    if custom_weights is not None:
        # Calculer la somme totale des poids personnalisés
        total_weight = sum(custom_weights.values())
        # Vérifier que la somme est positive
        if total_weight <= 0:
            raise ValueError("La somme des poids personnalisés doit être positive")
        
        # Normaliser les poids personnalisés pour qu'ils somment à 1
        normalized_weights = {k: v/total_weight for k, v in custom_weights.items()}
        # Mettre à jour les poids dans la configuration ELECTRE
        electre.params['weights'].update(normalized_weights)
        logger.info(f"Poids personnalisés appliqués : {normalized_weights}")
    
    # Tenter de classifier le produit
    try:
        # Appliquer la méthode de classification ELECTRE TRI
        assigned_class = electre.classify_alternative(criteria_values, variant)
        
        # Calculer les concordances globales avec chaque profil pour information
        profiles = electre.params['profiles']  # Récupérer tous les profils limites
        concordances = {}  # Dictionnaire pour stocker les concordances
        
        # Calculer la concordance avec chaque profil limite
        for profile_name, profile_values in profiles.items():
            # Calculer l'indice de concordance globale entre le produit et le profil
            conc = electre._compute_global_concordance(criteria_values, profile_values)
            # Stocker la concordance arrondie à 3 décimales
            concordances[f"S(a,{profile_name})"] = round(conc, 3)
        
        # Retourner un dictionnaire avec tous les détails de la classification
        return {
            'class': assigned_class,        # Classe assignée (A', B', C', D', E')
            'variant': variant,             # Variante utilisée (pessimistic/optimistic)
            'concordances': concordances,   # Concordances avec chaque profil
            'lambda': electre.params['lambda']  # Seuil lambda utilisé
        }
        
    except Exception as e:
        # Gérer toute erreur survenant pendant la classification
        logger.error(f"Erreur classification individuelle : {e}")
        # Retourner un dictionnaire d'erreur
        return {
            'class': 'ERROR',   # Code d'erreur
            'error': str(e)     # Message d'erreur détaillé
        }


if __name__ == "__main__":
    # Section de test du module ELECTRE TRI (exécutée uniquement si le fichier est lancé directement)
    print("=== Test ELECTRE TRI ===")
    
    # Définir un produit alimentaire exemple pour tester la classification
    test_product = {
        'energy_100g': 1500,  # Énergie en kilojoules pour 100g
        'saturated_fat_100g': 3.0,  # Graisses saturées en grammes pour 100g
        'sugars_100g': 12.0,  # Sucres en grammes pour 100g
        'sodium_100g': 200,  # Sodium en milligrammes pour 100g
        'proteins_100g': 8.0,  # Protéines en grammes pour 100g
        'fiber_100g': 2.5,  # Fibres en grammes pour 100g
        'fruits_veg_nuts_percent': 30,  # Pourcentage de fruits/légumes/noix
        'additives_count': 2  # Nombre d'additifs présents
    }
    
    # Afficher les valeurs du produit test
    print("Produit test :", test_product)
    
    # Bloc try-except pour gérer les erreurs potentielles durant les tests
    try:
        # Tester la classification avec la variante pessimiste
        result_pess = classify_single_product(test_product, variant="pessimistic")
        print(f"\nClassification pessimiste : {result_pess['class']}")
        print(f"Concordances : {result_pess['concordances']}")
        
        # Tester la classification avec la variante optimiste
        result_opt = classify_single_product(test_product, variant="optimistic")
        print(f"\nClassification optimiste : {result_opt['class']}")
        
    except Exception as e:
        # Capturer et afficher toute erreur survenant pendant les tests
        print(f"Erreur de test : {e}")
    
    # Message de fin des tests
    print("\nTests ELECTRE TRI terminés !")