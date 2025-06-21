from os import getenv
from dotenv import load_dotenv
from pathlib import Path
import logging

# Configuration du logging pour ce module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Déterminer le chemin du projet de manière dynamique
# Ce script (load_env.py) est à la racine du projet.
# Donc, Path(__file__).resolve().parent est la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"

def load_env(env_path: Path = DEFAULT_ENV_PATH) -> bool:
    """
    Charge les variables d'environnement à partir du fichier .env spécifié.

    Args:
        env_path (Path): Le chemin vers le fichier .env. Par défaut, .env à la racine du projet.

    Returns:
        bool: True si le chargement a réussi (ou si le fichier .env n'existe pas mais ce n'est pas une erreur fatale ici),
              False si une erreur s'est produite lors du chargement.
    """
    if not env_path.exists():
        logger.warning(f"Le fichier .env n'a pas été trouvé à l'emplacement : {env_path}")
        # Décider si c'est une erreur fatale ou non. Pour l'instant, on continue.
        # On pourrait vouloir lever une exception ici dans certains cas.
        return True # Ou False, selon la politique de gestion d'erreur souhaitée

    logger.info(f"Chargement des variables d'environnement depuis : {env_path}")
    load_dotenv(dotenv_path=env_path)

    # Vérification optionnelle d'une variable spécifique pour confirmer le chargement
    # (remplace "GET_ENV_SUCCESS" qui était une approche un peu ad-hoc)
    # Il est préférable de vérifier les variables spécifiques là où elles sont utilisées.
    # Si une variable critique est attendue, elle devrait être vérifiée dans get_config ou à l'utilisation.
    project_path_env = getenv("PROJECT_PATH")
    if project_path_env:
        logger.info("Variables d'environnement chargées avec succès.")
        # Valider que PROJECT_PATH correspond bien à la racine détectée peut être une bonne idée
        if Path(project_path_env).resolve() != PROJECT_ROOT:
            logger.warning(f"La variable d'environnement PROJECT_PATH ({project_path_env}) "
                           f"ne correspond pas à la racine détectée du projet ({PROJECT_ROOT}). "
                           "Cela pourrait causer des problèmes.")
    else:
        # Si PROJECT_PATH n'est pas défini après le chargement, c'est un problème.
        logger.error("La variable d'environnement PROJECT_PATH n'est pas définie dans le fichier .env. "
                       "Cette variable est cruciale pour la configuration des chemins.")
        # On pourrait ici définir PROJECT_PATH sur PROJECT_ROOT par défaut si non défini dans .env
        # import os
        # os.environ["PROJECT_PATH"] = str(PROJECT_ROOT)
        # logger.info(f"PROJECT_PATH a été défini par défaut sur : {PROJECT_ROOT}")
        # Ou lever une erreur :
        # raise EnvironmentError("PROJECT_PATH n'est pas défini dans le fichier .env")
        return False # Indique un problème de configuration

    return True

if __name__ == "__main__":
    if load_env():
        # Exemple d'utilisation des variables chargées
        project_path = getenv("PROJECT_PATH")
        data_path = getenv("DATA_PATH")
        download_path = getenv("DOWNLOAD_PATH")
        print(f"PROJECT_PATH: {project_path}")
        print(f"DATA_PATH: {data_path}")
        print(f"DOWNLOAD_PATH: {download_path}")
    else:
        print("Erreur lors du chargement de la configuration de l'environnement.")