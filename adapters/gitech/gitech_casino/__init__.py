"""
Adapter pour gitech_casino.
"""
from adapters import AdapterFactory
from adapters.gitech.gitech_casino.extract import run_extract
from adapters.gitech.gitech_casino.transform import run_transform
from adapters.gitech.gitech_casino.load import run_load


def register_adapters():
    """Enregistre les adapters pour gitech_casino"""
    AdapterFactory.register_extractor("gitech_casino", run_extract)
    AdapterFactory.register_transformer("gitech_casino", run_transform)
    AdapterFactory.register_loader("gitech_casino", run_load)
