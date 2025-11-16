"""Interface Streamlit pour Nutri-Score / ELECTRE TRI."""

import streamlit as st
import sys
from pathlib import Path


#streamlit run c:/Users/alila/Desktop/Projet_transparence/modele-d-evaluation-des-aliments/app/ui_streamlit.py

current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

try:
    from app.ui.setup import setup_page_and_logging
    from app.ui.sidebar import render_sidebar
    from app.ui.tabs.dataset import render_dataset_tab
    from app.ui.tabs.unitary import render_unitary_tab
except ImportError as e:
    st.error(f"Erreur d'import des modules : {e}")
    st.stop()


logger = setup_page_and_logging(__name__)


def main() -> None:
    """Point d'entrée principal de l'interface utilisateur."""
    st.markdown('<h1 class="main-header">🥗 Nutri-Score & ELECTRE TRI</h1>', unsafe_allow_html=True)
    st.markdown(
        """
    **Prototype d'évaluation nutritionnelle** combinant le calcul officiel du Nutri-Score 
    et la méthode ELECTRE TRI pour le classement des produits alimentaires.
    """
    )

    electre_config, variant, lambda_val, custom_weights = render_sidebar()

    tab1, tab2 = st.tabs(["🧮 Calcul Unitaire", "📊 Traitement Dataset"])

    with tab1:
        render_unitary_tab(electre_config, variant, lambda_val, custom_weights)

    with tab2:
        render_dataset_tab(electre_config, variant, lambda_val, custom_weights)


if __name__ == "__main__":
    main()