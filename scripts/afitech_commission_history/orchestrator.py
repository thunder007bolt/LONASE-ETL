# sys.path.append("C:\ETL") # À supprimer - non portable et mauvaise pratique

from base.orchestrator import Orchestrator # Classe de base refactorisée
# Importer les classes spécifiques des composants, pas les fonctions "run_*"
from scripts.afitech_commission_history.extract import ExtractAfitechCommissionHistory
from scripts.afitech_commission_history.transform import AfitechCommissionHistoryTransformer
from scripts.afitech_commission_history.load import AfitechCommissionHistoryLoader

# Assurer le chargement des variables d'environnement si ce script est un point d'entrée
# from load_env import load_env # load_env() est appelé par config_utils
# load_env()

JOB_NAME = "afitech_commission_history"

def run_afitech_commission_history_orchestrator():
    """
    Orchestre le pipeline ETL complet pour Afitech Commission History.
    """
    orchestrator_instance_name = f"{JOB_NAME}_pipeline"
    orchestrator_log_path = f"logs/orchestrator_{JOB_NAME}.log"

    # 1. Initialisation de l'Extracteur
    # Mapping des variables d'environnement pour les secrets de l'extracteur Afitech
    extract_env_mapping = {
        "AFITECH_LOGIN_USERNAME": "AFITECH_LOGIN_USERNAME",
        "AFITECH_LOGIN_PASSWORD": "AFITECH_LOGIN_PASSWORD",
        "AFITECH_GET_OTP_URL": "AFITECH_GET_OTP_URL"
    }
    extractor = ExtractAfitechCommissionHistory(env_vars_mapping=extract_env_mapping)

    # 2. Initialisation du Transformateur
    transformer = AfitechCommissionHistoryTransformer()

    # 3. Initialisation du Chargeur
    # Le Loader pour Afitech Commission History gère son propre mapping d'env pour la BD dans son __init__.
    loader = AfitechCommissionHistoryLoader()

    # Création de l'instance de l'Orchestrator de base
    pipeline_orchestrator = Orchestrator(
        orchestrator_name=orchestrator_instance_name,
        log_file_path=orchestrator_log_path,
        extractor_component=extractor,
        transformer_component=transformer,
        loader_component=loader
    )

    # Exécution du pipeline
    try:
        pipeline_orchestrator.run()
    except Exception as e:
        # L'Orchestrator de base logue déjà l'erreur.
        # Un log supplémentaire ici peut être redondant mais confirme l'échec au niveau du script.
        print(f"ERREUR CRITIQUE: L'orchestrateur du pipeline {JOB_NAME} a échoué. Détails: {e}")
        # exit(1) # Optionnel: sortir avec un code d'erreur si c'est un script batch.

if __name__ == "__main__":
    # S'assurer que les variables d'environnement sont chargées si ce script est le point d'entrée principal.
    # Normalement, config_utils (utilisé par les classes de base) s'en charge déjà au premier import.
    # Mais par précaution si ce script est exécuté de manière isolée avant tout autre import de config_utils :
    from load_env import load_env
    load_env()

    run_afitech_commission_history_orchestrator()