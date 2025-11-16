"""Onglet de traitement de dataset et comparaison des méthodes."""

import os
from typing import Any, Dict, Optional

import streamlit as st
import requests
import numpy as np


from app.electre_tri import electre_sorting
from app.eval import compare_nutriscore_electre
from app.nutriscore import apply_nutriscore
from app.nutriscore import apply_nutriscore_excel
from app.ui.cache_utils import load_and_process_data
from app.normalize import normalize_data


def render_dataset_tab(
    electre_config: Dict[str, Any],
    variant: str,
    lambda_val: float,
    custom_weights: Optional[Dict[str, float]],
) -> None:
    """Affiche le contenu de l'onglet de traitement de dataset."""
    st.header("Traitement du dataset et comparaison")

    st.subheader("📁 Chargement des données")

    data_source = st.radio(
        "Source des données:",
        ["Fichier par défaut (data/produits.xlsx)", "Charger un autre fichier", "🌐 API OpenFoodFacts"],
    )

    excel_path = "data/produits.xlsx"
    use_api = False

    if data_source == "Charger un autre fichier":
        uploaded_file = st.file_uploader(
            "Choisir un fichier Excel",
            type=["xlsx", "xls"],
            help="Le fichier doit contenir les colonnes nutritionnelles requises",
        )

        if uploaded_file:
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            excel_path = temp_path
    
    elif data_source == "🌐 API OpenFoodFacts":
        use_api = True
        st.info("📡 Récupération des données depuis OpenFoodFacts")
        
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            api_query = st.text_input("Recherche (optionnel)", placeholder="Ex: Nutella, Coca-Cola...")
            api_category = st.selectbox(
                "Catégorie",
                ["", "cereals", "yogurts", "cheeses", "chocolates", "beverages", "snacks"],
                help="Laisser vide pour toutes les catégories"
            )
        
        with col_api2:
            api_max_products = st.number_input("Nombre max de produits", min_value=10, max_value=500, value=100, step=10)
            api_country = st.selectbox("Pays", ["France", "World", "Belgium", "Switzerland"])
        
        # Stocker les paramètres API
        if 'api_params' not in st.session_state:
            st.session_state.api_params = {}
        
        st.session_state.api_params = {
            'query': api_query,
            'category': api_category if api_category else None,
            'max_products': api_max_products,
            'countries': api_country
        }

    if "dataset_loaded" not in st.session_state:
        st.session_state.dataset_loaded = False
        st.session_state.df_processed = None

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        button_label = "🌐 Charger depuis API" if use_api else "📊 Charger l'Excel"
        if st.button(button_label, type="primary"):
            if use_api:
                # Chargement depuis OpenFoodFacts API
                try:
                    from app.api_openfoodfacts import OpenFoodFactsAPI
                    
                    params = st.session_state.api_params
                    max_prod = params.get('max_products', 50)
                    
                    # Calculer temps estimé (~0.7s par produit)
                    estimated_time = int(max_prod * 0.7)
                    
                    info_placeholder = st.empty()
                    info_placeholder.info(f"🌐 Connexion à l'API OpenFoodFacts...")
                    
                    with st.spinner(f"Récupération de {max_prod} produits maximum..."):
                        api = OpenFoodFactsAPI()
                        df_raw = api.search_to_dataframe(
                            query=params.get('query', ''),
                            category=params.get('category'),
                            max_products=max_prod,
                            countries=params.get('countries', 'France')
                        )
                    
                    info_placeholder.empty()
                    
                    if df_raw.empty:
                        st.error("❌ Aucun produit trouvé avec ces critères. Essayez de modifier la catégorie ou la recherche.")
                    else:
                        # Normaliser les données
                        with st.spinner("Normalisation des données..."):
                            df_normalized, norm_report = normalize_data(df_raw)
                        
                        st.session_state.dataset_loaded = True
                        st.session_state.df_processed = df_normalized
                        
                        st.success(f"✅ {len(df_normalized)} produits récupérés depuis OpenFoodFacts !")
                        
                        with st.expander("📋 Rapport de récupération"):
                            st.write(f"**Produits bruts:** {len(df_raw)}")
                            st.write(f"**Après normalisation:** {len(df_normalized)}")
                            if norm_report.get('rows_removed', 0) > 0:
                                st.warning(f"⚠️ {norm_report['rows_removed']} produits supprimés (données manquantes)")
                            st.write(f"**Colonnes:** {', '.join(df_normalized.columns[:8])}...")
                
                except requests.exceptions.Timeout:
                    st.error("❌ Timeout: L'API met trop de temps à répondre. Réduisez le nombre de produits.")
                except Exception as e:
                    st.error(f"❌ Erreur API OpenFoodFacts: {e}")
                    with st.expander("Détails de l'erreur"):
                        import traceback
                        st.code(traceback.format_exc())
            else:
                # Chargement depuis fichier Excel
                with st.spinner("Chargement et normalisation des données..."):
                    df_processed, mapping, quality, norm_report, error = load_and_process_data(excel_path)

                if error:
                    st.error(f"Erreur de chargement : {error}")
                else:
                    st.session_state.dataset_loaded = True
                    st.session_state.df_processed = df_processed

                    st.success(f"✅ Données chargées : {len(df_processed)} produits")

                    with st.expander("Rapport de qualité des données"):
                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.write("**Mapping des colonnes:**")
                            for canonical, original in mapping.items():
                                st.write(f"- {canonical} ← {original}")

                        with col_b:
                            st.write("**Normalisation appliquée:**")
                            for step in norm_report.get("steps_applied", []):
                                st.write(f"✓ {step}")

                            if norm_report.get("rows_removed", 0) > 0:
                                st.warning(f"⚠️ {norm_report['rows_removed']} lignes supprimées")

    if st.session_state.dataset_loaded and st.session_state.df_processed is not None:
        df = st.session_state.df_processed

        st.divider()

        st.subheader("👁️ Aperçu des données")
        col1, col2 = st.columns([3, 1])

        with col1:
            st.dataframe(df.head(110), use_container_width=True)

        with col2:
            st.metric("Nombre de produits", len(df))
            nutritional_cols = ["energy_100g", "proteins_100g", "fiber_100g"]
            available_cols = [col for col in nutritional_cols if col in df.columns]
            st.metric("Colonnes nutritionnelles", len(available_cols))

        st.divider()

        st.subheader("🔄 Traitements")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🧮 Recalculer Nutri-Score", type="secondary"):
                with st.spinner("Calcul du Nutri-Score sur le dataset..."):
                    try:
                        # 🧮 1. Calcul du Nutri-Score
                        df_with_nutri = apply_nutriscore_excel(df)
                        st.session_state.df_processed = df_with_nutri

                        # ✅ 2. Comparaison avec Nutri-Score original (si présent)
                        if (
                            'ns_label_original' in df_with_nutri.columns and
                            'ns_label_calc' in df_with_nutri.columns and
                            'ns_score_original' in df_with_nutri.columns and
                            'ns_score_calc' in df_with_nutri.columns
                        ):
                            df_with_nutri['Comparaison_NS'] = np.where(
                                df_with_nutri['ns_label_original'] == df_with_nutri['ns_label_calc'],
                                '✅ Label identique',
                                '⚠️ Label différent'
                            )
                            df_with_nutri['Comparaison_Score'] = np.where(
                                df_with_nutri['ns_score_original'] == df_with_nutri['ns_score_calc'],
                                '✅ Score identique',
                                '⚠️ Score différent'
                            )

                        # 📊 3. Affichage global
                        label_dist = df_with_nutri["ns_label_calc"].value_counts()
                        st.success("✅ Nutri-Score recalculé avec succès !")

                        st.write("**Distribution des labels recalculés :**")
                        for label, count in label_dist.items():
                            st.write(f"- {label}: {count}")

                        # 🧾 4. Comparaison détaillée (produit par produit)
                        if {'produit', 'ns_label_original', 'ns_label_calc',
                            'ns_score_original', 'ns_score_calc',
                            'Comparaison_NS', 'Comparaison_Score'}.issubset(df_with_nutri.columns):

                            st.markdown("### 🔍 Comparaison détaillée (Original vs Recalculé)")

                            diff_df = df_with_nutri[
                                ['produit',
                                'ns_score_original', 'ns_score_calc', 'Comparaison_Score',
                                'ns_label_original', 'ns_label_calc', 'Comparaison_NS']
                            ].copy()

                            diff_only = diff_df[
                                (diff_df['Comparaison_NS'] != '✅ Label identique') |
                                (diff_df['Comparaison_Score'] != '✅ Score identique')
                            ]

                            if len(diff_only) > 0:
                                st.warning(f"⚠️ {len(diff_only)} produit(s) présentent des écarts entre les Nutri-Scores :")
                                st.dataframe(diff_only, use_container_width=True)
                            else:
                                st.success("✅ Tous les scores et labels Nutri-Score sont identiques.")

                            st.write("### 👁️ Aperçu global :")
                            st.dataframe(diff_df.head(30), use_container_width=True)

                        else:
                            st.info("ℹ️ Colonnes nécessaires à la comparaison manquantes (vérifie ton Excel).")

                    except Exception as e:
                        st.error(f"Erreur calcul Nutri-Score : {e}")
                        import traceback
                        st.code(traceback.format_exc())

        with col2:
            if st.button("🎯 Appliquer ELECTRE TRI", type="secondary"):
                if not electre_config:
                    st.error("Configuration ELECTRE non disponible")
                else:
                    with st.spinner(f"Classification ELECTRE TRI ({variant})..."):
                        try:
                            classifications = electre_sorting(
                                df,
                                variant=variant,
                                lambda_threshold=lambda_val,
                                custom_weights=custom_weights,
                            )

                            df_with_electre = df.copy()
                            df_with_electre["electre_cat"] = classifications
                            st.session_state.df_processed = df_with_electre

                            class_dist = classifications.value_counts()

                            st.success(f"✅ ELECTRE TRI ({variant}) appliqué !")
                            st.info(
                                f"Lambda = {lambda_val}, Poids personnalisés = {'Oui' if custom_weights else 'Non'}"
                            )

                            st.write("**Distribution des classes:**")
                            for classe, count in class_dist.items():
                                st.write(f"- {classe}: {count}")

                        except Exception as e:  # pragma: no cover - gestion d'erreur UI
                            st.error(f"Erreur ELECTRE TRI : {e}")
                            import traceback

                            st.code(traceback.format_exc())

        with col3:
            has_nutri = "ns_label_calc" in df.columns
            has_electre = "electre_cat" in df.columns

            if st.button(
                "📊 Comparer méthodes",
                type="primary",
                disabled=not (has_nutri and has_electre),
            ):
                with st.spinner("Génération de la comparaison..."):
                    try:
                        report = compare_nutriscore_electre(
                            df,
                            nutriscore_col="ns_label_calc",
                            electre_col="electre_cat",
                        )

                        st.success("✅ Comparaison terminée !")

                        metrics = report.get("metrics", {})
                        if metrics:
                            st.subheader("📈 Métriques de comparaison")

                            col_a, col_b, col_c, col_d = st.columns(4)

                            with col_a:
                                accuracy = metrics.get("accuracy", 0)
                                st.metric("Accuracy", f"{accuracy:.3f}")

                            with col_b:
                                f1_macro = metrics.get("f1_macro", 0)
                                st.metric("F1-Score Macro", f"{f1_macro:.3f}")

                            with col_c:
                                mae = metrics.get("mae_rank", 0)
                                st.metric("MAE (rang)", f"{mae:.3f}")

                            with col_d:
                                corr = metrics.get("spearman_correlation", 0)
                                st.metric("Corrélation", f"{corr:.3f}")

                            st.write("**Accuracy avec tolérance:**")
                            col_e, col_f = st.columns(2)

                            with col_e:
                                tol1 = metrics.get("accuracy_tolerance_1", 0)
                                st.write(f"±1 niveau: {tol1:.3f}")

                            with col_f:
                                tol2 = metrics.get("accuracy_tolerance_2", 0)
                                st.write(f"±2 niveaux: {tol2:.3f}")

                        # Affichage des visualisations
                        st.subheader("📊 Visualisations")
                        viz_col1, viz_col2 = st.columns(2)
                        
                        with viz_col1:
                            confusion_path = "outputs/reports/confusion_matrix.png"
                            if os.path.exists(confusion_path):
                                st.image(confusion_path, caption="Matrice de confusion", use_container_width=True)
                            else:
                                st.info("Matrice de confusion non disponible")
                        
                        with viz_col2:
                            metrics_path = "outputs/reports/metrics_comparison.png"
                            if os.path.exists(metrics_path):
                                st.image(metrics_path, caption="Comparaison des métriques", use_container_width=True)
                            else:
                                st.info("Graphique des métriques non disponible")

                        files = report.get("summary", {}).get("files_generated", {})
                        if files:
                            st.subheader("📁 Fichiers générés")
                            for file_type, file_path in files.items():
                                if os.path.exists(file_path):
                                    st.write(f"✅ {file_type}: `{file_path}`")
                                else:
                                    st.write(f"❌ {file_type}: `{file_path}` (non trouvé)")

                    except Exception as e:  # pragma: no cover - gestion d'erreur UI
                        st.error(f"Erreur comparaison : {e}")
                        import traceback

                        st.code(traceback.format_exc())

            if not (has_nutri and has_electre):
                st.info("💡 Calculez d'abord Nutri-Score et ELECTRE TRI")

        if st.session_state.df_processed is not None:
            st.divider()
            st.subheader("💾 Export des résultats")

            csv_data = st.session_state.df_processed.to_csv(index=False)

            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_data,
                file_name="dataset_traite.csv",
                mime="text/csv",
            )
