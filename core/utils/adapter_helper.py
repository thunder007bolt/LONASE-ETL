"""
Helper pour faciliter la création de wrappers d'adapters.
"""
from typing import Dict, Any, Callable, Optional
from core.config.env_config import JobConfig
from infrastructure.logging.logger import get_logger
from core.utils.date_injector import inject_dates_to_env


def create_simple_wrapper(
    func: Callable,
    step_name: str,
    source_name: str
) -> Callable:
    """
    Crée un wrapper simple pour une fonction existante.
    
    Args:
        func: Fonction existante à wrapper
        step_name: Nom de l'étape (extract, transform, load)
        source_name: Nom de la source
    
    Returns:
        Fonction wrapper compatible avec le pipeline
    """
    def wrapper(context: Dict[str, Any], config: JobConfig) -> Any:
        logger = get_logger(f"{step_name}_{source_name}")
        logger.info(f"Démarrage de l'étape {step_name} pour {source_name}")
        
        try:
            # Exécuter la fonction existante
            # La fonction peut être sync ou async
            import asyncio
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func())
            else:
                result = func()
            
            logger.info(f"Étape {step_name} terminée avec succès pour {source_name}")
            return {
                "status": "success",
                "source": source_name,
                "step": step_name
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'étape {step_name} pour {source_name}: {e}", exc_info=True)
            raise
    
    return wrapper


def create_wrapper_with_dates(
    func: Callable,
    step_name: str,
    source_name: str,
    date_param_name: str = "start_date"
) -> Callable:
    """
    Crée un wrapper qui passe les dates depuis la config.
    
    Args:
        func: Fonction existante qui accepte start_date et end_date
        step_name: Nom de l'étape
        source_name: Nom de la source
        date_param_name: Nom du paramètre de date dans la fonction
    
    Returns:
        Fonction wrapper compatible avec le pipeline
    """
    def wrapper(context: Dict[str, Any], config: JobConfig) -> Any:
        logger = get_logger(f"{step_name}_{source_name}")
        logger.info(f"Démarrage de l'étape {step_name} pour {source_name}")
        
        # Injecter les dates dans les variables d'environnement pour compatibilité
        inject_dates_to_env(config)
        
        if config.start_date or config.end_date:
            logger.info(f"Dates: {config.start_date} -> {config.end_date}")
        
        # Préparer les paramètres avec les dates si disponibles
        kwargs = {}
        if config.start_date:
            kwargs['start_date'] = config.start_date
        if config.end_date:
            kwargs['end_date'] = config.end_date
        
        try:
            # Exécuter la fonction avec les dates
            import asyncio
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(**kwargs))
            else:
                # Si la fonction n'accepte pas de kwargs, essayer sans
                import inspect
                sig = inspect.signature(func)
                if 'start_date' in sig.parameters or 'end_date' in sig.parameters:
                    result = func(**kwargs)
                else:
                    # La fonction lit probablement depuis os.getenv(), on l'a déjà injecté
                    result = func()
            
            logger.info(f"Étape {step_name} terminée avec succès pour {source_name}")
            return {
                "status": "success",
                "source": source_name,
                "step": step_name,
                "start_date": str(config.start_date) if config.start_date else None,
                "end_date": str(config.end_date) if config.end_date else None
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'étape {step_name} pour {source_name}: {e}", exc_info=True)
            raise
    
    return wrapper

