from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from transform import run_minishop_transformer
from extract import run_minishop
from load import run_minishop_loader

def run_minishop_orchestrator():
    orchestrator = Orchestrator(
        name="minishop",
        extractor=run_minishop,
        transformer=run_minishop_transformer,
        loader=run_minishop_loader

    )
    orchestrator.run()

if __name__ == "__main__":
    run_minishop_orchestrator()