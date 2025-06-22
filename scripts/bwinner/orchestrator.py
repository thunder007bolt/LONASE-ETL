import sys

sys.path.append("C:\ETL")

from transform import run_bwinner_transformer
from load import run_bwinner_loader
from base.orchestrator import Orchestrator


def run_bwinner_orchestrator():
  orchestrator = Orchestrator(
      name="bwinner",
      transformer=run_bwinner_transformer,
      loader=run_bwinner_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_bwinner_orchestrator()