#!/usr/bin/env python3
"""
Script de diagnostic pour comprendre le problème ELECTRE TRI.
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from app.electre_tri import ElectreTri
import yaml

def analyze_profiles():
    """Analyse les profils et leurs valeurs."""
    print("=== ANALYSE DES PROFILS ===")
    
    electre = ElectreTri()
    profiles = electre.params['profiles']
    
    print("Profils définis :")
    for profile_name in sorted(profiles.keys()):
        profile = profiles[profile_name]
        print(f"\n{profile_name}:")
        for criterion, value in profile.items():
            direction = electre.params['directions'][criterion]
            dir_symbol = "↑" if direction == 1 else "↓"
            print(f"  {criterion}: {value} {dir_symbol}")

def test_product_classification():
    """Test avec un produit intermédiaire."""
    print("\n=== TEST PRODUIT INTERMÉDIAIRE ===")
    
    # Produit avec des valeurs intermédiaires
    test_product = {
        'energy_100g': 1000,  # Entre b2 (700) et b3 (1400)
        'saturated_fat_100g': 3.0,  # Entre b2 (2.0) et b3 (4.0)
        'sugars_100g': 12.0,  # Entre b2 (9.0) et b3 (18.0)
        'sodium_100g': 250,  # Entre b2 (180) et b3 (360)
        'proteins_100g': 6.0,  # Au-dessus de tous les seuils
        'fiber_100g': 1.5,   # Au-dessus de tous les seuils
        'fruits_veg_nuts_percent': 25,  # Entre b2 (20) et b1 (40)
        'additives_count': 2  # Entre b2 (1) et b3 (3)
    }
    
    print("Produit test:", test_product)
    
    electre = ElectreTri()
    profiles = electre.params['profiles']
    
    # Calculer les concordances avec chaque profil
    print("\nConcordances avec chaque profil:")
    for profile_name in sorted(profiles.keys()):
        profile = profiles[profile_name]
        concordance = electre._compute_global_concordance(test_product, profile)
        outranks = electre._outrank_relation(test_product, profile)
        print(f"{profile_name}: concordance = {concordance:.3f}, surclasse = {outranks}")
    
    # Test classification
    class_pess = electre._classify_pessimistic(test_product)
    class_opt = electre._classify_optimistic(test_product)
    
    print(f"\nClassification pessimiste: {class_pess}")
    print(f"Classification optimiste: {class_opt}")

def debug_concordance_calculation():
    """Debug le calcul de concordance."""
    print("\n=== DEBUG CALCUL CONCORDANCE ===")
    
    test_product = {
        'energy_100g': 1000,
        'saturated_fat_100g': 3.0,
        'sugars_100g': 12.0,
        'sodium_100g': 250,
        'proteins_100g': 6.0,
        'fiber_100g': 1.5,
        'fruits_veg_nuts_percent': 25,
        'additives_count': 2
    }
    
    electre = ElectreTri()
    profiles = electre.params['profiles']
    
    # Détail du calcul pour b2
    print("Détail calcul concordance avec b2:")
    profile = profiles['b2']
    
    total_concordance = 0.0
    total_weight = 0.0
    
    for criterion in electre.params['weights']:
        if criterion in test_product and criterion in profile:
            weight = electre.params['weights'][criterion]
            concordance = electre._compute_concordance_index(test_product, profile, criterion)
            direction = electre.params['directions'][criterion]
            
            print(f"  {criterion}:")
            print(f"    Valeur produit: {test_product[criterion]}")
            print(f"    Valeur profil: {profile[criterion]}")
            print(f"    Direction: {direction} ({'maximiser' if direction == 1 else 'minimiser'})")
            print(f"    Poids: {weight:.3f}")
            print(f"    Concordance: {concordance}")
            
            total_concordance += weight * concordance
            total_weight += weight
    
    global_concordance = total_concordance / total_weight if total_weight > 0 else 0
    print(f"\nConcordance globale: {global_concordance:.3f}")
    print(f"Lambda: {electre.params['lambda']}")
    print(f"Surclassement: {global_concordance >= electre.params['lambda']}")

if __name__ == "__main__":
    analyze_profiles()
    test_product_classification()
    debug_concordance_calculation()