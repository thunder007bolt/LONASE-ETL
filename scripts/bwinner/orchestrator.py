from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from transform_from_afitech import run_bwinner_transformer as transform
from load import run_bwinner_loader as load

def run_bwinner_orchestrator():
    orchestrator = Orchestrator(
        name="bwinner",
        # extractor=None,  # Extract désactivé
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_bwinner_orchestrator()