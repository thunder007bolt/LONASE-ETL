import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_zeturf
from load import run_zeturf_loader

def run_zeturf_orchestrator():
    orchestrator = Orchestrator(
        name="zeturf",
        extractor=run_zeturf,
        loader=run_zeturf_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_zeturf_orchestrator()