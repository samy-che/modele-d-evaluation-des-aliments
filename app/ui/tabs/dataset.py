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
    
    # En-tête stylisé
    st.markdown("""
    <div class="dataset-header">
        <h2>📊 Traitement du Dataset et Comparaison</h2>
        <p>Chargez vos données, appliquez les méthodes d'évaluation et comparez les résultats</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<h3 class="section-header">📁 Chargement des données</h3>', unsafe_allow_html=True)

    data_source = st.radio(
        "Source des données:",
        ["Fichier par défaut (data/produits.xlsx)", "Charger un autre fichier", "API OpenFoodFacts"],
        horizontal=True
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
    
    elif data_source == "API OpenFoodFacts":
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
        button_label = "Charger depuis API" if use_api else "Charger l'Excel"
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
                        st.error("Aucun produit trouvé avec ces critères. Essayez de modifier la catégorie ou la recherche.")
                    else:
                        # Normaliser les données
                        with st.spinner("Normalisation des données..."):
                            df_normalized, norm_report = normalize_data(df_raw)
                        
                        st.session_state.dataset_loaded = True
                        st.session_state.df_processed = df_normalized
                        
                        st.success(f"✅ {len(df_normalized)} produits récupérés depuis OpenFoodFacts !")
                        
                        with st.expander("Rapport de récupération"):
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

        st.subheader("Traitements")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(" Recalculer Nutri-Score", type="secondary"):
                with st.spinner("Calcul du Nutri-Score sur le dataset..."):
                    try:
                        #  1. Calcul du Nutri-Score
                        df_with_nutri = apply_nutriscore_excel(df)
                        st.session_state.df_processed = df_with_nutri

                        # 2. Comparaison avec Nutri-Score original (si présent)
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

                        #  3. Stocker les résultats pour affichage persistant
                        label_dist = df_with_nutri["ns_label_calc"].value_counts().to_dict()
                        
                        # Préparer le rapport de comparaison
                        nutri_result = {
                            "success": True,
                            "label_dist": label_dist,
                            "diff_df": None,
                            "diff_only": None,
                            "has_comparison": False
                        }
                        
                        #  4. Comparaison détaillée (produit par produit)
                        if {'produit', 'ns_label_original', 'ns_label_calc',
                            'ns_score_original', 'ns_score_calc',
                            'Comparaison_NS', 'Comparaison_Score'}.issubset(df_with_nutri.columns):

                            diff_df = df_with_nutri[
                                ['produit',
                                'ns_score_original', 'ns_score_calc', 'Comparaison_Score',
                                'ns_label_original', 'ns_label_calc', 'Comparaison_NS']
                            ].copy()

                            diff_only = diff_df[
                                (diff_df['Comparaison_NS'] != '✅ Label identique') |
                                (diff_df['Comparaison_Score'] != '✅ Score identique')
                            ]
                            
                            nutri_result["has_comparison"] = True
                            nutri_result["diff_df"] = diff_df
                            nutri_result["diff_only"] = diff_only
                        
                        st.session_state.nutri_result = nutri_result

                    except Exception as e:
                        st.session_state.nutri_result = {"success": False, "error": str(e)}
                        import traceback
                        st.session_state.nutri_result["traceback"] = traceback.format_exc()

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

                            class_dist = classifications.value_counts().to_dict()

                            # Stocker les résultats pour affichage persistant
                            st.session_state.electre_result = {
                                "success": True,
                                "variant": variant,
                                "lambda_val": lambda_val,
                                "custom_weights": custom_weights,
                                "class_dist": class_dist
                            }

                        except Exception as e:  # pragma: no cover - gestion d'erreur UI
                            st.session_state.electre_result = {"success": False, "error": str(e)}
                            import traceback
                            st.session_state.electre_result["traceback"] = traceback.format_exc()

        # Recharger df après les modifications potentielles
        df = st.session_state.df_processed
        
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
                            metrics_path = "outputs/reports/metrics_summary.png"
                            if os.path.exists(metrics_path):
                                st.image(metrics_path, caption="Résumé des métriques", use_container_width=True)
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
                st.info(" Calculez d'abord Nutri-Score et ELECTRE TRI")

        # === Affichage persistant des résultats Nutri-Score ===
        if "nutri_result" in st.session_state and st.session_state.nutri_result:
            result = st.session_state.nutri_result
            st.divider()
            st.subheader("🔢 Résultats Nutri-Score")
            
            if result.get("success"):
                st.success("✅ Nutri-Score recalculé avec succès !")
                
                st.write("**Distribution des labels recalculés :**")
                for label, count in result.get("label_dist", {}).items():
                    st.write(f"- {label}: {count}")
                
                if result.get("has_comparison"):
                    st.markdown("### 🔍 Comparaison détaillée (Original vs Recalculé)")
                    
                    diff_only = result.get("diff_only")
                    if diff_only is not None and len(diff_only) > 0:
                        st.warning(f"⚠️ {len(diff_only)} produit(s) présentent des écarts entre les Nutri-Scores :")
                        st.dataframe(diff_only, use_container_width=True)
                    else:
                        st.success("✅ Tous les scores et labels Nutri-Score sont identiques.")
                    
                    diff_df = result.get("diff_df")
                    if diff_df is not None:
                        st.write("### 👁️ Aperçu global :")
                        st.dataframe(diff_df.head(30), use_container_width=True)
                else:
                    st.info("Colonnes nécessaires à la comparaison manquantes (vérifie ton Excel).")
            else:
                st.error(f"Erreur calcul Nutri-Score : {result.get('error')}")
                if result.get("traceback"):
                    st.code(result.get("traceback"))

        # === Affichage persistant des résultats ELECTRE ===
        if "electre_result" in st.session_state and st.session_state.electre_result:
            result = st.session_state.electre_result
            st.divider()
            st.subheader("🎯 Résultats ELECTRE TRI")
            
            if result.get("success"):
                st.success(f"✅ ELECTRE TRI ({result.get('variant')}) appliqué !")
                st.info(
                    f"Lambda = {result.get('lambda_val')}, Poids personnalisés = {'Oui' if result.get('custom_weights') else 'Non'}"
                )
                
                st.write("**Distribution des classes:**")
                for classe, count in result.get("class_dist", {}).items():
                    st.write(f"- {classe}: {count}")
            else:
                st.error(f"Erreur ELECTRE TRI : {result.get('error')}")
                if result.get("traceback"):
                    st.code(result.get("traceback"))

        # === Bouton Super Nutri-Score ===
        st.divider()
        with col3:
            if st.button(" Calculer Super Nutri-Score", type="secondary"):
                try:
                    df_super = st.session_state.df_processed.copy()

                    # Vérifier colonne Bio
                    if "bio or no" in df_super.columns:
                        df_super["is_bio"] = (
                            df_super["bio or no"]
                            .fillna("Non")
                            .astype(str)
                            .str.strip()
                            .str.lower()
                            .map({
                                "oui": 1, "yes": 1, "true": 1, "1": 1, "Oui" : 1, "OUI" : 1, 
                                "non": 0, "no": 0, "false": 0, "0": 0, "Non" : 0, "NON" : 0
                            })
                            .fillna(0)
                            .astype(int)
                        )
                    else:
                        st.warning("⚠️ Colonne 'Bio or no' absente : bio mis à 0 pour tout le dataset.")
                        df_super["is_bio"] = 0

                    # Vérifier colonne Green-Score
                    if "green label" in df_super.columns:
                        df_super["green_points"] = df_super["green label"].astype(str).str.upper().map({
                            "A": 1, "B": 0.75, "C": 0.50, "D": 0.25, "E": 0
                        }).fillna(0)
                    else:
                        st.warning("⚠️ Colonne 'green_score' absente : Green-Score mis à 0.")
                        df_super["green_points"] = 0

                    # Colonnes obligatoires            "ns_label_calc",
                    required_cols = {"electre_cat", "is_bio", "green_points"}
                    missing = required_cols - set(df_super.columns)
                    if missing:
                        st.error(f"Colonnes manquantes pour SuperNutri-Score : {missing}")
                        return

                    #Mapping Electre
                    electre_map = {"A'": 1, "B'": 0.75, "C'": 0.5, "D'": 0.25, "E'": 1}

                    df_super["electre_points"] = df_super["electre_cat"].map(electre_map).fillna(0)

                    # Pondérations
                 
                    w_electre = 0.6
                    w_bio = 0.1
                    w_green = 0.3

                    df_super["super_score"] = (
                        df_super["electre_points"] * w_electre +
                        df_super["is_bio"] * w_bio +
                        df_super["green_points"] * w_green
                    )

                    # Classification finale
                    def score_to_letter(s):
                        if s >= 0.80: return "A'"
                        if s >= 0.60: return "B'"
                        if s >= 0.40: return "C'"
                        if s >= 0.20: return "D'"
                        return "E'"
                    

                    df_super["super_label"] = df_super["super_score"].apply(score_to_letter)

                    st.session_state.df_processed = df_super

                    st.success("🌟 Super Nutri-Score (pondéré + Green-Score) calculé avec succès !")
                    st.dataframe(
                        df_super[["produit", "ns_label_calc", "electre_cat",
                                "is_bio", "green_points", "super_score", "super_label"]].head(20),
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Erreur Super Nutri-Score : {e}")
                    import traceback
                    st.code(traceback.format_exc())

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
