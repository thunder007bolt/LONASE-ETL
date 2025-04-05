import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from transform import run_honore_gaming_ticket_transformer
from extract import run_honore_gaming
from load import run_honore_gaming_ticket_loader

def run_honore_gaming_ticket_orchestrator():
    orchestrator = Orchestrator(
        name="honore_gaming_ticket",
        extractor=run_honore_gaming,
        transformer=run_honore_gaming_ticket_transformer,
        loader=run_honore_gaming_ticket_loader

    )
    orchestrator.run()

if __name__ == "__main__":
    run_honore_gaming_ticket_orchestrator()