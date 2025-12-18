import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_ussd_irv
from load import  run_ussd_irv_loader

def run_ussd_irv_orchestrator():
    orchestrator = Orchestrator(
        name="ussd_irv",
        extractor=run_ussd_irv,
        loader=run_ussd_irv_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_ussd_irv_orchestrator()
