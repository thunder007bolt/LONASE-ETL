import sys
sys.path.append("C:\ETL")

from extract import run_afitech_daily_betting_activity
from transform import run_afitech_daily_betting_transformer
from load import run_afitech_daily_betting_loader
from base.orchestrator import Orchestrator

def run_afitech_daily_betting_orchestrator():
  orchestrator = Orchestrator(
      name="afitech_daily_betting",
      extractor=run_afitech_daily_betting_activity,
      transformer=run_afitech_daily_betting_transformer,
      loader=run_afitech_daily_betting_loader
  )
  orchestrator.run()

if __name__ == "__main__":
  run_afitech_daily_betting_orchestrator()