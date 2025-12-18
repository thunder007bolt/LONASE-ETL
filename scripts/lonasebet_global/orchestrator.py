import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from scripts.lonasebet_global.extract import run_lonasebet_global_extractor
from scripts.lonasebet_global.transform import run_lonasebet_global_transformer
from scripts.lonasebet_global.load import run_lonasebet_global_loader

def run_lonasebet_global_orchestrator():
    orchestrator = Orchestrator(
        name="lonasebet_global",
        extractor=run_lonasebet_global_extractor,
        transformer=run_lonasebet_global_transformer,
        loader=run_lonasebet_global_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_lonasebet_global_orchestrator()
