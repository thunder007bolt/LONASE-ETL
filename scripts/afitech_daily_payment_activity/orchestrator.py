import sys
sys.path.append("C:\ETL")

from extract import run_afitech_payment_daily_activity
from transform import run_afitech_daily_payment_activity_transformer
from load import run_afitech_daily_payment_activity_loader
from base.orchestrator import Orchestrator

def run_afitech_daily_payment_activity_orchestrator():
  orchestrator = Orchestrator(
      name="afitech_daily_payment_activity",
      extractor=run_afitech_payment_daily_activity,
      transformer=run_afitech_daily_payment_activity_transformer,
      loader=run_afitech_daily_payment_activity_loader
  )
  orchestrator.run()

if __name__ == "__main__":
  run_afitech_daily_payment_activity_orchestrator()