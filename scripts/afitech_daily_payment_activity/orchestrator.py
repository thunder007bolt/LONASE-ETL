import sys, os
sys.path.append("C:\ETL")

from base.logger import Logger
from extract import run_afitech_payment_daily_activity as extract
from transform import run_afitech_daily_payment_activity_transformer as transform
from load import run_afitech_daily_payment_activity_loader as load

def orchestrator():
    allow_transform = os.getenv("transform") if os.getenv("transform") is not None else True
    allow_loading= os.getenv("load") if os.getenv("load") is not None else True
    logger = Logger(log_file="logs/orchestrator_afitech_daily_payment_activity.log").get_logger()
    try:
        logger.info("Lancement de l'orchestrateur...")
        extract()
        if allow_transform: transform()
        if allow_loading: load()
        logger.info("Orchestrateur terminé avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'orchestrateur : {e}")
        raise e

if __name__ == "__main__":
  orchestrator()