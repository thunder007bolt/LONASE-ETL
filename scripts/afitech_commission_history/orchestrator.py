import sys
sys.path.append("C:\ETL")

from base.logger import Logger
from extract import run_afitech_commission_history as extract
from transform import run_afitech_commission_history_transformer as transform
from load import run_afitech_commission_history_loader as load

def orchestrator():
    logger = Logger(log_file="logs/orchestrator_afitech_commission_history.log").get_logger()
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