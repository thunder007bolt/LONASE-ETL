from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_honore_gaming as extract
from transform import run_honore_gaming_transformer as transform
from load import run_honore_gaming_loader as load

def run_honore_gaming_orchestrator():
    orchestrator = Orchestrator(
        name="honore_gaming",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_honore_gaming_orchestrator()