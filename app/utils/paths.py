from pathlib import Path

def get_project_root() -> Path:
    """
    Renvoie le chemin absolu du dossier racine du projet.
    Suppose que ce script se trouve dans utils/, donc le root = parent de ce dossier.
    """
    return Path(__file__).resolve().parent.parent


def get_config_path(filename: str) -> Path:
    """
    Renvoie un chemin valide et universel vers un fichier de configuration.
    Teste plusieurs emplacements possibles pour compatibilité multi-environnement.
    
    Args:
        filename (str): chemin relatif du fichier (ex: "config/electre.yml" ou "config/columns.yml")
    """
    root = get_project_root()

    possible_paths = [
        root / filename,            # Projet lancé depuis la racine
        root.parent / filename,     # Projet lancé depuis un sous-dossier
        Path(filename),             # Chemin direct
        Path("../") / filename,     # Cas Streamlit ou notebook
    ]

    for path in possible_paths:
        if path.exists():
            return path.resolve()

    raise FileNotFoundError(
        f"❌ Fichier introuvable : {filename}\n"
        f"Chemins testés :\n" + "\n".join(str(p.resolve()) for p in possible_paths)
    )


# Variables globales (si tu veux les importer directement)
CONFIG_ELECTRE_PATH = get_config_path("config/electre.yml")
CONFIG_COLUMNS_PATH = get_config_path("config/columns.yml")
