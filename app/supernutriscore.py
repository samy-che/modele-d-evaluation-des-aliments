import pandas as pd

def compute_supernutriscore(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- 1) Récupérer les sorties existantes ---
    nutri = df.get("ns_label_calc")
    electre = df.get("electre_cat")
    greenscore = df.get("green_score")  # si tu l’as déjà
    bio = df.get("is_bio")  # bool ou 0/1

    # --- 2) Appliquer tes règles de SuperNutri-score ---
    def classify(row):
        n = row["ns_label_calc"]
        e = row["electre_cat"]
        g = row.get("green_score", None)
        b = row.get("is_bio", 0)

        # exemple de règles
        score = 0

        # Nutri-Score
        score += {"A":5, "B":4, "C":3, "D":2, "E":1}.get(n, 0)

        # ELECTRE TRI
        score += {"A'":5, "B'":4, "C'":3, "D'":2, "E'":1}.get(e, 0)

        # GreenScore (1 à 5)
        if g:
            score += g

        # BIO bonus
        if b == 1:
            score += 1

        # décision finale
        if score >= 14:
            return "A"
        elif score >= 11:
            return "B"
        elif score >= 8:
            return "C"
        elif score >= 5:
            return "D"
        else:
            return "E"

    df["supernutri_score"] = df.apply(classify, axis=1)
    return df


def compute_supernutriscore_row(row):
    """
    Calcule le Super Nutri-Score pondéré pour une ligne du dataset.
    Suppose que :
    - ns_label_calc est déjà calculé
    - electre_cat est déjà calculé
    - bio (0 ou 1) existe dans le fichier
    """

    nutri_label = row.get("ns_label_calc", None)
    electre_label = row.get("electre_cat", None)
    bio_value = row.get("bio", 0)

    # 1) Conversion en points
    nutri_points = {"A": 2, "B": 1, "C": 0, "D": -1, "E": -2}.get(nutri_label, 0)
    electre_points = {"A'": 2, "B'": 1, "C'": 0, "D'": -1, "E'": -2}.get(electre_label, 0)
    bio_points = 1 if bio_value == 1 else 0

    # 2) Score pondéré
    score = (
        0.50 * nutri_points
        + 0.35 * electre_points
        + 0.15 * bio_points
    )

    # 3) Catégorie finale
    if score >= 1.5:
        label = "A"
    elif score >= 0.5:
        label = "B"
    elif score >= -0.5:
        label = "C"
    elif score >= -1.5:
        label = "D"
    else:
        label = "E"

    return score, label
