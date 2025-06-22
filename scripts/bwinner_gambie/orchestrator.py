import sys

sys.path.append("C:\ETL")

from transform import run_bwinner_gambie_transformer
from load import run_bwinner_gambie_loader
from extract import run_bwinner_gambie
from base.orchestrator import Orchestrator


def run_bwinner_gambie_orchestrator():
  orchestrator = Orchestrator(
      name="bwinner",
      extractor=run_bwinner_gambie,
      transformer=run_bwinner_gambie_transformer,
      loader=run_bwinner_gambie_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_bwinner_gambie_orchestrator()