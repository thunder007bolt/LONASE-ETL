"""
Transformer pour lonasebet_online.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from core.utils.adapter_helper import create_simple_wrapper
from scripts.lonasebet_online.transform import run_lonasebet_online_transformer


def run_transform(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute la transformation pour lonasebet_online.
    
    Args:
        context: Contexte du pipeline
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat de la transformation
    """
    wrapper = create_simple_wrapper(
        run_lonasebet_online_transformer,
        "transform",
        "lonasebet_online"
    )
    return wrapper(context, config)
