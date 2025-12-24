from utils.path_utils import setup_project_paths
setup_project_paths()

from base.orchestrator import Orchestrator
# pmu ca
from scripts.pmu_ca.extract import run_pmu_ca
from scripts.pmu_ca.transform import run_pmu_ca_transformer
from scripts.pmu_ca.load import run_pmu_ca_loader
# pmu lots
from scripts.pmu_lots.extract import run_pmu_lots
from scripts.pmu_lots.transform import run_pmu_lots_transformer
from scripts.pmu_lots.load import run_pmu_lots_loader

pmu_ca_config_path = 'scripts/pmu_ca/config.yml'
pmu_lots_config_path = 'scripts/pmu_lots/config.yml'

def run_pmu_ca_orchestrator():
    orchestrator = Orchestrator(
        name="pmu_senegal",
        config_paths=[pmu_ca_config_path, pmu_lots_config_path],
        extractors=[run_pmu_ca, run_pmu_lots],
        transformers=[run_pmu_ca_transformer, run_pmu_lots_transformer],
        loaders=[run_pmu_ca_loader, run_pmu_lots_loader]
    )
    orchestrator.run()

if __name__ == "__main__":
    run_pmu_ca_orchestrator()