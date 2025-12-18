import sys
sys.path.append("C:\ETL")

from base.logger import Logger
from extract import run_mojabet_ussd_aggr as extract
from load import run_mojabet_ussd_aggr_loader as load

def orchestrator():
    logger = Logger(log_file="logs/orchestrator_mojabet_ussd.log").get_logger()
    try:
        logger.info("Lancement de l'orchestrateur...")
        extract()
        load()
        logger.info("Orchestrateur terminé avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'orchestrateur : {e}")
        raise e

if __name__ == "__main__":
  orchestrator()