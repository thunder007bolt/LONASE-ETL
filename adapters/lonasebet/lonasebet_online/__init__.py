"""
Adapter pour lonasebet_online.
"""
from adapters import AdapterFactory
from adapters.lonasebet.lonasebet_online.extract import run_extract
from adapters.lonasebet.lonasebet_online.transform import run_transform
from adapters.lonasebet.lonasebet_online.load import run_load


def register_adapters():
    """Enregistre les adapters pour lonasebet_online"""
    AdapterFactory.register_extractor("lonasebet_online", run_extract)
    AdapterFactory.register_transformer("lonasebet_online", run_transform)
    AdapterFactory.register_loader("lonasebet_online", run_load)
