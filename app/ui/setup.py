"""Configuration de l'interface Streamlit et du logging."""

import logging
from typing import Optional

import streamlit as st

CUSTOM_CSS = """
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
    
    /* Cards pour la page d'accueil */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        min-height: 280px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-card.nutriscore {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .feature-card.electre {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .feature-card.super {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .feature-card h3 {
        font-size: 1.8rem !important;
        margin-bottom: 1rem;
        color: white !important;
    }
    
    .feature-card p {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #1f77b4 0%, #2ecc71 100%);
        padding: 3rem 2rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .welcome-banner h2 {
        font-size: 2.5rem !important;
        margin-bottom: 1rem;
        color: white !important;
    }
    
    .welcome-banner p {
        font-size: 1.3rem;
        opacity: 0.95;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1.5rem 0;
    }
    
    /* Dataset page styles */
    .dataset-header {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .dataset-header h2 {
        color: white !important;
        margin: 0;
    }
</style>
"""

# JavaScript pour contrôler l'état de la sidebar selon l'onglet actif
SIDEBAR_CONTROL_JS = """
<script>
    (function() {
        // Fonction pour contrôler la sidebar et ajuster le layout
        function setSidebarState(expand) {
            var sidebarContent = window.parent.document.querySelector('section[data-testid="stSidebar"]');
            var mainBlock = window.parent.document.querySelector('section.main');
            var blockContainer = window.parent.document.querySelector('.block-container');
            
            if (sidebarContent) {
                if (expand) {
                    // Ouvrir la sidebar
                    sidebarContent.style.transform = 'translateX(0)';
                    sidebarContent.style.width = '';
                    sidebarContent.style.minWidth = '';
                    
                    // Remettre le contenu principal à sa taille normale
                    if (mainBlock) {
                        mainBlock.style.marginLeft = '';
                        mainBlock.style.width = '';
                        mainBlock.style.maxWidth = '';
                    }
                    if (blockContainer) {
                        blockContainer.style.maxWidth = '';
                        blockContainer.style.paddingLeft = '';
                        blockContainer.style.paddingRight = '';
                    }
                } else {
                    // Fermer la sidebar
                    sidebarContent.style.transform = 'translateX(-100%)';
                    sidebarContent.style.width = '0';
                    sidebarContent.style.minWidth = '0';
                    
                    // Élargir le contenu principal pour prendre tout l'espace
                    if (mainBlock) {
                        mainBlock.style.marginLeft = '0';
                        mainBlock.style.width = '100%';
                        mainBlock.style.maxWidth = '100%';
                    }
                    if (blockContainer) {
                        blockContainer.style.maxWidth = '100%';
                        blockContainer.style.paddingLeft = '3rem';
                        blockContainer.style.paddingRight = '3rem';
                    }
                }
                sidebarContent.style.transition = 'transform 0.3s ease, width 0.3s ease';
            }
        }
        
        // Fonction pour vérifier l'onglet actif
        function checkActiveTab() {
            var tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
            if (tabs.length > 0) {
                for (var i = 0; i < tabs.length; i++) {
                    if (tabs[i].getAttribute('aria-selected') === 'true') {
                        var tabText = tabs[i].innerText || tabs[i].textContent;
                        // Si c'est l'onglet "Calcul Unitaire", ouvrir la sidebar
                        if (tabText.includes('Calcul Unitaire')) {
                            setSidebarState(true);
                        } else {
                            // Sinon fermer la sidebar
                            setSidebarState(false);
                        }
                        break;
                    }
                }
            }
        }
        
        // Observer les changements d'onglet
        function observeTabs() {
            var tabList = window.parent.document.querySelector('[role="tablist"]');
            if (tabList) {
                // Vérifier l'état initial
                checkActiveTab();
                
                // Observer les clics sur les onglets
                tabList.addEventListener('click', function() {
                    setTimeout(checkActiveTab, 50);
                });
                
                // Observer les changements d'attributs
                var observer = new MutationObserver(function(mutations) {
                    checkActiveTab();
                });
                
                var tabs = tabList.querySelectorAll('button[data-baseweb="tab"]');
                tabs.forEach(function(tab) {
                    observer.observe(tab, { attributes: true, attributeFilter: ['aria-selected'] });
                });
            } else {
                // Réessayer si les onglets ne sont pas encore chargés
                setTimeout(observeTabs, 100);
            }
        }
        
        // Démarrer l'observation
        if (window.parent.document.readyState === 'complete') {
            observeTabs();
        } else {
            window.parent.addEventListener('load', observeTabs);
        }
        
        // Aussi observer immédiatement
        setTimeout(observeTabs, 200);
    })();
</script>
"""


def setup_sidebar_control():
    """Injecte le JavaScript pour contrôler la sidebar selon l'onglet actif."""
    st.components.v1.html(SIDEBAR_CONTROL_JS, height=0)


def collapse_sidebar():
    """Fonction legacy - maintenant gérée par setup_sidebar_control."""
    pass


def expand_sidebar():
    """Fonction legacy - maintenant gérée par setup_sidebar_control."""
    pass


def setup_page_and_logging(logger_name: Optional[str] = None) -> logging.Logger:
    """Configure la page Streamlit, le logging et applique le style personnalisé."""
    st.set_page_config(
        page_title="Nutri-Score & ELECTRE TRI",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(logger_name or __name__)

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    return logger
