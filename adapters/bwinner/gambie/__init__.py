"""
Adapter pour bwinner_gambie.
"""
from adapters import AdapterFactory
from adapters.bwinner.gambie.extract import run_extract
from adapters.bwinner.gambie.transform import run_transform
from adapters.bwinner.gambie.load import run_load


def register_adapters():
    """Enregistre les adapters pour bwinner_gambie"""
    AdapterFactory.register_extractor("bwinner_gambie", run_extract)
    AdapterFactory.register_transformer("bwinner_gambie", run_transform)
    AdapterFactory.register_loader("bwinner_gambie", run_load)

