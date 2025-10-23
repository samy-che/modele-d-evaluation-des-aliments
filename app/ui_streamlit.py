"""
Interface utilisateur Streamlit pour le prototype Nutri-Score / ELECTRE TRI.
Deux onglets : calcul unitaire et traitement de dataset.
"""

import streamlit as st
import pandas as pd
import numpy as np
import yaml
import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


#streamlit run c:/Users/alila/Desktop/Projet_transparence/modele-d-evaluation-des-aliments/app/ui_streamlit.py         


# Ajouter le répertoire parent au path pour les imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

# Import des modules locaux
try:
    from app.io import load_data, ExcelDataLoader
    from app.normalize import normalize_data
    from app.nutriscore import apply_nutriscore, compute_nutriscore_single
    from app.electre_tri import electre_sorting, classify_single_product
    from app.eval import compare_nutriscore_electre
except ImportError as e:
    st.error(f"Erreur d'import des modules : {e}")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Nutri-Score & ELECTRE TRI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Fonctions utilitaires
@st.cache_data
def load_electre_config(config_path: str = "config/electre.yml") -> Dict[str, Any]:
    """Charge la configuration ELECTRE avec cache."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Erreur chargement configuration ELECTRE : {e}")
        return {}

@st.cache_data
def load_and_process_data(excel_path: str) -> tuple:
    """Charge et traite les données avec cache."""
    try:
        df, mapping, quality = load_data(excel_path)
        df_normalized, norm_report = normalize_data(df)
        return df_normalized, mapping, quality, norm_report, None
    except Exception as e:
        return None, None, None, None, str(e)

def display_nutriscore_result(result: Dict[str, Any], title: str = "Résultat Nutri-Score"):
    """Affiche le résultat du calcul Nutri-Score."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Score Nutri-Score", result['score'])
    
    with col2:
        # Couleur selon le label
        label_colors = {
            'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'E': '⚫'
        }
        color = label_colors.get(result['label'], '⚪')
        st.metric("Label Nutri-Score", f"{color} {result['label']}")
    
    # Détails du calcul
    if 'details' in result:
        with st.expander("Détails du calcul"):
            details = result['details']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Points négatifs :**")
                for key, value in details['negative_detail'].items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                st.write(f"**Total négatif: {details['negative_points']} pts**")
            
            with col2:
                st.write("**Points positifs :**")
                for key, value in details['positive_detail'].items():
                    if key != 'protein_rule_applied':
                        st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                if details['positive_detail'].get('protein_rule_applied', False):
                    st.write("⚠️ Règle protéines appliquée")
                st.write(f"**Total positif: {details['positive_points']} pts**")

def display_electre_result(result: Dict[str, Any], title: str = "Résultat ELECTRE TRI"):
    """Affiche le résultat de la classification ELECTRE TRI."""
    st.subheader(title)
    
    # Classe assignée
    class_colors = {
        "A'": '🟢', "B'": '🟡', "C'": '🟠', "D'": '🔴', "E'": '⚫'
    }
    color = class_colors.get(result['class'], '⚪')
    st.metric("Classe ELECTRE TRI", f"{color} {result['class']}")
    
    # Détails
    if 'credibilities' in result:
        with st.expander("Indices de crédibilité"):
            for profile, credibility in result['credibilities'].items():
                st.write(f"- {profile}: {credibility}")
            st.write(f"Seuil lambda: {result.get('lambda', 0.7)}")

def convert_units_if_needed(energy_value: float, is_kcal: bool, salt_value: float, is_salt: bool) -> tuple:
    """Convertit les unités si nécessaire."""
    # Conversion énergie
    if is_kcal:
        energy_kj = energy_value * 4.184
    else:
        energy_kj = energy_value
    
    # Conversion sel -> sodium
    if is_salt and salt_value > 0:
        sodium_mg = salt_value * 400
    else:
        sodium_mg = salt_value
    
    return energy_kj, sodium_mg

