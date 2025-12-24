"""
Adapter pour gitech_parifoot.
Wrapper autour des fonctions existantes pour la nouvelle architecture.
"""
from adapters import AdapterFactory
from adapters.gitech.parifoot.extract import run_extract
from adapters.gitech.parifoot.transform import run_transform
from adapters.gitech.parifoot.load import run_load


def register_adapters():
    """Enregistre les adapters pour gitech_parifoot"""
    AdapterFactory.register_extractor("gitech_parifoot", run_extract)
    AdapterFactory.register_transformer("gitech_parifoot", run_transform)
    AdapterFactory.register_loader("gitech_parifoot", run_load)

