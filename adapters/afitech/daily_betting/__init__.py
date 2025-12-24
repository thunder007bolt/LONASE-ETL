"""
Adapter pour afitech_daily_betting.
"""
from adapters import AdapterFactory
from adapters.afitech.daily_betting.extract import run_extract
from adapters.afitech.daily_betting.transform import run_transform
from adapters.afitech.daily_betting.load import run_load


def register_adapters():
    """Enregistre les adapters pour afitech_daily_betting"""
    AdapterFactory.register_extractor("afitech_daily_betting", run_extract)
    AdapterFactory.register_transformer("afitech_daily_betting", run_transform)
    AdapterFactory.register_loader("afitech_daily_betting", run_load)

