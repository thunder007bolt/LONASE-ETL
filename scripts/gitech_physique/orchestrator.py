import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_gitech_physique
from transform import run_gitech_physique_transformer
from load import run_gitech_physique_loader

def run_physique_orchestrator():
    orchestrator = Orchestrator(
        name="physique",
        extractor=run_gitech_physique,
        transformer=run_gitech_physique_transformer,
        loader=run_gitech_physique_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_physique_orchestrator()