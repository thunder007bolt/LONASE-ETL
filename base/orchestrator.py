from symtable import Function

from base.logger import Logger

class Orchestrator:
    def __init__(self, name, extractor=None, transformer=None, loader=None ):
        self.logger = Logger(f"logs/orchestrator_{name}.log").get_logger()
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self):
        logger = self.logger
        try:
            logger.info("Lancement de l'orchestrateur...")
            if self.extractor : self.extractor()
            if self.transformer: self.transformer()
            if self.loader: self.loader()
            logger.info("Orchestrator terminé avec succès.")

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'orchestrateur : {e}")
            raise e