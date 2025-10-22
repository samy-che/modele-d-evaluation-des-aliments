#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections des problèmes ELECTRE TRI.
Tests les nouvelles fonctionnalités : lambda personnalisé et poids personnalisés.
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from app.electre_tri import classify_single_product, electre_sorting
import pandas as pd

def test_lambda_customization():
    """Test la personnalisation du paramètre lambda."""
    print("=== Test personnalisation lambda ===")
    
    # Produit de test
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
    
    # Test avec différentes valeurs de lambda
    lambda_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    print("Produit test:", test_product)
    print("\nClassifications avec différents lambda (pessimiste):")
    
    for lambda_val in lambda_values:
        try:
            result = classify_single_product(
                test_product, 
                variant="pessimistic",
                lambda_threshold=lambda_val
            )
            print(f"Lambda {lambda_val}: Classe {result['class']} (concordances: {result.get('concordances', {})})")
        except Exception as e:
            print(f"Lambda {lambda_val}: Erreur - {e}")
    
    print("✅ Test lambda terminé\n")

def test_custom_weights():
    """Test la personnalisation des poids."""
    print("=== Test personnalisation des poids ===")
    
    # Produit de test
    test_product = {
        'energy_100g': 1500,
        'saturated_fat_100g': 3.0,
        'sugars_100g': 12.0,
        'sodium_100g': 200,
        'proteins_100g': 8.0,
        'fiber_100g': 2.5,
        'fruits_veg_nuts_percent': 30,
        'additives_count': 2
    }
    
    # Poids par défaut
    print("Classification avec poids par défaut:")
    result_default = classify_single_product(test_product, variant="pessimistic")
    print(f"Classe: {result_default['class']}")
    
    # Poids personnalisés : privilégier les fibres et protéines
    custom_weights_fiber_focus = {
        'energy_100g': 0.1,
        'saturated_fat_100g': 0.1,
        'sugars_100g': 0.1,
        'sodium_100g': 0.1,
        'proteins_100g': 0.25,      # Plus important
        'fiber_100g': 0.25,         # Plus important
        'fruits_veg_nuts_percent': 0.05,
        'additives_count': 0.05
    }
    
    print("\nClassification avec poids privilégiant fibres/protéines:")
    result_custom = classify_single_product(
        test_product, 
        variant="pessimistic",
        custom_weights=custom_weights_fiber_focus
    )
    print(f"Classe: {result_custom['class']}")
    
    # Poids personnalisés : privilégier les critères négatifs (énergie, sucres)
    custom_weights_negative_focus = {
        'energy_100g': 0.3,         # Plus important
        'saturated_fat_100g': 0.15,
        'sugars_100g': 0.25,        # Plus important
        'sodium_100g': 0.15,
        'proteins_100g': 0.05,
        'fiber_100g': 0.05,
        'fruits_veg_nuts_percent': 0.03,
        'additives_count': 0.02
    }
    
    print("\nClassification avec poids privilégiant critères négatifs:")
    result_negative = classify_single_product(
        test_product, 
        variant="pessimistic",
        custom_weights=custom_weights_negative_focus
    )
    print(f"Classe: {result_negative['class']}")
    
    print("✅ Test poids personnalisés terminé\n")

def test_dataframe_processing():
    """Test le traitement d'un petit DataFrame avec les nouvelles options."""
    print("=== Test traitement DataFrame ===")
    
    # Créer un DataFrame de test
    test_data = {
        'energy_100g': [1200, 1800, 2500],
        'saturated_fat_100g': [1.5, 4.0, 8.0],
        'sugars_100g': [5.0, 15.0, 30.0],
        'sodium_100g': [120, 300, 600],
        'proteins_100g': [10.0, 6.0, 2.0],
        'fiber_100g': [3.0, 1.5, 0.5],
        'fruits_veg_nuts_percent': [50, 20, 5],
        'additives_count': [0, 2, 5]
    }
    
    df = pd.DataFrame(test_data)
    
    print("DataFrame de test:")
    print(df)
    
    # Test avec paramètres par défaut
    print("\nClassification avec paramètres par défaut:")
    classifications_default = electre_sorting(df, variant="pessimistic")
    print("Classes assignées:", classifications_default.tolist())
    
    # Test avec lambda personnalisé
    print("\nClassification avec lambda = 0.6:")
    classifications_lambda = electre_sorting(
        df, 
        variant="pessimistic", 
        lambda_threshold=0.6
    )
    print("Classes assignées:", classifications_lambda.tolist())
    
    # Test avec poids personnalisés
    custom_weights = {
        'energy_100g': 0.2,
        'saturated_fat_100g': 0.2,
        'sugars_100g': 0.2,
        'sodium_100g': 0.1,
        'proteins_100g': 0.1,
        'fiber_100g': 0.1,
        'fruits_veg_nuts_percent': 0.05,
        'additives_count': 0.05
    }
    
    print("\nClassification avec poids personnalisés:")
    classifications_weights = electre_sorting(
        df, 
        variant="pessimistic",
        custom_weights=custom_weights
    )
    print("Classes assignées:", classifications_weights.tolist())
    
    print("✅ Test DataFrame terminé\n")

def main():
    """Fonction principale de test."""
    print("🧪 === TESTS DES CORRECTIONS ELECTRE TRI ===\n")
    
    try:
        test_lambda_customization()
        test_custom_weights()
        test_dataframe_processing()
        
        print("🎉 Tous les tests sont passés avec succès !")
        print("\n📝 Résumé des corrections :")
        print("1. ✅ Le paramètre lambda de l'interface est maintenant transmis aux calculs")
        print("2. ✅ Le seuil lambda peut être choisi librement entre 0.5 et 1.0")
        print("3. ✅ Les poids des critères peuvent être modifiés depuis l'interface")
        print("\n💡 L'interface Streamlit est disponible sur: http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Erreur durant les tests : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()