from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_gitech as extract
from transform import run_gitech_transformer as transform
from load import run_gitech_loader as load

def run_solidicon_orchestrator():
    orchestrator = Orchestrator(
        name="solidicon",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_solidicon_orchestrator()