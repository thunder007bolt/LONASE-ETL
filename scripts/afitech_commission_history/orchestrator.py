import sys
sys.path.append("C:\ETL")

from extract import run_afitech_commission_history
from transform import run_afitech_commission_history_transformer
from load import run_afitech_commission_history_loader
from base.orchestrator import Orchestrator

def run_afitech_commission_history_orchestrator():
  orchestrator = Orchestrator(
      name="afitech_commission_history",
      extractor=run_afitech_commission_history,
      transformer=run_afitech_commission_history_transformer,
      loader=run_afitech_commission_history_loader
  )
  orchestrator.run()

if __name__ == "__main__":
  run_afitech_commission_history_orchestrator()