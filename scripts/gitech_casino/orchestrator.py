import sys

sys.path.append("C:\ETL")

from extract import run_gitech_casino
from transform import run_gitech_casino_transformer
from load import run_gitech_casino_loader
from base.orchestrator import Orchestrator


def run_gitech_casino_orchestrator():
  orchestrator = Orchestrator(
      name="bwinner",
      extractor=run_gitech_casino,
      transformer=run_gitech_casino_transformer,
      loader=run_gitech_casino_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_gitech_casino_orchestrator()