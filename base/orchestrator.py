from base.logger import Logger
import traceback


class Orchestrator:
    """
    Classe orchestrator de base pour coordonner les étapes ETL (Extract, Transform, Load).
    
    Supporte l'exécution de fonctions uniques ou multiples pour chaque étape.
    """
    def __init__(self, name, extractor=None, transformer=None, loader=None, extractors=None, transformers=None,
                 loaders=None, config_paths=None):
        """
        Initialise l'orchestrator.
        
        Args:
            name: Nom de l'orchestrator (utilisé pour les logs)
            extractor: Fonction d'extraction unique (optionnel)
            transformer: Fonction de transformation unique (optionnel)
            loader: Fonction de chargement unique (optionnel)
            extractors: Liste de fonctions d'extraction (optionnel)
            transformers: Liste de fonctions de transformation (optionnel)
            loaders: Liste de fonctions de chargement (optionnel)
            config_paths: Liste de chemins de configuration (requis si extractors/transformers/loaders utilisés)
        """
        self.logger = Logger(f"logs/orchestrator_{name}.log").get_logger()
        self.extractor = extractor
        self.extractors = extractors
        self.transformer = transformer
        self.transformers = transformers
        self.loader = loader
        self.loaders = loaders
        self.config_paths = config_paths
        self.name = name

    def _execute_step(self, step_name, func, config_path=None):
        """
        Exécute une étape avec gestion d'erreurs améliorée.
        
        Args:
            step_name: Nom de l'étape (pour logging)
            func: Fonction à exécuter
            config_path: Chemin de configuration (optionnel)
        """
        try:
            self.logger.info(f"Début de l'étape: {step_name}")
            if config_path:
                func(config_path)
            else:
                func()
            self.logger.info(f"Étape terminée avec succès: {step_name}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'étape {step_name}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def run(self):
        """
        Exécute le pipeline ETL complet.
        
        Exécute les étapes dans l'ordre: Extract -> Transform -> Load
        """
        logger = self.logger
        try:
            logger.info(f"Lancement de l'orchestrateur '{self.name}'...")
            
            # Exécution des fonctions uniques
            if self.extractor:
                self._execute_step("Extraction", self.extractor)
            if self.transformer:
                self._execute_step("Transformation", self.transformer)
            if self.loader:
                self._execute_step("Chargement", self.loader)

            # Exécution des fonctions multiples
            if self.extractors:
                if not self.config_paths:
                    raise ValueError("config_paths requis pour extractors multiples")
                for idx, extractor in enumerate(self.extractors):
                    config_path = self.config_paths[idx] if idx < len(self.config_paths) else None
                    self._execute_step(f"Extraction {idx+1}", extractor, config_path)

            if self.transformers:
                if not self.config_paths:
                    raise ValueError("config_paths requis pour transformers multiples")
                for idx, transformer in enumerate(self.transformers):
                    config_path = self.config_paths[idx] if idx < len(self.config_paths) else None
                    self._execute_step(f"Transformation {idx+1}", transformer, config_path)

            if self.loaders:
                if not self.config_paths:
                    raise ValueError("config_paths requis pour loaders multiples")
                for idx, loader in enumerate(self.loaders):
                    config_path = self.config_paths[idx] if idx < len(self.config_paths) else None
                    self._execute_step(f"Chargement {idx+1}", loader, config_path)

            logger.info(f"Orchestrator '{self.name}' terminé avec succès.")

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'orchestrateur '{self.name}': {e}")
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            raise e
