from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_afitech_betting_operation_activity as extract
# from transform import run_afitech_betting_operation_transformer as transform
# from load import run_afitech_betting_operation_loader as load

def run_afitech_betting_operation_orchestrator():
    orchestrator = Orchestrator(
        name="afitech_betting_operation",
        extractor=extract,
        # transformer=transform,  # Désactivé
        # loader=load  # Désactivé
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_betting_operation_orchestrator()