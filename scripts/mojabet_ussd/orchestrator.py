from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_mojabet_ussd as extract
from load import run_mojabet_ussd_loader as load

def run_mojabet_ussd_orchestrator():
    orchestrator = Orchestrator(
        name="mojabet_ussd",
        extractor=extract,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_mojabet_ussd_orchestrator()