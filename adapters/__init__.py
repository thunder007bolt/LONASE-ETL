"""
Factory pour créer les adapters selon la source.
Permet d'enregistrer dynamiquement les extractors, transformers et loaders.
"""
from typing import Dict, Callable
from core.config.env_config import JobConfig


class AdapterFactory:
    """Factory pour créer les adapters selon la source"""
    
    _extractors: Dict[str, Callable] = {}
    _transformers: Dict[str, Callable] = {}
    _loaders: Dict[str, Callable] = {}
    
    @classmethod
    def register_extractor(cls, source_name: str, extractor_func: Callable):
        """Enregistre un extractor pour une source"""
        cls._extractors[source_name] = extractor_func
    
    @classmethod
    def register_transformer(cls, source_name: str, transformer_func: Callable):
        """Enregistre un transformer pour une source"""
        cls._transformers[source_name] = transformer_func
    
    @classmethod
    def register_loader(cls, source_name: str, loader_func: Callable):
        """Enregistre un loader pour une source"""
        cls._loaders[source_name] = loader_func
    
    def create_extractor(self, config: JobConfig) -> Callable:
        """Crée un extractor pour la source"""
        if config.source_name not in self._extractors:
            raise ValueError(f"Extractor non trouvé pour: {config.source_name}")
        return self._extractors[config.source_name]
    
    def create_transformer(self, config: JobConfig) -> Callable:
        """Crée un transformer pour la source"""
        if config.source_name not in self._transformers:
            raise ValueError(f"Transformer non trouvé pour: {config.source_name}")
        return self._transformers[config.source_name]
    
    def create_loader(self, config: JobConfig) -> Callable:
        """Crée un loader pour la source"""
        if config.source_name not in self._loaders:
            raise ValueError(f"Loader non trouvé pour: {config.source_name}")
        return self._loaders[config.source_name]


def get_adapter_factory(source_name: str) -> AdapterFactory:
    """Récupère la factory pour une source et charge les adapters"""
    import importlib
    
    # Essayer d'importer le module adapter pour la source
    # Format: adapters.{source_name} ou adapters.{category}.{source_name}
    possible_modules = [
        f"adapters.{source_name}",
        f"scripts.{source_name}",  # Fallback vers l'ancienne structure
    ]
    
    # Si le nom contient un underscore, essayer aussi la catégorie
    if '_' in source_name:
        category = source_name.split('_')[0]
        possible_modules.insert(1, f"adapters.{category}.{source_name}")
    
    for module_name in possible_modules:
        try:
            adapter_module = importlib.import_module(module_name)
            if hasattr(adapter_module, "register_adapters"):
                adapter_module.register_adapters()
                break
        except ImportError:
            continue
    
    return AdapterFactory()

