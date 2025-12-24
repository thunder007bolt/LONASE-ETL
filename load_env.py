from os import getenv
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """
    Charge les variables d'environnement depuis le fichier .env.
    Cherche le fichier .env dans le répertoire racine du projet.
    """
    # Trouver le répertoire racine du projet (parent du répertoire contenant ce fichier)
    project_root = Path(__file__).parent.resolve()
    env_file = project_root / '.env'
    
    load_dotenv(env_file)

    if getenv("GET_ENV_SUCCESS") == "success":
        print("Variables d'environement chargées avec succès")
    else:
        print("Une erreur s'est produite lors du chargement des variables d'environement")
DSD
if __name__ == "__main__":
    load_env()