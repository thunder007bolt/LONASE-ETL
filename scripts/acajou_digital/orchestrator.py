# Le sys.path.append est une mauvaise pratique et devrait être évité.
# La structure du projet et PYTHONPATH devraient permettre les imports corrects.
# Si ce script est exécuté depuis la racine du projet, les imports relatifs ou absolus (depuis la racine)
# devraient fonctionner. Ex: from scripts.acajou_digital.extract import ...
# Ou si les modules base et utils sont bien dans PYTHONPATH.
# Pour l'instant, on suppose que l'environnement d'exécution gère cela.
# import sys
# sys.path.append("C:\ETL") # A supprimer

from base.orchestrator import Orchestrator # Importer la classe Orchestrator refactorisée
# Importer les classes spécifiques d'extracteur, transformateur, chargeur
# et non plus les fonctions run_*
from scripts.acajou_digital.extract import ExtractAcajouDigital # La classe, pas la fonction run_
from scripts.acajou_digital.transform import AcajouDigitalTransformer # La classe
from scripts.acajou_digital.load import AcajouDigitalLoader # La classe

# Importer load_env pour s'assurer que les variables d'environnement sont chargées
# Ceci est crucial si ce script est le point d'entrée principal et que config_utils n'a pas encore été importé ailleurs.
# Cependant, les classes de base (via config_utils) devraient déjà appeler load_env.
# Redonder ici peut être sûr si load_env est idempotent.
# from load_env import load_env
# load_env() # Assurer le chargement des variables d'environnement

JOB_NAME = "acajou_digital"

def run_acajou_digital_orchestrator():
    """
    Orchestre le pipeline ETL complet pour Acajou Digital.
    Instancie les composants (Extracteur, Transformateur, Chargeur) et les passe à l'Orchestrator de base.
    """

    # Nom de l'orchestrateur, peut être utilisé pour le logging spécifique à cet orchestrateur.
    orchestrator_instance_name = f"{JOB_NAME}_pipeline"

    # Chemin du fichier de log pour cet orchestrateur spécifique.
    # La classe Orchestrator de base a un chemin par défaut, mais on peut le surcharger.
    orchestrator_log_path = f"logs/orchestrator_{JOB_NAME}.log"

    # Initialisation des composants
    # 1. Extracteur
    # Le mapping des variables d'environnement pour les secrets de l'extracteur
    extract_env_mapping = {
        "ACAJOU_DIGITAL_LOGIN_USERNAME": "ACAJOU_DIGITAL_LOGIN_USERNAME",
        "ACAJOU_DIGITAL_LOGIN_PASSWORD": "ACAJOU_DIGITAL_LOGIN_PASSWORD"
    }
    extractor = ExtractAcajouDigital(ftp_env_vars_mapping=extract_env_mapping) # Le nom du param est générique

    # 2. Transformateur
    transformer = AcajouDigitalTransformer()

    # 3. Chargeur
    # Le mapping des variables d'environnement pour les secrets de la BD du chargeur
    load_db_env_mapping = {
        'SQL_SERVER_HOST': 'SQL_SERVER_HOST',
        'SQL_SERVER_TEMPDB_NAME': 'SQL_SERVER_TEMPDB_NAME',
        'SQL_SERVER_TEMPDB_USERNAME': 'SQL_SERVER_TEMPDB_USERNAME',
        'SQL_SERVER_TEMPDB_PASSWORD': 'SQL_SERVER_TEMPDB_PASSWORD'
    }
    # Note: AcajouDigitalLoader __init__ ne prend pas db_env_vars_mapping directement.
    # Il faudra ajuster AcajouDigitalLoader ou la manière dont il récupère sa config de BD.
    # Pour l'instant, on suppose qu'il est correctement configuré en interne ou que
    # la classe Loader de base le gère via get_loading_configurations.
    # Revoyons le constructeur de AcajouDigitalLoader: il appelle super() avec db_env_vars_mapping. C'est bon.
    loader = AcajouDigitalLoader() # Il prend les infos de mapping en interne via son constructeur.

    # Création de l'instance de l'Orchestrator de base
    pipeline_orchestrator = Orchestrator(
        orchestrator_name=orchestrator_instance_name,
        log_file_path=orchestrator_log_path,
        extractor_component=extractor,
        transformer_component=transformer,
        loader_component=loader
    )

    # Exécution du pipeline
    # La méthode run de l'Orchestrator de base gère le logging et l'exécution séquentielle.
    try:
        pipeline_orchestrator.run()
    except Exception as e:
        # Le logger de l'Orchestrator de base devrait déjà avoir loggué l'erreur.
        # On peut ajouter un log ici si ce script est le point d'entrée et qu'on veut
        # s'assurer qu'une trace de l'échec global est visible facilement.
        # Utiliser un print ou un logger basique si le logger de l'orchestrateur n'est pas dispo.
        print(f"ERREUR CRITIQUE: L'orchestrateur du pipeline {JOB_NAME} a échoué. Détails: {e}")
        # Optionnel: exit(1) si c'est un script stand-alone.

if __name__ == "__main__":
    # Assurez-vous que load_env.py est appelé si ce script est un point d'entrée
    # et que les variables d'environnement ne sont pas déjà chargées.
    # (Déjà commenté ci-dessus, mais important à noter)
    from load_env import load_env # S'assurer que c'est accessible
    load_env()

    run_acajou_digital_orchestrator()