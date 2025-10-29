"""
Interface utilisateur Streamlit pour le prototype Nutri-Score / ELECTRE TRI.
Deux onglets : calcul unitaire et traitement de dataset.
"""

# Import des bibliothèques nécessaires
import streamlit as st  # Framework web pour créer l'interface utilisateur
import pandas as pd     # Pour manipuler les données sous forme de DataFrames
import numpy as np      # Pour les calculs numériques et la gestion des valeurs NaN
import yaml            # Pour lire les fichiers de configuration YAML
import sys             # Pour modifier le chemin d'importation des modules
import os              # Pour les opérations sur le système de fichiers
import logging         # Pour enregistrer les logs et messages de débogage
from pathlib import Path  # Pour gérer les chemins de fichiers de manière portable
from typing import Dict, Any, Optional  # Pour les annotations de types

# Configurer le chemin d'importation pour accéder aux modules locaux
current_dir = Path(__file__).parent  # Obtenir le répertoire du fichier actuel
sys.path.append(str(current_dir.parent))  # Ajouter le répertoire parent au path

# Tenter d'importer les modules locaux avec gestion d'erreur
try:
    # Import du module de chargement des données Excel
    from app.io import load_data, ExcelDataLoader
    # Import du module de normalisation des données
    from app.normalize import normalize_data
    # Import des fonctions de calcul Nutri-Score
    from app.nutriscore import apply_nutriscore, compute_nutriscore_single
    # Import des fonctions de classification ELECTRE TRI
    from app.electre_tri import electre_sorting, classify_single_product
    # Import du module de comparaison entre méthodes
    from app.eval import compare_nutriscore_electre
except ImportError as e:
    # Afficher une erreur Streamlit et arrêter l'exécution si les imports échouent
    st.error(f"Erreur d'import des modules : {e}")
    st.stop()  # Arrêter l'exécution de l'application Streamlit

# Configuration générale de la page Streamlit
st.set_page_config(
    page_title="Nutri-Score & ELECTRE TRI",  # Titre affiché dans l'onglet du navigateur
    page_icon="🥗",                          # Icône affichée dans l'onglet
    layout="wide",                           # Utiliser toute la largeur de l'écran
    initial_sidebar_state="expanded"         # Sidebar ouverte par défaut
)

# Configuration du système de logging pour tracer l'exécution
logging.basicConfig(level=logging.INFO)  # Niveau de log INFO et plus
logger = logging.getLogger(__name__)      # Créer un logger spécifique à ce module

# Définir des styles CSS personnalisés pour améliorer l'apparence de l'interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;          /* Taille de police grande pour le titre principal */
        color: #1f77b4;             /* Couleur bleue pour le titre */
        text-align: center;         /* Centrer le titre */
        margin-bottom: 2rem;        /* Espacement en bas du titre */
    }
    .metric-card {
        background-color: #f0f2f6;  /* Couleur de fond gris clair pour les cartes de métriques */
        padding: 1rem;              /* Espacement interne */
        border-radius: 0.5rem;      /* Coins arrondis */
        margin: 0.5rem 0;           /* Espacement vertical */
    }
    .success-box {
        background-color: #d4edda;  /* Couleur de fond verte claire pour les messages de succès */
        border: 1px solid #c3e6cb;  /* Bordure verte */
        color: #155724;             /* Texte vert foncé */
        padding: 1rem;              /* Espacement interne */
        border-radius: 0.25rem;     /* Coins légèrement arrondis */
        margin: 1rem 0;             /* Espacement vertical */
    }
    .error-box {
        background-color: #f8d7da;  /* Couleur de fond rouge claire pour les messages d'erreur */
        border: 1px solid #f5c6cb;  /* Bordure rouge */
        color: #721c24;             /* Texte rouge foncé */
        padding: 1rem;              /* Espacement interne */
        border-radius: 0.25rem;     /* Coins légèrement arrondis */
        margin: 1rem 0;             /* Espacement vertical */
    }
