#!/usr/bin/env python3
"""
Script de test spécifique pour les métriques et la matrice de confusion.
"""

import sys
import os
sys.path.append('.')

from app.io import load_data
from app.normalize import normalize_data
from app.nutriscore import apply_nutriscore
from app.electre_tri import electre_sorting
from app.eval import compare_nutriscore_electre
import matplotlib.pyplot as plt

def test_metriques_complet():
    """Test complet du système de métriques et visualisations."""
    print("=" * 70)
    print("🧪 TEST COMPLET DES MÉTRIQUES ET MATRICE DE CONFUSION")
    print("=" * 70)
    
    # 1. Chargement et préparation des données
    print("\n📥 1. Chargement des données...")
    df, mapping, quality = load_data('data/produits.xlsx')
    print(f"   ✅ {len(df)} produits chargés")
    
    # 2. Normalisation
    print("\n🔧 2. Normalisation...")
    df_norm, report = normalize_data(df)
    print(f"   ✅ {len(df_norm)} produits normalisés")
    
    # 3. Calcul Nutri-Score
    print("\n🥗 3. Calcul Nutri-Score...")
    df_nutri = apply_nutriscore(df_norm)
    nutri_dist = df_nutri['ns_label_calc'].value_counts().to_dict()
    print(f"   ✅ Distribution Nutri-Score : {nutri_dist}")
    
    # 4. Classification ELECTRE TRI
    print("\n⚖️ 4. Classification ELECTRE TRI...")
    classifications = electre_sorting(df_nutri, variant="pessimistic")
    df_nutri['electre_cat'] = classifications
    electre_dist = classifications.value_counts().to_dict()
    print(f"   ✅ Distribution ELECTRE : {electre_dist}")
    
    # 5. Génération du rapport de comparaison
    print("\n📊 5. Génération du rapport de comparaison...")
    report = compare_nutriscore_electre(
        df_nutri,
        nutriscore_col='ns_label_calc',
        electre_col='electre_cat',
        output_dir='outputs'
    )
    
    # 6. Affichage des résultats
    print("\n" + "=" * 70)
    print("📈 RÉSULTATS DE LA COMPARAISON")
    print("=" * 70)
    
    summary = report.get('summary', {})
    print(f"\n📊 Statistiques générales :")
    print(f"   • Produits totaux    : {summary.get('total_products', 0)}")
    print(f"   • Comparaisons valides: {summary.get('valid_comparisons', 0)}")
    
    metrics = report.get('metrics', {})
    if metrics:
        print(f"\n🎯 Métriques de performance :")
        print(f"   • Accuracy (exact)          : {metrics.get('accuracy', 0):.3f}")
        print(f"   • F1-Score (macro)          : {metrics.get('f1_macro', 0):.3f}")
        print(f"   • F1-Score (weighted)       : {metrics.get('f1_weighted', 0):.3f}")
        print(f"   • MAE (rang)                : {metrics.get('mae_rank', 0):.3f}")
        print(f"   • Accuracy (tolérance ±1)   : {metrics.get('accuracy_tolerance_1', 0):.3f}")
        print(f"   • Accuracy (tolérance ±2)   : {metrics.get('accuracy_tolerance_2', 0):.3f}")
        print(f"   • Corrélation Spearman      : {metrics.get('spearman_correlation', 0):.3f}")
        print(f"   • P-value                   : {metrics.get('spearman_p_value', 0):.6f}")
    
    files = summary.get('files_generated', {})
    if files:
        print(f"\n📁 Fichiers générés :")
        for file_type, file_path in files.items():
            status = "✅" if os.path.exists(file_path) else "❌"
            print(f"   {status} {file_type:20s} : {file_path}")
    
    # 7. Vérification de la matrice de confusion
    cm = report.get('confusion_matrix', [])
    if cm:
        print(f"\n🔢 Matrice de confusion :")
        cm_meta = report.get('confusion_metadata', {})
        nutri_labels = cm_meta.get('nutriscore_labels', [])
        electre_labels = cm_meta.get('electre_labels', [])
        
        # Affichage formaté de la matrice
        print(f"\n   Labels Nutri-Score (lignes) : {nutri_labels}")
        electre_display = [l + "'" for l in electre_labels]
        print(f"   Labels ELECTRE (colonnes)   : {electre_display}")
        print(f"\n   Matrice :")
        import numpy as np
        cm_array = np.array(cm)
        for i, row in enumerate(cm_array):
            label = nutri_labels[i] if i < len(nutri_labels) else f"L{i}"
            print(f"   {label:4s} {row}")
    
    # 8. Interprétation des résultats
    print("\n" + "=" * 70)
    print("💡 INTERPRÉTATION")
    print("=" * 70)
    
    if metrics:
        accuracy = metrics.get('accuracy', 0)
        tol1 = metrics.get('accuracy_tolerance_1', 0)
        corr = metrics.get('spearman_correlation', 0)
        
        print(f"\n🎯 Concordance exacte : {accuracy*100:.1f}%")
        if accuracy > 0.8:
            print("   ➜ Excellente concordance entre les deux méthodes")
        elif accuracy > 0.6:
            print("   ➜ Bonne concordance entre les deux méthodes")
        elif accuracy > 0.4:
            print("   ➜ Concordance modérée entre les deux méthodes")
        else:
            print("   ➜ Faible concordance - les méthodes diffèrent significativement")
        
        print(f"\n🎯 Concordance à ±1 niveau : {tol1*100:.1f}%")
        if tol1 > 0.9:
            print("   ➜ Les méthodes sont très proches (différence max 1 niveau)")
        
        print(f"\n🎯 Corrélation des rangs : {corr:.3f}")
        if corr > 0.8:
            print("   ➜ Forte corrélation - classement très similaire")
        elif corr > 0.6:
            print("   ➜ Corrélation modérée - classement globalement similaire")
        elif corr > 0.4:
            print("   ➜ Corrélation faible - classements assez différents")
        else:
            print("   ➜ Très faible corrélation - classements très différents")
    
    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ AVEC SUCCÈS !")
    print("=" * 70)
    print(f"\n💡 Pour visualiser les graphiques, consultez :")
    print(f"   • outputs/reports/confusion_matrix.png")
    print(f"   • outputs/reports/metrics_summary.png")
    
    return report

if __name__ == "__main__":
    try:
        report = test_metriques_complet()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