# Interface principale
def main():
    st.markdown('<h1 class="main-header">🥗 Nutri-Score & ELECTRE TRI</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **Prototype d'évaluation nutritionnelle** combinant le calcul officiel du Nutri-Score 
    et la méthode ELECTRE TRI pour le classement des produits alimentaires.
    """)
    
    # Sidebar pour les paramètres globaux
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Chargement de la configuration ELECTRE
        electre_config = load_electre_config()
        
        if electre_config:
            st.success("Configuration ELECTRE chargée ✅")
            
            st.divider()
            st.subheader("🎛️ Paramètres ELECTRE TRI")
            
            # Sélection de variante
            variant = st.selectbox(
                "Variante ELECTRE TRI", 
                ["pessimistic", "optimistic"], 
                index=0,
                help="Pessimiste: classement prudent, Optimiste: classement favorable"
            )
            
            # Paramètre lambda
            current_lambda = electre_config.get('lambda', 0.7)
            lambda_val = st.slider(
                "Seuil lambda", 
                min_value=0.5, 
                max_value=1.0, 
                value=current_lambda, 
                step=0.05,
                help="Seuil de concordance pour le surclassement"
            )
            
            # Modification des poids des critères
            st.write("**Configuration des poids:**")
            use_custom_weights = st.checkbox(
                "Modifier les poids des critères", 
                value=False,
                help="Cocher pour personnaliser les poids (seront normalisés automatiquement)"
            )
            
            custom_weights = None
            if use_custom_weights:
                with st.expander("⚖️ Ajuster les poids des critères", expanded=True):
                    st.write("*Les poids seront normalisés automatiquement pour sommer à 1*")
                    
                    weights = electre_config.get('weights', {})
                    custom_weights = {}
                    
                    # Organiser les critères par type
                    cost_criteria = ['energy_100g', 'saturated_fat_100g', 'sugars_100g', 'sodium_100g', 'additives_count']
                    benefit_criteria = ['proteins_100g', 'fiber_100g', 'fruits_veg_nuts_percent']
                    
                    st.write("**🔴 Éléments à limiter:**")
                    for criterion in cost_criteria:
                        if criterion in weights:
                            label = criterion.replace('_', ' ').replace('100g', '(100g)').title()
                            custom_weights[criterion] = st.slider(
                                label,
                                min_value=0.01,
                                max_value=1.0,
                                value=float(weights[criterion]),
                                step=0.01,
                                key=f"weight_{criterion}"
                            )
                    
                    st.write("**🟢 Éléments favorables:**")
                    for criterion in benefit_criteria:
                        if criterion in weights:
                            label = criterion.replace('_', ' ').replace('100g', '(100g)').replace('percent', '(%)').title()
                            custom_weights[criterion] = st.slider(
                                label,
                                min_value=0.01,
                                max_value=1.0,
                                value=float(weights[criterion]),
                                step=0.01,
                                key=f"weight_{criterion}"
                            )
                    
                    # Afficher les poids normalisés en temps réel
                    if custom_weights:
                        total_weight = sum(custom_weights.values())
                        st.write("**Poids normalisés (aperçu):**")
                        for criterion, weight in custom_weights.items():
                            normalized = weight / total_weight
                            st.write(f"- {criterion.replace('_', ' ')}: {normalized:.3f}")
            else:
                with st.expander("📊 Poids actuels des critères"):
                    weights = electre_config.get('weights', {})
                    for criterion, weight in weights.items():
                        st.write(f"- {criterion.replace('_', ' ').title()}: {weight:.3f}")
        else:
            st.error("Configuration ELECTRE non disponible ❌")
    
    # Onglets principaux
    tab1, tab2 = st.tabs(["🧮 Calcul Unitaire", "📊 Traitement Dataset"])
    
    # ONGLET 1 : CALCUL UNITAIRE
    with tab1:
        st.header("Calcul individuel Nutri-Score & ELECTRE TRI")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("💊 Saisie des composantes nutritionnelles")
            
            # Saisie des 7 composantes
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**Éléments à limiter:**")
                
                # Énergie avec conversion
                energy_unit = st.selectbox("Unité d'énergie", ["kJ", "kcal"], index=0)
                energy_val = st.number_input(f"Énergie ({energy_unit})", min_value=0.0, value=1500.0, step=10.0)
                
                # AG saturés
                sat_fat = st.number_input("Acides gras saturés (g)", min_value=0.0, value=3.0, step=0.1)
                
                # Sucres
                sugars = st.number_input("Sucres (g)", min_value=0.0, value=10.0, step=0.5)
                
                # Sodium avec conversion
                sodium_unit = st.selectbox("Unité sodium/sel", ["Sodium (mg)", "Sel (g)"], index=0)
                sodium_val = st.number_input(
                    sodium_unit, 
                    min_value=0.0, 
                    value=200.0 if "mg" in sodium_unit else 0.5, 
                    step=10.0 if "mg" in sodium_unit else 0.1
                )
            
            with col_b:
                st.write("**Éléments favorables:**")
                
                # Protéines
                proteins = st.number_input("Protéines (g)", min_value=0.0, value=8.0, step=0.5)
                
                # Fibres
                fiber = st.number_input("Fibres (g)", min_value=0.0, value=2.0, step=0.1)
                
                # Fruits/légumes/noix
                fruits_veg = st.number_input("Fruits/légumes/noix (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0)
            
            # Conversions d'unités
            is_kcal = energy_unit == "kcal"
            is_salt = "Sel" in sodium_unit
            
            energy_kj, sodium_mg = convert_units_if_needed(energy_val, is_kcal, sodium_val, is_salt)
            
            # Affichage des valeurs converties
            if is_kcal or is_salt:
                st.info(f"**Valeurs converties:** Énergie = {energy_kj:.1f} kJ, Sodium = {sodium_mg:.1f} mg")
        
        with col2:
            st.subheader("📊 État de la configuration")
            
            if electre_config:
                st.success("✅ Configuration ELECTRE chargée")
                
                # Afficher un résumé des paramètres actuels
                st.info(f"""
                **Paramètres actuels (sidebar):**
                - Variante: {variant}
                - Lambda: {lambda_val}
                - Poids personnalisés: {'✅ Oui' if custom_weights else '❌ Non'}
                """)
                
                if custom_weights:
                    total_weight = sum(custom_weights.values())
                    with st.expander("Poids personnalisés"):
                        for criterion, weight in custom_weights.items():
                            normalized = weight / total_weight
                            st.write(f"- {criterion.replace('_', ' ')}: {normalized:.3f}")
            else:
                st.error("❌ Configuration ELECTRE non disponible")
        
        # Boutons de calcul
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧮 Calculer Nutri-Score", type="primary"):
                try:
                    # Calcul Nutri-Score
                    nutri_result = compute_nutriscore_single(
                        energy_kj=energy_kj,
                        saturated_fat_g=sat_fat,
                        sugars_g=sugars,
                        sodium_mg=sodium_mg,
                        fiber_g=fiber,
                        protein_g=proteins,
                        fruits_veg_nuts_percent=fruits_veg
                    )
                    
                    st.success("Calcul Nutri-Score terminé !")
                    display_nutriscore_result(nutri_result)
                    
                except Exception as e:
                    st.error(f"Erreur calcul Nutri-Score : {e}")
        
        with col2:
            if st.button("🎯 Classer avec ELECTRE TRI", type="secondary") and electre_config:
                try:
                    # Préparer les critères
                    criteria_values = {
                        'energy_100g': energy_kj,
                        'saturated_fat_100g': sat_fat,
                        'sugars_100g': sugars,
                        'sodium_100g': sodium_mg,
                        'proteins_100g': proteins,
                        'fiber_100g': fiber,
                        'fruits_veg_nuts_percent': fruits_veg,
                        'additives_count': 0  # Par défaut
                    }
                    
                    # Classification ELECTRE TRI avec paramètres personnalisés
                    electre_result = classify_single_product(
                        criteria_values, 
                        variant=variant,
                        lambda_threshold=lambda_val,
                        custom_weights=custom_weights
                    )
                    
                    st.success(f"Classification ELECTRE TRI ({variant}) terminée !")
                    st.info(f"Paramètres utilisés: Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}")
                    display_electre_result(electre_result)
                    
                except Exception as e:
                    st.error(f"Erreur classification ELECTRE TRI : {e}")
    
    # ONGLET 2 : TRAITEMENT DATASET
    with tab2:
        st.header("Traitement du dataset et comparaison")
        
        # Section chargement des données
        st.subheader("📁 Chargement des données")
        
        # Choix du fichier
        data_source = st.radio(
            "Source des données:",
            ["Fichier par défaut (data/produits.xlsx)", "Charger un autre fichier"]
        )
        
        excel_path = "data/produits.xlsx"
        
        if data_source == "Charger un autre fichier":
            uploaded_file = st.file_uploader(
                "Choisir un fichier Excel", 
                type=['xlsx', 'xls'],
                help="Le fichier doit contenir les colonnes nutritionnelles requises"
            )
            
            if uploaded_file:
                # Sauvegarder temporairement
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                excel_path = temp_path
        
        # État des données chargées
        if 'dataset_loaded' not in st.session_state:
            st.session_state.dataset_loaded = False
            st.session_state.df_processed = None
        
        # Bouton de chargement
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📊 Charger l'Excel", type="primary"):
                with st.spinner("Chargement et normalisation des données..."):
                    df_processed, mapping, quality, norm_report, error = load_and_process_data(excel_path)
                
                if error:
                    st.error(f"Erreur de chargement : {error}")
                else:
                    st.session_state.dataset_loaded = True
                    st.session_state.df_processed = df_processed
                    
                    st.success(f"✅ Données chargées : {len(df_processed)} produits")
                    
                    # Afficher le rapport de qualité
                    with st.expander("Rapport de qualité des données"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write("**Mapping des colonnes:**")
                            for canonical, original in mapping.items():
                                st.write(f"- {canonical} ← {original}")
                        
                        with col_b:
                            st.write("**Normalisation appliquée:**")
                            for step in norm_report.get('steps_applied', []):
                                st.write(f"✓ {step}")
                            
                            if norm_report.get('rows_removed', 0) > 0:
                                st.warning(f"⚠️ {norm_report['rows_removed']} lignes supprimées")
        
        # Section traitement si données chargées
        if st.session_state.dataset_loaded and st.session_state.df_processed is not None:
            df = st.session_state.df_processed
            
            st.divider()
            
            # Prévisualisation des données
            st.subheader("👁️ Aperçu des données")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                st.metric("Nombre de produits", len(df))
                nutritional_cols = ['energy_100g', 'proteins_100g', 'fiber_100g']
                available_cols = [col for col in nutritional_cols if col in df.columns]
                st.metric("Colonnes nutritionnelles", len(available_cols))
            
            st.divider()
            
            # Boutons de traitement
            st.subheader("🔄 Traitements")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧮 Recalculer Nutri-Score", type="secondary"):
                    with st.spinner("Calcul du Nutri-Score sur le dataset..."):
                        try:
                            df_with_nutri = apply_nutriscore(df)
                            st.session_state.df_processed = df_with_nutri
                            
                            # Statistiques
                            label_dist = df_with_nutri['ns_label_calc'].value_counts()
                            
                            st.success("✅ Nutri-Score calculé !")
                            
                            st.write("**Distribution des labels:**")
                            for label, count in label_dist.items():
                                st.write(f"- {label}: {count}")
                            
                        except Exception as e:
                            st.error(f"Erreur calcul Nutri-Score : {e}")
            
            with col2:
                if st.button("🎯 Appliquer ELECTRE TRI", type="secondary"):
                    if not electre_config:
                        st.error("Configuration ELECTRE non disponible")
                    else:
                        with st.spinner(f"Classification ELECTRE TRI ({variant})..."):
                            try:
                                # Utiliser les paramètres de la sidebar
                                classifications = electre_sorting(
                                    df, 
                                    variant=variant,
                                    lambda_threshold=lambda_val,
                                    custom_weights=custom_weights
                                )
                                
                                df_with_electre = df.copy()
                                df_with_electre['electre_cat'] = classifications
                                st.session_state.df_processed = df_with_electre
                                
                                # Statistiques
                                class_dist = classifications.value_counts()
                                
                                st.success(f"✅ ELECTRE TRI ({variant}) appliqué !")
                                st.info(f"Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}")
                                
                                st.write("**Distribution des classes:**")
                                for classe, count in class_dist.items():
                                    st.write(f"- {classe}: {count}")
                                
                            except Exception as e:
                                st.error(f"Erreur ELECTRE TRI : {e}")
                                import traceback
                                st.code(traceback.format_exc())
            
            with col3:
                # Vérifier si les deux colonnes sont présentes
                has_nutri = 'ns_label_calc' in df.columns
                has_electre = 'electre_cat' in df.columns
                
                if st.button("📊 Comparer méthodes", 
                           type="primary", 
                           disabled=not (has_nutri and has_electre)):
                    
                    with st.spinner("Génération de la comparaison..."):
                        try:
                            # Comparaison complète
                            report = compare_nutriscore_electre(
                                df, 
                                nutriscore_col='ns_label_calc',
                                electre_col='electre_cat'
                            )
                            
                            st.success("✅ Comparaison terminée !")
                            
                            # Affichage des métriques
                            metrics = report.get('metrics', {})
                            if metrics:
                                st.subheader("📈 Métriques de comparaison")
                                
                                col_a, col_b, col_c, col_d = st.columns(4)
                                
                                with col_a:
                                    accuracy = metrics.get('accuracy', 0)
                                    st.metric("Accuracy", f"{accuracy:.3f}")
                                
                                with col_b:
                                    f1_macro = metrics.get('f1_macro', 0)
                                    st.metric("F1-Score Macro", f"{f1_macro:.3f}")
                                
                                with col_c:
                                    mae = metrics.get('mae_rank', 0)
                                    st.metric("MAE (rang)", f"{mae:.3f}")
                                
                                with col_d:
                                    corr = metrics.get('spearman_correlation', 0)
                                    st.metric("Corrélation", f"{corr:.3f}")
                                
                                # Tolérance
                                st.write("**Accuracy avec tolérance:**")
                                col_e, col_f = st.columns(2)
                                
                                with col_e:
                                    tol1 = metrics.get('accuracy_tolerance_1', 0)
                                    st.write(f"±1 niveau: {tol1:.3f}")
                                
                                with col_f:
                                    tol2 = metrics.get('accuracy_tolerance_2', 0)
                                    st.write(f"±2 niveaux: {tol2:.3f}")
                            
                            # Fichiers générés
                            files = report.get('summary', {}).get('files_generated', {})
                            if files:
                                st.subheader("📁 Fichiers générés")
                                for file_type, file_path in files.items():
                                    if os.path.exists(file_path):
                                        st.write(f"✅ {file_type}: `{file_path}`")
                                    else:
                                        st.write(f"❌ {file_type}: `{file_path}` (non trouvé)")
                            
                        except Exception as e:
                            st.error(f"Erreur comparaison : {e}")
                            import traceback
                            st.code(traceback.format_exc())
                
                if not (has_nutri and has_electre):
                    st.info("💡 Calculez d'abord Nutri-Score et ELECTRE TRI")
            
            # Section export
            if st.session_state.df_processed is not None:
                st.divider()
                st.subheader("💾 Export des résultats")
                
                # Bouton de téléchargement
                csv_data = st.session_state.df_processed.to_csv(index=False)
                
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv_data,
                    file_name="dataset_traite.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()