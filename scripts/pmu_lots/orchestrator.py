import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_pmu_lots
from transform import run_pmu_lots_transformer
from load import run_pmu_lots_loader

def run_pmu_lots_orchestrator():
    orchestrator = Orchestrator(
        name="pmu_lots",
        extractor=run_pmu_lots,
        transformer=run_pmu_lots_transformer,
        loader=run_pmu_lots_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_pmu_lots_orchestrator()