"""Module d'interface utilisateur Streamlit refactorisée."""

from .setup import setup_page_and_logging
from .sidebar import render_sidebar
from .components import display_nutriscore_result, display_electre_result

__all__ = [
    'setup_page_and_logging',
    'render_sidebar',
    'display_nutriscore_result',
    'display_electre_result',
]
