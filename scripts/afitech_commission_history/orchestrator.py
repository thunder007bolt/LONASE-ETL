from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_afitech_commission_history as extract
from transform import run_afitech_commission_history_transformer as transform
from load import run_afitech_commission_history_loader as load

def run_afitech_commission_history_orchestrator():
    orchestrator = Orchestrator(
        name="afitech_commission_history",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_commission_history_orchestrator()