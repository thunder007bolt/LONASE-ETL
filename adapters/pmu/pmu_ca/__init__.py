"""
Adapter pour pmu_ca.
"""
from adapters import AdapterFactory
from adapters.pmu.pmu_ca.extract import run_extract
from adapters.pmu.pmu_ca.transform import run_transform
from adapters.pmu.pmu_ca.load import run_load


def register_adapters():
    """Enregistre les adapters pour pmu_ca"""
    AdapterFactory.register_extractor("pmu_ca", run_extract)
    AdapterFactory.register_transformer("pmu_ca", run_transform)
    AdapterFactory.register_loader("pmu_ca", run_load)
