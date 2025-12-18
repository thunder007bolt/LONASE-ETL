import sys
sys.path.append("C:\ETL")

from base.logger import Logger
from extract import run_honore_gaming as extract
from transform_new import run_honore_gaming_new_transformer as transform
from load import run_honore_gaming_loader as load

def orchestrator():
    logger = Logger(log_file="logs/orchestrator_honore_gaming.log").get_logger()
    try:
        logger.info("Lancement de l'orchestrateur...")
        extract()
        transform()
        load()
        logger.info("Orchestrateur terminé avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'orchestrateur : {e}")
        raise e

if __name__ == "__main__":
  orchestrator()