from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
from extract import run_afitech_daily_betting_activity as extract
from transform import run_afitech_daily_betting_transformer as transform
from load import run_afitech_daily_betting_loader as load

def run_afitech_daily_betting_orchestrator():
    orchestrator = Orchestrator(
        name="afitech_daily_betting",
        extractor=extract,
        transformer=transform,
        loader=load
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_daily_betting_orchestrator()