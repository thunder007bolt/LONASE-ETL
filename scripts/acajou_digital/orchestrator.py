from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_acajou_digital as extract
from transform import run_acajou_digital_transformer as transform
from load import run_acajou_digital_loader as load

def run_acajou_digital_orchestrator():
    orchestrator = Orchestrator(
        name="acajou_digital",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_acajou_digital_orchestrator()