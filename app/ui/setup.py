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
</style>
"""


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
