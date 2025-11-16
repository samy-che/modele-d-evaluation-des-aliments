"""Fonctions avec mise en cache pour l'interface Streamlit."""

from typing import Any, Dict, Optional, Tuple

import streamlit as st
import yaml
import pandas as pd
import numpy as np

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
def _norm(s: str) -> str:
    if s is None:
        return ""
    return (
        str(s).strip().lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ù", "u")
        .replace("û", "u")
        .replace("ç", "c")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("\u00a0", " ")
    )


@st.cache_data
def load_and_process_data(excel_path: str) -> tuple:
    """
    - Lit l'Excel
    - Normalise les en-têtes (minuscules, sans accents, apostrophes)
    - Renomme vers les colonnes attendues par le calcul
    - Caste en numérique
    """
    import re
    try:
        df_raw = pd.read_excel(excel_path, dtype=str, engine="openpyxl")

        # 1) Normaliser entêtes
        df_raw.columns = [_norm(c) for c in df_raw.columns]

        # 2) Mapping normalisé -> colonnes cibles
        column_mapping_norm = {
            "produit": "produit",
            "valeur energetique (kj)": "energy_100g",
            "quantite acides gras satures (g)": "saturated_fat_100g",
            "quantite de sucres (g)": "sugars_100g",
            "quantite de sodium (mg/g)": "sodium_100g",
            "quantite de proteines (g)": "proteins_100g",
            "quantite de fibres (g)": "fiber_100g",
            "teneur en fruits/legumes/fruits a coques": "fruits_veg_nuts_percent",
            "score issue de nutri score": "ns_score_original",
            "label nutri score": "ns_label_original",
            "nombre d'aditife": "additives_count",
        }

        df_raw.rename(columns={k: v for k, v in column_mapping_norm.items() if k in df_raw.columns},
                      inplace=True)

        # 3) Conversion numérique stricte
        numeric_cols = [
            "energy_100g", "saturated_fat_100g", "sugars_100g",
            "sodium_100g", "fiber_100g", "proteins_100g",
            "fruits_veg_nuts_percent", "ns_score_original"
        ]
        for col in numeric_cols:
            if col in df_raw.columns:
                df_raw[col] = (df_raw[col].astype(str)
                               .str.replace(",", ".", regex=False)
                               .str.replace(r"[^0-9.\-Ee]", "", regex=True)
                               .apply(lambda x: np.nan if x == "" else float(x)))

        mapping = {c: c for c in df_raw.columns}
        quality = {"rows": len(df_raw), "cols": len(df_raw.columns)}
        norm_report = {"steps_applied": ["normalize headers", "rename columns", "numeric cast"]}

        return df_raw, mapping, quality, norm_report, None

    except Exception as e:
        st.error(f"Erreur lecture Excel : {e}")
        import traceback; st.code(traceback.format_exc())
        return None, None, None, None, str(e)

