"""Onglet de calcul individuel Nutri-Score & ELECTRE TRI."""

from typing import Any, Dict, Optional

import streamlit as st

from app.electre_tri import classify_single_product
from app.nutriscore import compute_nutriscore_single
from app.ui.components import (
    convert_units_if_needed,
    display_electre_result,
    display_nutriscore_result,
)


def render_unitary_tab(
    electre_config: Dict[str, Any],
    variant: str,
    lambda_val: float,
    custom_weights: Optional[Dict[str, float]],
) -> None:
    """Affiche le contenu de l'onglet de calcul unitaire."""
    st.header("Calcul individuel Nutri-Score & ELECTRE TRI")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💊 Saisie des composantes nutritionnelles")

        col_a, col_b = st.columns(2)

        with col_a:
            st.write("**Éléments à limiter:**")

            energy_unit = st.selectbox("Unité d'énergie", ["kJ", "kcal"], index=0)
            energy_val = st.number_input(
                f"Énergie ({energy_unit})",
                min_value=0.0,
                value=1500.0,
                step=10.0,
            )

            sat_fat = st.number_input(
                "Acides gras saturés (g)",
                min_value=0.0,
                value=3.0,
                step=0.1,
            )

            sugars = st.number_input(
                "Sucres (g)",
                min_value=0.0,
                value=10.0,
                step=0.5,
            )

            sodium_unit = st.selectbox("Unité sodium/sel", ["Sodium (mg)", "Sel (g)"], index=0)
            sodium_val = st.number_input(
                sodium_unit,
                min_value=0.0,
                value=200.0 if "mg" in sodium_unit else 0.5,
                step=10.0 if "mg" in sodium_unit else 0.1,
            )

        with col_b:
            st.write("**Éléments favorables:**")

            proteins = st.number_input(
                "Protéines (g)",
                min_value=0.0,
                value=8.0,
                step=0.5,
            )

            fiber = st.number_input(
                "Fibres (g)",
                min_value=0.0,
                value=2.0,
                step=0.1,
            )

            fruits_veg = st.number_input(
                "Fruits/légumes/noix (%)",
                min_value=0.0,
                max_value=100.0,
                value=30.0,
                step=5.0,
            )

        st.write("**Additifs:**")
        additives = st.number_input(
            "Nombre d'additifs",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
            help="Nombre d'additifs présents dans le produit (critère à minimiser pour ELECTRE TRI)",
        )

        is_kcal = energy_unit == "kcal"
        is_salt = "Sel" in sodium_unit

        energy_kj, sodium_mg = convert_units_if_needed(
            energy_val,
            is_kcal,
            sodium_val,
            is_salt,
        )

        if is_kcal or is_salt:
            st.info(
                f"**Valeurs converties:** Énergie = {energy_kj:.1f} kJ, Sodium = {sodium_mg:.1f} mg"
            )

    with col2:
        st.subheader("📊 État de la configuration")

        if electre_config:
            st.success("✅ Configuration ELECTRE chargée")
            st.info(
                f"""
                **Paramètres actuels (sidebar):**
                - Variante: {variant}
                - Lambda: {lambda_val}
                - Poids personnalisés: {'✅ Oui' if custom_weights else '❌ Non'}
                """
            )

            if custom_weights:
                total_weight = sum(custom_weights.values())
                with st.expander("Poids personnalisés"):
                    for criterion, weight in custom_weights.items():
                        normalized = weight / total_weight
                        st.write(f"- {criterion.replace('_', ' ')}: {normalized:.3f}")
        else:
            st.error("❌ Configuration ELECTRE non disponible")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧮 Calculer Nutri-Score", type="primary"):
            try:
                nutri_result = compute_nutriscore_single(
                    energy_kj=energy_kj,
                    saturated_fat_g=sat_fat,
                    sugars_g=sugars,
                    sodium_mg_or_salt_g=sodium_mg,
                    fiber_g=fiber,
                    protein_g=proteins,
                    fruits_veg_nuts_percent=fruits_veg,
                )

                st.success("Calcul Nutri-Score terminé !")
                display_nutriscore_result(nutri_result)

            except Exception as e:  # pragma: no cover - gestion d'erreur UI
                st.error(f"Erreur calcul Nutri-Score : {e}")

    with col2:
        if st.button("🎯 Classer avec ELECTRE TRI", type="secondary") and electre_config:
            try:
                criteria_values = {
                    "energy_100g": energy_kj,
                    "saturated_fat_100g": sat_fat,
                    "sugars_100g": sugars,
                    "sodium_100g": sodium_mg,
                    "proteins_100g": proteins,
                    "fiber_100g": fiber,
                    "fruits_veg_nuts_percent": fruits_veg,
                    "additives_count": additives,
                }

                electre_result = classify_single_product(
                    criteria_values,
                    variant=variant,
                    lambda_threshold=lambda_val,
                    custom_weights=custom_weights,
                )

                st.success(f"Classification ELECTRE TRI ({variant}) terminée !")
                st.info(
                    f"Paramètres utilisés: Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}"
                )
                display_electre_result(electre_result)

            except Exception as e:  # pragma: no cover - gestion d'erreur UI
                st.error(f"Erreur classification ELECTRE TRI : {e}")
