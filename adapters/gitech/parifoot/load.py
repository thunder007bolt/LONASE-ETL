"""
Loader pour gitech_parifoot.
Wrapper autour du loader existant.
"""
from typing import Dict, Any
from core.config.env_config import JobConfig
from scripts.gitech_parifoot.load import run_gitech_parifoot_loader


def run_load(context: Dict[str, Any], config: JobConfig) -> Any:
    """
    Exécute le chargement pour gitech_parifoot.
    
    Args:
        context: Contexte du pipeline (contient les résultats de la transformation)
        config: Configuration du job depuis les variables d'environnement
    
    Returns:
        Résultat du chargement
    """
    # Exécuter le chargement existant
    run_gitech_parifoot_loader()
    
    # Retourner un résultat
    return {
        "status": "success",
        "source": config.source_name,
        "loaded_records": 0  # Peut être enrichi si nécessaire
    }

