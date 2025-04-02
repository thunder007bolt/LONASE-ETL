import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from transform import run_honore_gaming_ticket_transformer

def run_honore_gaming_ticket_orchestrator():
    orchestrator = Orchestrator(
        name="honore_gaming_ticket",
        extractor=run_honore_gaming_ticket_transformer,
    )
    orchestrator.run()

if __name__ == "__main__":
    run_honore_gaming_ticket_orchestrator()