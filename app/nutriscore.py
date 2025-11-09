#===========================================
#Module NutriScore – Version Officielle 2025
#===========================================

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



DEFAULT_POINT_TABLES = {

    
    # Points défavorables (négatifs)
    # Énergie (kJ/100g)
    "energy": [
        (335, 0), (670, 1), (1005, 2), (1340, 3), (1675, 4),
        (2010, 5), (2345, 6), (2680, 7), (3015, 8), (3350, 9),
        (float("inf"), 10)
    ],

    # Acides gras saturés (g/100g)
    "saturated_fat": [
        (1.0, 0), (2.0, 1), (3.0, 2), (4.0, 3), (5.0, 4),
        (6.0, 5), (7.0, 6), (8.0, 7), (9.0, 8), (10.0, 9),
        (float("inf"), 10)
    ],

    # Sucres (g/100g)
    "sugars": [
        (3.4, 0), (6.8, 1), (10.0, 2), (14.0, 3), (17.0, 4),
        (20.0, 5), (24.0, 6), (27.0, 7), (31.0, 8), (34.0, 9),
        (37.0, 10), (41.0, 11), (44.0, 12), (48.0, 13), (51.0, 14),
        (float("inf"), 15)
    ],

    # Sel (g/100g)
    "salt": [
        (0.2, 0), (0.4, 1), (0.6, 2), (0.8, 3), (1.0, 4),
        (1.2, 5), (1.4, 6), (1.6, 7), (1.8, 8), (2.0, 9),
        (2.2, 10), (2.4, 11), (2.6, 12), (2.8, 13), (3.0, 14),
        (3.2, 15), (3.4, 16), (3.6, 17), (3.8, 18), (4.0, 19),
        (float("inf"), 20)
    ],


    # Points favorables (positifs)
    # Protéines (g/100g)
    "protein": [
        (2.4, 0), (4.8, 1), (7.2, 2), (9.6, 3),
        (12.0, 4), (14.0, 5), (17.0, 6),
        (float("inf"), 7)
    ],

    # Fibres (g/100g)
    "fiber": [
        (3.0, 0), (4.1, 1), (5.2, 2), (6.3, 3),
        (7.4, 4), (float("inf"), 5)
    ],

    # Fruits, légumes, légumineuses (%)
    "fruits_veg": [
        (40, 0), (60, 1), (80, 2), (float("inf"), 5)
    ]
}

# Seuils score -> label (identiques aux précédentes versions)
DEFAULT_THRESHOLDS = {
    "solid": [(0, "A"), (2, "B"), (10, "C"), (18, "D"), (float("inf"), "E")],
    "beverage": [(1, "A"), (5, "B"), (9, "C"), (13, "D"), (float("inf"), "E")]
}



def _get_points_from_table(value: float, table: list) -> int:
    #Retourne les points associes à une valeur selon le tableau fourni.
    if pd.isna(value):
        return 0
    for threshold, pts in table:
        if value <= threshold:
            return int(pts)
    return int(table[-1][1])



def convert_to_salt_g(value: float) -> float:
    # Conversion automatiquement sodium (mg) ou sel (g).
    if pd.isna(value):
        return 0.0
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v > 5:
        return v / 400.0
    return v


