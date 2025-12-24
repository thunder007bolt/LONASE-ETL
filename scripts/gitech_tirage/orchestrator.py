from utils.path_utils import setup_project_paths
setup_project_paths()

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