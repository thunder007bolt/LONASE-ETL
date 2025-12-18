import sys
sys.path.append("C:\ETL")

from base.logger import Logger
from extract import run_gitech as extract
from transform import run_gitech_transformer as transform
from load import run_gitech_loader as load

def orchestrator():
    logger = Logger(log_file="logs/orchestrator_gitech.log").get_logger()
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