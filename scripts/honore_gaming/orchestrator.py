import sys

sys.path.append("C:\ETL")

from extract import run_honore_gaming
from transform import run_honore_gaming_transformer
from load import run_honore_gaming_loader
from base.orchestrator import Orchestrator


def run_honore_gaming_orchestrator():
  orchestrator = Orchestrator(
      name="honore_gaming",
      extractor=run_honore_gaming,
      transformer=run_honore_gaming_transformer,
      loader=run_honore_gaming_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_honore_gaming_orchestrator()