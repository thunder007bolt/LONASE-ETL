import sys
sys.path.append("C:\ETL")
from scripts.mojabet_ussd.transform import run_acajou_digital_transformer

from extract import run_acajou_digital
from transform import run_acajou_digital_transformer
from load import run_acajou_digital_loader
from base.orchestrator import Orchestrator


def run_acajou_digital_orchestrator():
  orchestrator = Orchestrator(
      name="acajou_digital",
      extractor=run_acajou_digital,
      transformer=run_acajou_digital_transformer,
      loader=run_acajou_digital_loader
  )
  orchestrator.run()


  if __name__ == "__main__":
      run_acajou_digital_orchestrator()