"""Affichage de la barre latérale de configuration."""

from typing import Any, Dict, Optional, Tuple

import streamlit as st

from app.ui.cache_utils import load_electre_config


def render_sidebar() -> Tuple[Dict[str, Any], str, float, Optional[Dict[str, float]]]:
    """Affiche la configuration dans la barre latérale et retourne les paramètres sélectionnés."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        electre_config = load_electre_config()

        if electre_config:
            st.success("Configuration ELECTRE chargée ✅")
            st.divider()
            st.subheader("🎛️ Paramètres ELECTRE TRI")

            variant = st.selectbox(
                "Variante ELECTRE TRI",
                ["pessimistic", "optimistic"],
                index=0,
                help="Pessimiste: classement prudent, Optimiste: classement favorable",
            )

            current_lambda = electre_config.get("lambda", 0.7)
            lambda_val = st.slider(
                "Seuil lambda",
                min_value=0.5,
                max_value=1.0,
                value=current_lambda,
                step=0.05,
                help="Seuil de concordance pour le surclassement",
            )

            st.write("**Configuration des poids:**")
            use_custom_weights = st.checkbox(
                "Modifier les poids des critères",
                value=False,
                help="Cocher pour personnaliser les poids (seront normalisés automatiquement)",
            )

            custom_weights: Optional[Dict[str, float]] = None

            if use_custom_weights:
                with st.expander("⚖️ Ajuster les poids des critères", expanded=True):
                    st.write("*Les poids seront normalisés automatiquement pour sommer à 1*")

                    weights = electre_config.get("weights", {})
                    custom_weights = {}

                    cost_criteria = [
                        "energy_100g",
                        "saturated_fat_100g",
                        "sugars_100g",
                        "sodium_100g",
                        "additives_count",
                    ]
                    benefit_criteria = [
                        "proteins_100g",
                        "fiber_100g",
                        "fruits_veg_nuts_percent",
                    ]

                    st.write("**🔴 Éléments à limiter:**")
                    for criterion in cost_criteria:
                        if criterion in weights:
                            label = (
                                criterion.replace("_", " ")
                                .replace("100g", "(100g)")
                                .title()
                            )
                            custom_weights[criterion] = st.slider(
                                label,
                                min_value=0.01,
                                max_value=1.0,
                                value=float(weights[criterion]),
                                step=0.01,
                                key=f"weight_{criterion}",
                            )

                    st.write("**🟢 Éléments favorables:**")
                    for criterion in benefit_criteria:
                        if criterion in weights:
                            label = (
                                criterion.replace("_", " ")
                                .replace("100g", "(100g)")
                                .replace("percent", "(%)")
                                .title()
                            )
                            custom_weights[criterion] = st.slider(
                                label,
                                min_value=0.01,
                                max_value=1.0,
                                value=float(weights[criterion]),
                                step=0.01,
                                key=f"weight_{criterion}",
                            )

                    if custom_weights:
                        total_weight = sum(custom_weights.values())
                        st.write("**Poids normalisés (aperçu):**")
                        for criterion, weight in custom_weights.items():
                            normalized = weight / total_weight
                            st.write(f"- {criterion.replace('_', ' ')}: {normalized:.3f}")
            else:
                with st.expander("📊 Poids actuels des critères"):
                    weights = electre_config.get("weights", {})
                    for criterion, weight in weights.items():
                        st.write(f"- {criterion.replace('_', ' ').title()}: {weight:.3f}")
        else:
            st.error("Configuration ELECTRE non disponible ❌")
            variant = "pessimistic"
            lambda_val = 0.7
            custom_weights = None

    return electre_config, variant, lambda_val, custom_weights
