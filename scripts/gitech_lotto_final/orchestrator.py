from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from transform import run_gitech_lotto_final_transformer
from load import run_gitech_lotto_final_loader

def run_gitech_lotto_final_orchestrator():
    orchestrator = Orchestrator(
        name="gitech_lotto_final",
        transformer=run_gitech_lotto_final_transformer,
        loader=run_gitech_lotto_final_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_gitech_lotto_final_orchestrator()