import sys

sys.path.append("C:\ETL")

from extract import run_gitech
from transform import run_gitech_transformer
from load import run_gitech_loader
from base.orchestrator import Orchestrator


def run_gitech_orchestrator():
  orchestrator = Orchestrator(
      name="bwinner",
      extractor=run_gitech,
      transformer=run_gitech_transformer,
      loader=run_gitech_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_gitech_orchestrator()