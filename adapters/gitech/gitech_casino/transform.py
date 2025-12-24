"""
Transformer pour gitech_casino.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.gitech_casino.transform import run_gitech_casino_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour gitech_casino.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        run_gitech_casino_transformer,
        "transform",
        "gitech_casino"
    )
    return wrapper(context, config)
