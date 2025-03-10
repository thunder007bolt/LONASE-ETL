from os import getenv
from dotenv import load_dotenv

def load_env():
    load_dotenv(r"C:\ETL\.env")

    if getenv("GET_ENV_SUCCESS") == "success":
        print("Variables d'environement chargées avec succès")
    else:
        print("Une erreur s'est produite lors du chargement des variables d'environement")

if __name__ == "__main__":
    load_env()