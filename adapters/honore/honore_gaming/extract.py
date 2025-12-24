"""
Extractor pour honore_gaming.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.honore_gaming.extract import run_honore_gaming


def run_extract(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute l'extraction pour honore_gaming.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de l'extraction
    """
    wrapper = create_simple_wrapper(
        run_honore_gaming,
        "extract",
        "honore_gaming"
    )
    return wrapper(context, config)
