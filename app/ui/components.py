"""Composants d'affichage et fonctions utilitaires pour l'interface Streamlit."""

from typing import Any, Dict, Tuple

import streamlit as st


def display_nutriscore_result(result: Dict[str, Any], title: str = "Résultat Nutri-Score") -> None:
    """Affiche le résultat du calcul Nutri-Score."""
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Score Nutri-Score", result["score"])

    with col2:
        label_colors = {
            "A": "🟢",
            "B": "🟡",
            "C": "🟠",
            "D": "🔴",
            "E": "⚫",
        }
        color = label_colors.get(result["label"], "⚪")
        st.metric("Label Nutri-Score", f"{color} {result['label']}")

    if "details" in result:
        with st.expander("Détails du calcul"):
            details = result["details"]
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Points négatifs :**")
                for key, value in details["negative_detail"].items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                st.write(f"**Total négatif: {details['negative_points']} pts**")

            with col2:
                st.write("**Points positifs :**")
                for key, value in details["positive_detail"].items():
                    if key != "protein_rule_applied":
                        st.write(f"- {key.replace('_', ' ').title()}: {value} pts")
                if details["positive_detail"].get("protein_rule_applied", False):
                    st.write("⚠️ Règle protéines appliquée")
                st.write(f"**Total positif: {details['positive_points']} pts**")


def display_electre_result(result: Dict[str, Any], title: str = "Résultat ELECTRE TRI") -> None:
    """Affiche le résultat de la classification ELECTRE TRI."""
    st.subheader(title)

    class_colors = {
        "A'": "🟢",
        "B'": "🟡",
        "C'": "🟠",
        "D'": "🔴",
        "E'": "⚫",
    }
    color = class_colors.get(result["class"], "⚪")
    st.metric("Classe ELECTRE TRI", f"{color} {result['class']}")

    if "credibilities" in result:
        with st.expander("Indices de crédibilité"):
            for profile, credibility in result["credibilities"].items():
                st.write(f"- {profile}: {credibility}")
            st.write(f"Seuil lambda: {result.get('lambda', 0.7)}")


def convert_units_if_needed(
    energy_value: float,
    is_kcal: bool,
    salt_value: float,
    is_salt: bool,
) -> Tuple[float, float]:
    """Convertit les unités si nécessaire."""
    if is_kcal:
        energy_kj = energy_value * 4.184
    else:
        energy_kj = energy_value

    if is_salt and salt_value > 0:
        sodium_mg = salt_value * 400
    else:
        sodium_mg = salt_value

    return energy_kj, sodium_mg
