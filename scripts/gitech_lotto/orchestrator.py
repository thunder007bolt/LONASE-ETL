from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_gitech_lotto as extract
from transform import run_gitech_lotto_transformer as transform
# from load import run_gitech_lotto_loader as load

def run_gitech_lotto_orchestrator():
    orchestrator = Orchestrator(
        name="gitech_lotto",
        extractor=extract,
        transformer=transform,
        # loader=load  # Load désactivé
    )
    orchestrator.run()

if __name__ == "__main__":
    run_gitech_lotto_orchestrator()