# Classe principale
class NutriScoreCalculator:


    def __init__(self,
                 point_tables: Optional[Dict[str, list]] = None,
                 thresholds: Optional[Dict[str, list]] = None):
        self.tables = point_tables if point_tables else DEFAULT_POINT_TABLES
        self.thresholds = thresholds if thresholds else DEFAULT_THRESHOLDS



    # Étape 1 : Points négatifs
    def compute_negative_points(self,
                                energy_kj: float,
                                saturated_fat_g: float,
                                sugars_g: float,
                                sodium_or_salt_value: float) -> Tuple[int, Dict]:
        #Calcule les points négatifs (énergie, SFA, sucres, sel).
        
        detail = {}

        energy_pts = _get_points_from_table(energy_kj, self.tables["energy"])
        sfa_pts = _get_points_from_table(saturated_fat_g, self.tables["saturated_fat"])
        sugar_pts = _get_points_from_table(sugars_g, self.tables["sugars"])

        # conversion sodium/sel
        salt_g = convert_to_salt_g(sodium_or_salt_value)
        salt_pts = _get_points_from_table(salt_g, self.tables["salt"])

        detail.update({
            "energy_points": energy_pts,
            "saturated_fat_points": sfa_pts,
            "sugars_points": sugar_pts,
            "salt_g": salt_g,
            "salt_points": salt_pts
        })

        total = energy_pts + sfa_pts + sugar_pts + salt_pts
        return total, detail



    # Étape 2 : Points positifs
    def compute_positive_points(self,
                                fiber_g: float,
                                protein_g: float,
                                fruits_veg_percent: float,
                                negative_points: int,
                                category: str = "general") -> Tuple[int, Dict]:
        """Calcule les points positifs avec la règle des protéines."""
        detail = {}
        fiber_pts = _get_points_from_table(fiber_g, self.tables["fiber"])
        protein_pts = _get_points_from_table(protein_g, self.tables["protein"])
        fruits_pts = _get_points_from_table(fruits_veg_percent, self.tables["fruits_veg"])

        # Règle protéines : si points négatifs ≥ 11 et fruits < 80 %, ne pas compter les protéines
        if negative_points >= 11 and (fruits_veg_percent < 80 or pd.isna(fruits_veg_percent)):
            if category == "cheese":
                detail["protein_rule_applied"] = False
            else:
                detail["protein_rule_applied"] = True
                protein_pts = 0
        else:
            detail["protein_rule_applied"] = False

        detail.update({
            "fiber_points": fiber_pts,
            "protein_points": protein_pts,
            "fruits_veg_points": fruits_pts
        })

        total = fiber_pts + protein_pts + fruits_pts
        return total, detail


    # Étape 3 : Score final + label
    def compute_score_and_label(self,
                                energy_kj: float,
                                saturated_fat_g: float,
                                sugars_g: float,
                                sodium_or_salt_value: float,
                                fiber_g: float,
                                protein_g: float,
                                fruits_veg_percent: float,
                                category: str = "general") -> Tuple[int, str, Dict]:

        neg_pts, neg_detail = self.compute_negative_points(
            energy_kj, saturated_fat_g, sugars_g, sodium_or_salt_value
        )
        pos_pts, pos_detail = self.compute_positive_points(
            fiber_g, protein_g, fruits_veg_percent, neg_pts, category
        )

        final_score = neg_pts - pos_pts
        thresholds = self.thresholds["beverage"] if category == "beverage" else self.thresholds["solid"]
        label = self.score_to_label(final_score, thresholds)

        details = {
            "negative_points": neg_pts,
            "positive_points": pos_pts,
            "final_score": final_score,
            "negative_detail": neg_detail,
            "positive_detail": pos_detail,
            "category": category
        }
        return final_score, label, details



    @staticmethod
    def score_to_label(score: int, thresholds: list) -> str:
        """Convertit un score numérique en label A–E."""
        for thr, lab in thresholds:
            if score <= thr:
                return lab
        return "E"



    # Étape 4 : Application à DataFrame
    def apply_to_dataframe(self, df: pd.DataFrame,
                           colmap: Optional[Dict[str, str]] = None,
                           default_category: str = "general") -> pd.DataFrame:
        #Applique le calcul à un DataFrame
        default_map = {
            "energy": "energy_100g",
            "saturated_fat": "saturated_fat_100g",
            "sugars": "sugars_100g",
            "salt": "sodium_100g",  # g/100g
            "fiber": "fiber_100g",
            "protein": "proteins_100g",
            "fruits_veg": "fruits_veg_nuts_percent",
            "category": None
        }
        if colmap:
            default_map.update(colmap)

        df_out = df.copy()

        def _compute_row(row):
            try:
                score, label, details = self.compute_score_and_label(
                    energy_kj=row.get(default_map["energy"], np.nan),
                    saturated_fat_g=row.get(default_map["saturated_fat"], np.nan),
                    sugars_g=row.get(default_map["sugars"], np.nan),
                    sodium_or_salt_value=row.get(default_map["salt"], np.nan),
                    fiber_g=row.get(default_map["fiber"], np.nan),
                    protein_g=row.get(default_map["protein"], np.nan),
                    fruits_veg_percent=row.get(default_map["fruits_veg"], np.nan),
                    category=row.get(default_map["category"], default_category)
                )
                return pd.Series({
                    "ns_score_calc": score,
                    "ns_label_calc": label,
                    "ns_calculation_details": details
                })
            except Exception as e:
                logger.error(f"Erreur ligne : {e}")
                return pd.Series({
                    "ns_score_calc": np.nan,
                    "ns_label_calc": "ERROR",
                    "ns_calculation_details": {"error": str(e)}
                })

        results = df_out.apply(_compute_row, axis=1)
        df_out = pd.concat([df_out, results], axis=1)
        
        # Supprimer ns_calculation_details pour éviter les problèmes de groupby
        if "ns_calculation_details" in df_out.columns:
            df_out = df_out.drop(columns=["ns_calculation_details"])
        
        return df_out

