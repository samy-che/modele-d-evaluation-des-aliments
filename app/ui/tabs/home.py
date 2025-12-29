"""Onglet Accueil de l'interface Streamlit."""

import streamlit as st


def render_home_tab() -> None:
    """Affiche l'onglet d'accueil avec présentation du projet."""
    
    # Banner de bienvenue
    st.markdown("""
    <div class="welcome-banner">
        <h2>👋 Bienvenue</h2>
        <p>Cette application est un <strong>prototype d'évaluation nutritionnelle</strong> qui combine plusieurs 
        approches pour analyser et classer les produits alimentaires.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section des fonctionnalités avec cards
    st.markdown('<h2 class="section-header">🎯 Nos Méthodes d\'Évaluation</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card nutriscore">
            <h3>🥗 Nutri-Score</h3>
            <p>Calcul du <strong>Nutri-Score officiel</strong> selon l'algorithme 
            de Santé Publique France.</p>
            <br>
            <p>✓ Score de A à E<br>
            ✓ Valeurs nutritionnelles<br>
            ✓ Méthode internationale</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card electre">
            <h3>⚖️ ELECTRE TRI</h3>
            <p>Méthode d'aide à la décision multicritère 
            pour un classement plus nuancé.</p>
            <br>
            <p>✓ Analyse multicritère<br>
            ✓ Seuils personnalisables<br>
            ✓ Classification robuste</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card super">
            <h3>🌟 Super Nutri-Score</h3>
            <p>Combinaison innovante des deux approches 
            pour une évaluation enrichie.</p>
            <br>
            <p>✓ Synthèse des méthodes<br>
            ✓ Vision globale<br>
            ✓ Score environnemental</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section Comment utiliser
    st.markdown('<h2 class="section-header">📖 Comment utiliser l\'application ?</h2>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown("""
        ### 🧮 Calcul Unitaire
        
        Entrez manuellement les valeurs nutritionnelles d'un produit pour obtenir :
        
        - 🔢 Son **Nutri-Score** calculé
        - 🎯 Sa classification **ELECTRE TRI**
        - ⭐ Le **Super Nutri-Score** combiné
        
        > 💡 *Idéal pour tester un produit spécifique*
        """)
    
    with col_right:
        st.markdown("""
        ### 📊 Traitement Dataset
        
        Chargez un fichier Excel ou utilisez l'API OpenFoodFacts pour :
        
        - 📈 Analyser un ensemble de produits
        - 🔄 Comparer les différentes méthodes
        - 💾 Exporter les résultats
        
        > 💡 *Idéal pour l'analyse en masse*
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section À propos
    with st.expander("ℹ️ À propos du projet", expanded=False):
        col_about1, col_about2, col_about3 = st.columns(3)
        
        with col_about1:
            st.markdown("""
            **📊 Sources de données**
            - Open Food Facts
            - Fichiers Excel personnalisés
            - API temps réel
            """)
        
        with col_about2:
            st.markdown("""
            **🔬 Méthodologies**
            - Nutri-Score (algorithme 2024)
            - ELECTRE TRI multicritère
            - Score environnemental
            """)
        
        with col_about3:
            st.markdown("""
            **💻 Technologies**
            - Python & Streamlit
            - Pandas & NumPy
            - Scikit-learn
            """)
