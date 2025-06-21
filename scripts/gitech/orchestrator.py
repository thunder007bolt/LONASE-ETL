# sys.path.append("C:\ETL") # À supprimer

from base.orchestrator import Orchestrator
from scripts.gitech.extract import ExtractGitech
from scripts.gitech.transform import GitechTransformer
from scripts.gitech.load import GitechLoader

# from load_env import load_env # Géré par config_utils
# load_env()

JOB_NAME = "gitech"

def run_gitech_orchestrator(): # Nom de fonction mis à jour
    """
    Orchestre le pipeline ETL complet pour Gitech.
    """
    orchestrator_instance_name = f"{JOB_NAME}_pipeline"
    orchestrator_log_path = f"logs/orchestrator_{JOB_NAME}.log"

    # 1. Extracteur
    extract_env_mapping = {
        "GITECH_LOGIN_USERNAME": "GITECH_LOGIN_USERNAME",
        "GITECH_LOGIN_PASSWORD": "GITECH_LOGIN_PASSWORD"
    }
    extractor = ExtractGitech(env_vars_mapping=extract_env_mapping)

    # 2. Transformateur
    transformer = GitechTransformer()

    # 3. Chargeur
    loader = GitechLoader() # Gère son propre mapping d'env DB en interne

    # Création de l'Orchestrator
    pipeline_orchestrator = Orchestrator(
        orchestrator_name=orchestrator_instance_name,
        log_file_path=orchestrator_log_path,
        extractor_component=extractor,
        transformer_component=transformer,
        loader_component=loader
    )

    try:
        pipeline_orchestrator.run()
    except Exception as e:
        print(f"ERREUR CRITIQUE: Pipeline {JOB_NAME} a échoué. Détails: {e}")
        # exit(1) # Optionnel

if __name__ == "__main__":
    from load_env import load_env
    load_env() # S'assurer que les variables d'env sont chargées si exécuté directement

    run_gitech_orchestrator() # Nom de fonction mis à jour