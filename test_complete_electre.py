#!/usr/bin/env python3
"""
Test complet des corrections ELECTRE TRI avec différents produits.
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from app.electre_tri import classify_single_product

def test_various_products():
    """Test avec différents types de produits."""
    print("=== TEST PRODUITS VARIÉS ===")
    
    products = {
        "Excellent produit": {
            'energy_100g': 300,      # Très faible
            'saturated_fat_100g': 0.5,  # Très faible
            'sugars_100g': 2.0,         # Très faible
            'sodium_100g': 50,          # Très faible
            'proteins_100g': 10.0,      # Élevé
            'fiber_100g': 5.0,          # Élevé
            'fruits_veg_nuts_percent': 60,  # Élevé
            'additives_count': 0        # Aucun
        },
        
        "Bon produit": {
            'energy_100g': 650,      # Entre b1 et b2
            'saturated_fat_100g': 1.5,  # Entre b1 et b2
            'sugars_100g': 7.0,         # Entre b1 et b2
            'sodium_100g': 150,         # Entre b1 et b2
            'proteins_100g': 5.0,       # Bon
            'fiber_100g': 2.0,          # Bon
            'fruits_veg_nuts_percent': 30,  # Entre b2 et b1
            'additives_count': 1        # Acceptable
        },
        
        "Produit moyen": {
            'energy_100g': 1200,     # Entre b2 et b3
            'saturated_fat_100g': 3.5,  # Entre b2 et b3
            'sugars_100g': 15.0,        # Entre b2 et b3
            'sodium_100g': 300,         # Entre b2 et b3
            'proteins_100g': 3.0,       # Moyen
            'fiber_100g': 1.0,          # Moyen
            'fruits_veg_nuts_percent': 15,  # Sous b2
            'additives_count': 2        # Entre b2 et b3
        },
        
        "Produit médiocre": {
            'energy_100g': 1800,     # Entre b3 et b4
            'saturated_fat_100g': 6.0,  # Entre b3 et b4
            'sugars_100g': 25.0,        # Entre b3 et b4
            'sodium_100g': 500,         # Entre b3 et b4
            'proteins_100g': 1.0,       # Faible
            'fiber_100g': 0.2,          # Faible
            'fruits_veg_nuts_percent': 5,   # Très faible
            'additives_count': 4        # Entre b3 et b4
        },
        
        "Très mauvais produit": {
            'energy_100g': 2500,     # Au-dessus de b4
            'saturated_fat_100g': 12.0, # Au-dessus de b4
            'sugars_100g': 45.0,        # Au-dessus de b4
            'sodium_100g': 1000,        # Au-dessus de b4
            'proteins_100g': 0.5,       # Très faible
            'fiber_100g': 0.0,          # Aucune
            'fruits_veg_nuts_percent': 0,   # Aucun
            'additives_count': 8        # Beaucoup
        }
    }
    
    results = []
    
    for product_name, product_values in products.items():
        print(f"\n--- {product_name} ---")
        print("Valeurs:", product_values)
        
        try:
            # Classification pessimiste
            result_pess = classify_single_product(
                product_values, 
                variant="pessimistic"
            )
            
            # Classification optimiste
            result_opt = classify_single_product(
                product_values, 
                variant="optimistic"
            )
            
            pess_class = result_pess['class']
            opt_class = result_opt['class']
            
            print(f"Classification pessimiste: {pess_class}")
            print(f"Classification optimiste: {opt_class}")
            
            results.append({
                'product': product_name,
                'pessimistic': pess_class,
                'optimistic': opt_class
            })
            
        except Exception as e:
            print(f"Erreur: {e}")
            results.append({
                'product': product_name,
                'pessimistic': 'ERROR',
                'optimistic': 'ERROR'
            })
    
    # Résumé
    print("\n=== RÉSUMÉ DES CLASSIFICATIONS ===")
    print(f"{'Produit':<20} {'Pessimiste':<12} {'Optimiste':<12}")
    print("-" * 50)
    
    for result in results:
        print(f"{result['product']:<20} {result['pessimistic']:<12} {result['optimistic']:<12}")
    
    # Vérification de la diversité
    pess_classes = [r['pessimistic'] for r in results if r['pessimistic'] != 'ERROR']
    opt_classes = [r['optimistic'] for r in results if r['optimistic'] != 'ERROR']
    
    print(f"\nClasses obtenues (pessimiste): {set(pess_classes)}")
    print(f"Classes obtenues (optimiste): {set(opt_classes)}")
    
    # Vérifier qu'on a bien des classes intermédiaires
    expected_classes = {'A\'', 'B\'', 'C\'', 'D\'', 'E\''}
    
    if len(set(pess_classes)) >= 3:
        print("✅ Diversité des classes pessimistes OK")
    else:
        print("⚠️ Diversité des classes pessimistes insuffisante")
    
    if len(set(opt_classes)) >= 3:
        print("✅ Diversité des classes optimistes OK")
    else:
        print("⚠️ Diversité des classes optimistes insuffisante")

def test_lambda_impact():
    """Test l'impact du paramètre lambda."""
    print("\n=== TEST IMPACT LAMBDA ===")
    
    # Produit à la frontière
    borderline_product = {
        'energy_100g': 800,      # Entre b2 et b3
        'saturated_fat_100g': 2.5,  # Entre b2 et b3
        'sugars_100g': 12.0,        # Entre b2 et b3
        'sodium_100g': 220,         # Entre b2 et b3
        'proteins_100g': 4.0,       # Moyen
        'fiber_100g': 1.2,          # Moyen
        'fruits_veg_nuts_percent': 15,  # Moyen
        'additives_count': 2        # Entre b2 et b3
    }
    
    lambda_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    print("Produit borderline:", borderline_product)
    print("\nImpact du lambda sur la classification:")
    print(f"{'Lambda':<8} {'Pessimiste':<12} {'Optimiste':<12}")
    print("-" * 35)
    
    for lambda_val in lambda_values:
        try:
            result_pess = classify_single_product(
                borderline_product, 
                variant="pessimistic",
                lambda_threshold=lambda_val
            )
            
            result_opt = classify_single_product(
                borderline_product, 
                variant="optimistic",
                lambda_threshold=lambda_val
            )
            
            print(f"{lambda_val:<8} {result_pess['class']:<12} {result_opt['class']:<12}")
            
        except Exception as e:
            print(f"{lambda_val:<8} ERROR        ERROR")

if __name__ == "__main__":
    test_various_products()
    test_lambda_impact()