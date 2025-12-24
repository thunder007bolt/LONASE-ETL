"""
Utilitaire pour injecter les dates depuis JobConfig dans les fonctions existantes.
"""
import os
from typing import Optional
from datetime import datetime
from core.config.env_config import JobConfig


def inject_dates_to_env(config: JobConfig):
    """
    Injecte les dates depuis JobConfig dans les variables d'environnement.
    Cela permet aux fonctions existantes qui lisent depuis os.getenv() de fonctionner.
    
    Args:
        config: Configuration du job avec les dates
    """
    if config.start_date:
        os.environ["start_date"] = config.start_date.strftime("%Y-%m-%d")
    
    if config.end_date:
        os.environ["end_date"] = config.end_date.strftime("%Y-%m-%d")


def get_dates_from_config_or_env(config: JobConfig) -> tuple[Optional[datetime], Optional[datetime]]:
    """
    Récupère les dates depuis la config ou les variables d'environnement.
    
    Args:
        config: Configuration du job
    
    Returns:
        Tuple (start_date, end_date)
    """
    start_date = config.start_date
    end_date = config.end_date
    
    # Si les dates ne sont pas dans la config, essayer les variables d'environnement
    if not start_date:
        start_date_str = os.getenv("start_date")
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                pass
    
    if not end_date:
        end_date_str = os.getenv("end_date")
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                pass
    
    return start_date, end_date

