"""
Adapter pour honore_gaming.
"""
from adapters import AdapterFactory
from adapters.honore.honore_gaming.extract import run_extract
from adapters.honore.honore_gaming.transform import run_transform
from adapters.honore.honore_gaming.load import run_load


def register_adapters():
    """Enregistre les adapters pour honore_gaming"""
    AdapterFactory.register_extractor("honore_gaming", run_extract)
    AdapterFactory.register_transformer("honore_gaming", run_transform)
    AdapterFactory.register_loader("honore_gaming", run_load)
