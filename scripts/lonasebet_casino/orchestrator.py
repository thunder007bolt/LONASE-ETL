import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from transform import run_lonasebet_casino_transformer
from extract import run_lonasebet_casino
from load import run_lonasebet_casino_loader

def run_lonasebet_casino_orchestrator():
    orchestrator = Orchestrator(
        name="lonasebet_casino",
        extractor=run_lonasebet_casino,
        transformer=run_lonasebet_casino_transformer,
        loader=run_lonasebet_casino_loader

    )
    orchestrator.run()

if __name__ == "__main__":
    run_lonasebet_casino_orchestrator()