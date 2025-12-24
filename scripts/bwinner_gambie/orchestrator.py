from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_bwinner_gambie as extract
from transform import run_bwinner_gambie_transformer as transform
from load import run_bwinner_gambie_loader as load

def run_bwinner_gambie_orchestrator():
    orchestrator = Orchestrator(
        name="bwinner_gambie",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_bwinner_gambie_orchestrator()