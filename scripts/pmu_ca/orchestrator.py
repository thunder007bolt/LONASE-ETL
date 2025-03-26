import sys
sys.path.append("C:\ETL")

from base.orchestrator import Orchestrator
from extract import run_pmu_ca
from transform import run_pmu_ca_transformer
from load import run_pmu_ca_loader

def run_pmu_ca_orchestrator():
    orchestrator = Orchestrator(
        name="pmu_ca",
        extractor=run_pmu_ca,
        transformer=run_pmu_ca_transformer,
        loader=run_pmu_ca_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_pmu_ca_orchestrator()