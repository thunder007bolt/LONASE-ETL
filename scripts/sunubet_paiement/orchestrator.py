from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_sunubet_paiement as extract
# from transform import run_sunubet_casino_transformer as transform
from load import run_sunubet_paiement_loader as load

def run_sunubet_paiement_orchestrator():
    orchestrator = Orchestrator(
        name="sunubet_paiement",
        extractor=extract,
        # transformer=transform,  # Désactivé
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_sunubet_paiement_orchestrator()