</style>
""", unsafe_allow_html=True)  # Permettre l'injection de HTML/CSS personnalisé

# Définition des fonctions utilitaires avec mise en cache Streamlit
@st.cache_data  # Décorateur pour mettre en cache les résultats et éviter de recharger inutilement
def load_electre_config(config_path: str = "config/electre.yml") -> Dict[str, Any]:
    """Charge la configuration ELECTRE avec cache."""
    try:
        # Ouvrir et lire le fichier de configuration ELECTRE en UTF-8
        with open(config_path, 'r', encoding='utf-8') as f:
            # Parser le contenu YAML et le retourner comme dictionnaire
            return yaml.safe_load(f)
    except Exception as e:
        # Afficher une erreur Streamlit si le chargement échoue
        st.error(f"Erreur chargement configuration ELECTRE : {e}")
        # Retourner un dictionnaire vide en cas d'erreur
        return {}

@st.cache_data  # Mise en cache pour éviter de reprocesser les mêmes données
def load_and_process_data(excel_path: str) -> tuple:
    """Charge et traite les données avec cache."""
    try:
        # Charger les données depuis le fichier Excel
        df, mapping, quality = load_data(excel_path)
        # Normaliser les données chargées
        df_normalized, norm_report = normalize_data(df)
        # Retourner tous les résultats avec None pour l'erreur (succès)
        return df_normalized, mapping, quality, norm_report, None
    except Exception as e:
        # Retourner des valeurs None et le message d'erreur en cas d'échec
        return None, None, None, None, str(e)

def display_nutriscore_result(result: Dict[str, Any], title: str = "Résultat Nutri-Score"):
    """Affiche le résultat du calcul Nutri-Score."""
    # Créer deux colonnes pour afficher le score et le label côte à côte
    col1, col2 = st.columns(2)
    
    # Colonne 1 : Afficher le score numérique
    with col1:
        st.metric("Score Nutri-Score", result['score'])
    
    # Colonne 2 : Afficher le label avec couleur correspondante
    with col2:
        # Dictionnaire d'association entre labels et emojis colorés
        label_colors = {
            'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'E': '⚫'
        }
        # Récupérer l'emoji correspondant au label (blanc par défaut)
        color = label_colors.get(result['label'], '⚪')
        # Afficher le label avec son emoji coloré
        st.metric("Label Nutri-Score", f"{color} {result['label']}")
    
    # Section extensible pour les détails du calcul (si disponibles)
    if 'details' in result:
        with st.expander("Détails du calcul"):
            # Récupérer les détails du calcul
            details = result['details']
            
            # Créer deux colonnes pour séparer points négatifs et positifs
            col1, col2 = st.columns(2)
            
            # Colonne 1 : Points négatifs (éléments défavorables)
            with col1:
                st.write("**Points négatifs :**")
                # Parcourir tous les éléments négatifs et les afficher
                for key, value in details['negative_detail'].items():
                    # Formatter le nom du critère et afficher les points
                    st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                # Afficher le total des points négatifs en gras
                st.write(f"**Total négatif: {details['negative_points']} pts**")
            
            # Colonne 2 : Points positifs (éléments favorables)
            with col2:
                st.write("**Points positifs :**")
                # Parcourir les éléments positifs en excluant les indicateurs techniques
                for key, value in details['positive_detail'].items():
                    if key != 'protein_rule_applied':  # Ignorer l'indicateur de règle
                        # Formatter le nom du critère et afficher les points
                        st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                # Vérifier si la règle spéciale des protéines a été appliquée
                if details['positive_detail'].get('protein_rule_applied', False):
                    st.write("⚠️ Règle protéines appliquée")  # Avertissement visuel
                # Afficher le total des points positifs en gras
                st.write(f"**Total positif: {details['positive_points']} pts**")

def display_electre_result(result: Dict[str, Any], title: str = "Résultat ELECTRE TRI"):
    """Affiche le résultat de la classification ELECTRE TRI."""
    # Afficher le titre de la section
    st.subheader(title)
    
    # Dictionnaire d'association entre classes ELECTRE et emojis colorés
    class_colors = {
        "A'": '🟢', "B'": '🟡', "C'": '🟠', "D'": '🔴', "E'": '⚫'
    }
    # Récupérer l'emoji correspondant à la classe (blanc par défaut)
    color = class_colors.get(result['class'], '⚪')
    # Afficher la classe assignée avec son emoji coloré
    st.metric("Classe ELECTRE TRI", f"{color} {result['class']}")
    
    # Section extensible pour les détails de classification (si disponibles)  
    if 'credibilities' in result:
        with st.expander("Indices de crédibilité"):
            # Parcourir et afficher tous les indices de crédibilité par profil
            for profile, credibility in result['credibilities'].items():
                st.write(f"- {profile}: {credibility}")
            # Afficher le seuil lambda utilisé pour la classification
            st.write(f"Seuil lambda: {result.get('lambda', 0.7)}")

def convert_units_if_needed(energy_value: float, is_kcal: bool, salt_value: float, is_salt: bool) -> tuple:
    """Convertit les unités si nécessaire."""
    # Gestion de la conversion d'énergie
    if is_kcal:
        # Convertir les kcal en kJ (facteur de conversion officiel)
        energy_kj = energy_value * 4.184
    else:
        # Garder la valeur en kJ si déjà dans la bonne unité
        energy_kj = energy_value
    
    # Gestion de la conversion sel/sodium
    if is_salt and salt_value > 0:
        # Convertir le sel (g) en sodium (mg) : facteur de conversion 400
        sodium_mg = salt_value * 400
    else:
        # Garder la valeur en mg de sodium si déjà dans la bonne unité
        sodium_mg = salt_value
    
    # Retourner les valeurs converties en tuple
    return energy_kj, sodium_mg

# Fonction principale de l'interface utilisateur
def main():
    # Afficher le titre principal avec style CSS personnalisé
    st.markdown('<h1 class="main-header">🥗 Nutri-Score & ELECTRE TRI</h1>', 
                unsafe_allow_html=True)  # Permettre l'injection HTML pour le style
    
    # Afficher la description du prototype
    st.markdown("""
    **Prototype d'évaluation nutritionnelle** combinant le calcul officiel du Nutri-Score 
    et la méthode ELECTRE TRI pour le classement des produits alimentaires.
    """)
    
    # Créer une sidebar pour les paramètres globaux de l'application
    with st.sidebar:
        # Titre de la section de configuration
        st.header("⚙️ Configuration")
        
        # Charger la configuration ELECTRE en utilisant la fonction avec cache
        electre_config = load_electre_config()
        
        # Vérifier si la configuration a été chargée avec succès
        if electre_config:
            # Afficher un message de succès
            st.success("Configuration ELECTRE chargée ✅")
            
            # Ajouter un séparateur visuel
            st.divider()
            # Sous-titre pour les paramètres ELECTRE TRI
            st.subheader("🎛️ Paramètres ELECTRE TRI")
            
            # Widget de sélection pour la variante d'ELECTRE TRI
            variant = st.selectbox(
                "Variante ELECTRE TRI",                    # Label du widget
                ["pessimistic", "optimistic"],            # Options disponibles
                index=0,                                   # Sélection par défaut (pessimistic)
                help="Pessimiste: classement prudent, Optimiste: classement favorable"  # Aide contextuelle
            )
            
            # Widget slider pour ajuster le paramètre lambda
            current_lambda = electre_config.get('lambda', 0.7)  # Valeur par défaut depuis config
            lambda_val = st.slider(
                "Seuil lambda",                           # Label du slider
                min_value=0.5,                            # Valeur minimale
                max_value=1.0,                            # Valeur maximale
                value=current_lambda,                     # Valeur par défaut
                step=0.05,                                # Pas d'incrémentation
                help="Seuil de concordance pour le surclassement"  # Aide contextuelle
            )
            
            # Section pour la modification des poids des critères
            st.write("**Configuration des poids:**")
            # Checkbox pour activer/désactiver la personnalisation des poids
            use_custom_weights = st.checkbox(
                "Modifier les poids des critères",        # Label de la checkbox
                value=False,                              # État par défaut (non cochée)
                help="Cocher pour personnaliser les poids (seront normalisés automatiquement)"  # Aide
            )
            
            # Initialiser la variable des poids personnalisés
            custom_weights = None
            # Si l'utilisateur veut personnaliser les poids
            if use_custom_weights:
                # Créer une section extensible pour ajuster les poids (ouverte par défaut)
                with st.expander("⚖️ Ajuster les poids des critères", expanded=True):
                    # Note explicative sur la normalisation automatique
                    st.write("*Les poids seront normalisés automatiquement pour sommer à 1*")
                    
                    # Récupérer les poids par défaut de la configuration
                    weights = electre_config.get('weights', {})
                    # Initialiser le dictionnaire des poids personnalisés
                    custom_weights = {}
                    
                    # Classer les critères par type pour une meilleure organisation
                    cost_criteria = ['energy_100g', 'saturated_fat_100g', 'sugars_100g', 'sodium_100g', 'additives_count']      # Critères à minimiser
                    benefit_criteria = ['proteins_100g', 'fiber_100g', 'fruits_veg_nuts_percent']  # Critères à maximiser
                    
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
    
    # Créer les onglets principaux de l'application
    tab1, tab2 = st.tabs(["🧮 Calcul Unitaire", "📊 Traitement Dataset"])
    
    # PREMIER ONGLET : Calcul pour un produit individuel
    with tab1:
        # Titre de la section de calcul unitaire
        st.header("Calcul individuel Nutri-Score & ELECTRE TRI")
        
        # Créer deux colonnes : large pour la saisie, étroite pour l'état
        col1, col2 = st.columns([2, 1])
        
        # Colonne principale : Saisie des données nutritionnelles
        with col1:
            # Sous-titre pour la section de saisie
            st.subheader("💊 Saisie des composantes nutritionnelles")
            
            # Diviser en deux sous-colonnes pour organiser les éléments défavorables/favorables
            col_a, col_b = st.columns(2)
            
            # Sous-colonne A : Éléments nutritionnels défavorables (à limiter)
            with col_a:
                st.write("**Éléments à limiter:**")
                
                # Widget pour choisir l'unité d'énergie (avec conversion automatique)
                energy_unit = st.selectbox("Unité d'énergie", ["kJ", "kcal"], index=0)
                # Widget de saisie numérique pour l'énergie
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
            
            # Nouveau champ pour le nombre d'additifs (critère à minimiser)
            st.write("**Additifs:**")
            additives = st.number_input("Nombre d'additifs", min_value=0, max_value=50, value=0, step=1, 
                                       help="Nombre d'additifs présents dans le produit (critère à minimiser pour ELECTRE TRI)")
            
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
        
        # Section des boutons de calcul - deux colonnes pour les deux méthodes
        col1, col2 = st.columns(2)
        
        # Colonne 1 : Bouton de calcul Nutri-Score
        with col1:
            # Bouton principal pour lancer le calcul Nutri-Score
            if st.button("🧮 Calculer Nutri-Score", type="primary"):
                # Bloc try-except pour gérer les erreurs de calcul
                try:
                    # Appeler la fonction de calcul avec toutes les valeurs saisies
                    nutri_result = compute_nutriscore_single(
                        energy_kj=energy_kj,              # Énergie convertie en kJ
                        saturated_fat_g=sat_fat,          # Acides gras saturés
                        sugars_g=sugars,                  # Sucres
                        sodium_mg=sodium_mg,              # Sodium converti en mg
                        fiber_g=fiber,                    # Fibres
                        protein_g=proteins,               # Protéines
                        fruits_veg_nuts_percent=fruits_veg # Pourcentage fruits/légumes/noix
                    )
                    
                    # Afficher un message de succès
                    st.success("Calcul Nutri-Score terminé !")
                    # Appeler la fonction d'affichage des résultats
                    display_nutriscore_result(nutri_result)
                    
                except Exception as e:
                    # Afficher un message d'erreur en cas de problème
                    st.error(f"Erreur calcul Nutri-Score : {e}")
        
        # Colonne 2 : Bouton de classification ELECTRE TRI
        with col2:
            # Bouton secondaire pour ELECTRE TRI (actif seulement si config disponible)
            if st.button("🎯 Classer avec ELECTRE TRI", type="secondary") and electre_config:
                # Bloc try-except pour gérer les erreurs de classification
                try:
                    # Préparer le dictionnaire des valeurs de critères au format ELECTRE
                    criteria_values = {
                        'energy_100g': energy_kj,                 # Énergie en kJ
                        'saturated_fat_100g': sat_fat,            # AG saturés en g
                        'sugars_100g': sugars,                    # Sucres en g
                        'sodium_100g': sodium_mg,                 # Sodium en mg
                        'proteins_100g': proteins,                # Protéines en g
                        'fiber_100g': fiber,                      # Fibres en g
                        'fruits_veg_nuts_percent': fruits_veg,    # % fruits/légumes/noix
                        'additives_count': additives              # Nombre d'additifs (saisi par l'utilisateur)
                    }
                    
                    # Appeler la fonction de classification avec les paramètres personnalisés
                    electre_result = classify_single_product(
                        criteria_values,                # Dictionnaire des critères
                        variant=variant,                # Variante choisie (pessimistic/optimistic)
                        lambda_threshold=lambda_val,    # Seuil lambda personnalisé
                        custom_weights=custom_weights   # Poids personnalisés (si définis)
                    )
                    
                    # Afficher les messages de succès avec détails
                    st.success(f"Classification ELECTRE TRI ({variant}) terminée !")
                    st.info(f"Paramètres utilisés: Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}")
                    # Appeler la fonction d'affichage des résultats ELECTRE
                    display_electre_result(electre_result)
                    
                except Exception as e:
                    # Afficher un message d'erreur en cas de problème
                    st.error(f"Erreur classification ELECTRE TRI : {e}")
    
    # DEUXIÈME ONGLET : Traitement de datasets complets
    with tab2:
        # Titre de la section de traitement de dataset
        st.header("Traitement du dataset et comparaison")
        
        # Sous-section pour le chargement des données
        st.subheader("📁 Chargement des données")
        
        # Widget radio pour choisir la source des données
        data_source = st.radio(
            "Source des données:",                                              # Label du choix
            ["Fichier par défaut (data/produits.xlsx)", "Charger un autre fichier"]  # Options disponibles
        )
        
        # Initialiser le chemin par défaut vers le fichier Excel
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
        
        # Gestion de l'état des données chargées via Streamlit session state
        if 'dataset_loaded' not in st.session_state:
            # Initialiser les variables d'état si elles n'existent pas
            st.session_state.dataset_loaded = False     # État de chargement des données
            st.session_state.df_processed = None        # DataFrame traité
        
        # Créer trois colonnes pour organiser les boutons (chargement et actions)
        col1, col2, col3 = st.columns([1, 1, 2])
        
        # Colonne 1 : Bouton de chargement des données
        with col1:
            # Bouton principal pour charger et traiter le fichier Excel
            if st.button("📊 Charger l'Excel", type="primary"):
                # Afficher un spinner pendant le chargement
                with st.spinner("Chargement et normalisation des données..."):
                    # Appeler la fonction de chargement et traitement (avec cache)
                    df_processed, mapping, quality, norm_report, error = load_and_process_data(excel_path)
                
                # Vérifier si une erreur s'est produite
                if error:
                    # Afficher le message d'erreur
                    st.error(f"Erreur de chargement : {error}")
                else:
                    # Mettre à jour l'état de session avec les données chargées
                    st.session_state.dataset_loaded = True          # Marquer comme chargé
                    st.session_state.df_processed = df_processed    # Sauvegarder le DataFrame
                    
                    # Afficher un message de succès avec le nombre de produits
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
            
            # Colonne 1 : Bouton de calcul Nutri-Score sur le dataset
            with col1:
                # Bouton pour recalculer le Nutri-Score sur tout le dataset
                if st.button("🧮 Recalculer Nutri-Score", type="secondary"):
                    # Afficher un spinner pendant le calcul
                    with st.spinner("Calcul du Nutri-Score sur le dataset..."):
                        # Bloc try-except pour gérer les erreurs
                        try:
                            # Appliquer le calcul Nutri-Score à tout le DataFrame
                            df_with_nutri = apply_nutriscore(df)
                            # Mettre à jour le DataFrame dans l'état de session
                            st.session_state.df_processed = df_with_nutri
                            
                            # Calculer les statistiques de distribution des labels
                            label_dist = df_with_nutri['ns_label_calc'].value_counts()
                            
                            # Afficher le message de succès
                            st.success("✅ Nutri-Score calculé !")
                            
                            # Afficher la distribution des labels calculés
                            st.write("**Distribution des labels:**")
                            for label, count in label_dist.items():
                                st.write(f"- {label}: {count}")
                            
                        except Exception as e:
                            # Afficher l'erreur en cas de problème
                            st.error(f"Erreur calcul Nutri-Score : {e}")
            
            # Colonne 2 : Bouton de classification ELECTRE TRI sur le dataset
            with col2:
                # Bouton pour appliquer ELECTRE TRI à tout le dataset
                if st.button("🎯 Appliquer ELECTRE TRI", type="secondary"):
                    # Vérifier que la configuration ELECTRE est disponible
                    if not electre_config:
                        st.error("Configuration ELECTRE non disponible")
                    else:
                        # Afficher un spinner avec la variante utilisée
                        with st.spinner(f"Classification ELECTRE TRI ({variant})..."):
                            # Bloc try-except pour gérer les erreurs
                            try:
                                # Appliquer ELECTRE TRI avec les paramètres de la sidebar
                                classifications = electre_sorting(
                                    df,                             # DataFrame à classifier
                                    variant=variant,                # Variante choisie
                                    lambda_threshold=lambda_val,    # Seuil lambda personnalisé
                                    custom_weights=custom_weights   # Poids personnalisés
                                )
                                
                                # Créer une copie du DataFrame et ajouter les classifications
                                df_with_electre = df.copy()
                                df_with_electre['electre_cat'] = classifications
                                # Mettre à jour l'état de session
                                st.session_state.df_processed = df_with_electre
                                
                                # Calculer les statistiques de distribution des classes
                                class_dist = classifications.value_counts()
                                
                                # Afficher les messages de succès et d'information
                                st.success(f"✅ ELECTRE TRI ({variant}) appliqué !")
                                st.info(f"Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}")
                                
                                # Afficher la distribution des classes
                                st.write("**Distribution des classes:**")
                                for classe, count in class_dist.items():
                                    st.write(f"- {classe}: {count}")
                                
                            except Exception as e:
                                # Afficher l'erreur et la stack trace complète
                                st.error(f"Erreur ELECTRE TRI : {e}")
                                import traceback
                                st.code(traceback.format_exc())  # Afficher la trace d'erreur complète
            
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
                
                # Générer les données CSV pour le téléchargement
                csv_data = st.session_state.df_processed.to_csv(index=False)
                
                # Widget de téléchargement pour exporter les résultats
                st.download_button(
                    label="📥 Télécharger CSV",      # Texte du bouton
                    data=csv_data,                   # Données à télécharger
                    file_name="dataset_traite.csv", # Nom du fichier suggéré
                    mime="text/csv"                  # Type MIME du fichier
                )

# Point d'entrée principal de l'application
if __name__ == "__main__":
    # Lancer l'interface utilisateur Streamlit
    main()