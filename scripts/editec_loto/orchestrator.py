from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_editec_loto as extract
from transform import run_editec_loto_transformer as transform
# from load import run_editec_loto_loader as load

def run_editec_loto_orchestrator():
    orchestrator = Orchestrator(
        name="editec_loto",
        extractor=extract,
        transformer=transform,
        # loader=load  # Load désactivé
    )
    orchestrator.run()

if __name__ == "__main__":
    run_editec_loto_orchestrator()