# Compatibilite Streamlit (fonctions simplifiées)

_default_calc = NutriScoreCalculator()


def compute_nutriscore_single(
    energy_kj: float = 0,
    saturated_fat_g: float = 0,
    sugars_g: float = 0,
    sodium_mg_or_salt_g: float = 0,
    fiber_g: float = 0,
    protein_g: float = 0,
    fruits_veg_nuts_percent: float = 0,
    category: str = "general"
) -> dict:
    #Fonction simplifiée compatible Streamlit (calcul unitaire)
    score, label, details = _default_calc.compute_score_and_label(
        energy_kj, saturated_fat_g, sugars_g, sodium_mg_or_salt_g,
        fiber_g, protein_g, fruits_veg_nuts_percent, category
    )
    return {"score": score, "label": label, "details": details}




# Cas Excel (nouvelle fonction adaptée) 
def compute_nutriscore_from_excel_row(row):

    # Récupération sécurisée
    energy = row.get("energy_100g", np.nan)
    sodium = row.get("sodium_100g", np.nan)

    # Conversion énergie
    #if not pd.isna(energy) and energy < 500:  # valeur en kcal
     #   energy = energy * 4.184  # conversion en kJ

    # Conversion sodium
    #if not pd.isna(sodium) and sodium < 10:  # valeur en g de sel
        #sodium = sodium * 400  # conversion en mg sodium

    return compute_nutriscore_single(
        energy_kj=energy,
        saturated_fat_g=row.get("saturated_fat_100g", np.nan),
        sugars_g=row.get("sugars_100g", np.nan),
        sodium_mg_or_salt_g=sodium,
        fiber_g=row.get("fiber_100g", np.nan),
        protein_g=row.get("proteins_100g", np.nan),
        fruits_veg_nuts_percent=row.get("fruits_veg_nuts_percent", np.nan)
    )


def apply_nutriscore(df: pd.DataFrame, category_col: str = None) -> pd.DataFrame:
    #Fonction compatible Streamlit (calcul dataset).
    if category_col and category_col in df.columns:
        return _default_calc.apply_to_dataframe(df, colmap={"category": category_col})
    else:
        return _default_calc.apply_to_dataframe(df)


#  Fonction batch pour Excel
def apply_nutriscore_excel(df):
    # Applique le calcul Nutri-Score sur tout un DataFrame Excel.
    
    df = df.copy()
    results = df.apply(lambda row: compute_nutriscore_from_excel_row(row), axis=1)

    df["ns_score_calc"] = results.apply(lambda r: r["score"])
    df["ns_label_calc"] = results.apply(lambda r: r["label"])
    
    # Supprimer la colonne ns_calculation_details si elle existe (cause des problèmes de groupby)
    if "ns_calculation_details" in df.columns:
        df = df.drop(columns=["ns_calculation_details"])

    return df
