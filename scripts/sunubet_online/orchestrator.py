from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_sunubet_online as extract
from transform import run_sunubet_online_transformer as transform
from load import run_sunubet_online_loader as load

def run_sunubet_online_orchestrator():
    orchestrator = Orchestrator(
        name="sunubet_online",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_sunubet_online_orchestrator()