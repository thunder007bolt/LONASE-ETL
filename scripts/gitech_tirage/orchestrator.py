import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_gitech_tirage

def run_tirage_orchestrator():
    orchestrator = Orchestrator(
        name="tirage",
        extractor=run_gitech_tirage,
    )
    orchestrator.run()

if __name__ == "__main__":
    run_tirage_orchestrator()