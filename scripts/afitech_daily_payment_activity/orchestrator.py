from utils.path_utils import setup_project_paths
setup_project_paths()

import os
from base.orchestrator import Orchestrator
from extract import run_afitech_payment_daily_activity as extract
from transform import run_afitech_daily_payment_activity_transformer as transform
from load import run_afitech_daily_payment_activity_loader as load

def run_afitech_daily_payment_activity_orchestrator():
    allow_transform = os.getenv("transform") if os.getenv("transform") is not None else True
    allow_loading = os.getenv("load") if os.getenv("load") is not None else True
    
    orchestrator = Orchestrator(
        name="afitech_daily_payment_activity",
        extractor=extract,
        transformer=transform if allow_transform else None,
        loader=load if allow_loading else None
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_daily_payment_activity_orchestrator()