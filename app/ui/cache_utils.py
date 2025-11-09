"""Fonctions avec mise en cache pour l'interface Streamlit."""

from typing import Any, Dict, Optional, Tuple

import streamlit as st
import yaml

from app.utils.paths import get_config_path
from app.io import load_data, ExcelDataLoader  # noqa: F401 utilisé pour compatibilité
from app.normalize import normalize_data


@st.cache_data
def load_electre_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Charge la configuration ELECTRE avec cache."""
    config_path = config_path or get_config_path("config/electre.yml")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:  # pragma: no cover - gestion d'erreur UI
        st.error(f"Erreur chargement configuration ELECTRE : {e}")
        return {}


@st.cache_data
def load_and_process_data(excel_path: str) -> Tuple[Any, Any, Any, Any, Optional[str]]:
    """Charge et traite les données avec cache."""
    try:
        df, mapping, quality = load_data(excel_path)
        df_normalized, norm_report = normalize_data(df)
        return df_normalized, mapping, quality, norm_report, None
    except Exception as e:  # pragma: no cover - gestion d'erreur UI
        return None, None, None, None, str(e)
