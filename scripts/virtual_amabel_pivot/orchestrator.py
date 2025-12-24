from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_virtual_amabel_pivot as extract
from transform import run_virtual_amabel_pivot_transformer as transform
from load import run_virtual_amabel_pivot_loader as load

def run_virtual_amabel_pivot_orchestrator():
    orchestrator = Orchestrator(
        name="virtual_amabel_pivot",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_virtual_amabel_pivot_orchestrator()