import sys

sys.path.append("C:\ETL")
from base.orchestrator import Orchestrator
from extract import run_afitech_betting_operation_activity



def run_afitech_betting_operation_orchestrator():
  orchestrator = Orchestrator(
      name="afitech_betting_operation",
      extractor=run_afitech_betting_operation_activity,
  )
  orchestrator.run()

  if __name__ == "__main__":
      run_afitech_betting_operation_orchestrator()