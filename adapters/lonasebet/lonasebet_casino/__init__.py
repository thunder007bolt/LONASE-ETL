"""
Adapter pour lonasebet_casino.
"""
from adapters import AdapterFactory
from adapters.lonasebet.lonasebet_casino.extract import run_extract
from adapters.lonasebet.lonasebet_casino.transform import run_transform
from adapters.lonasebet.lonasebet_casino.load import run_load


def register_adapters():
    """Enregistre les adapters pour lonasebet_casino"""
    AdapterFactory.register_extractor("lonasebet_casino", run_extract)
    AdapterFactory.register_transformer("lonasebet_casino", run_transform)
    AdapterFactory.register_loader("lonasebet_casino", run_load)
