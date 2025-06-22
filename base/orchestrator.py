from base.logger import Logger


class Orchestrator:
    """
        Classe d'orchestrateur
    """
    def __init__(
            self,
            name,
            extractor=None,
            transformer=None,
            loader=None,
            extractors=None,
            transformers=None,
            loaders=None,
            config_paths=None
    ):
        """
            Initialisation de l'objet

            Args:
                name (str): Nom de l'orchestrateur
                extractor (function): Fonction d'extraction
                transformer (function): Fonction de transformation
                loader (function): Fonction de chargement
                extractors (list): Liste des fonctions d'extraction
                transformers (list): Liste des fonctions de transformation
                loaders (list): Liste des fonctions de chargement
                config_paths (list): Liste des chemins des fichiers de configuration
        """
        self.logger = Logger(f"logs/orchestrator_{name}.log").get_logger()
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

        self.extractors = extractors
        self.transformers = transformers
        self.loaders = loaders
        self.config_paths = config_paths

    def run(self):
        logger = self.logger
        try:
            logger.info("Lancement de l'orchestrateur...")
            if self.extractor: self.extractor()
            if self.transformer: self.transformer()
            if self.loader: self.loader()

            if self.extractors:
                for idx, extractor in enumerate(self.extractors):
                    extractor(self.config_paths[idx])

            if self.transformers:
                for idx, transformer in enumerate(self.transformers):
                    transformer(self.config_paths[idx])

            if self.loaders:
                for idx, loader in enumerate(self.loaders):
                    loader(self.config_paths[idx])

            logger.info("Orchestrator terminé avec succès.")

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'orchestrateur : {e}")
            raise e
