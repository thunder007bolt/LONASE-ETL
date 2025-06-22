import logging
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, log_file="app.log", log_level=logging.INFO, max_size=5 * 1024 * 1024, backup_count=1):
        """
        Initialise le logger avec rotation de fichiers.
        :param log_file: Nom du fichier de log.
        :param log_level: Niveau de log (e.g., logging.INFO, logging.DEBUG).
        :param max_size: Taille maximale du fichier de log avant rotation (en octets).
        :param backup_count: Nombre maximum de fichiers de log sauvegardés.
        """
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(log_level)

        if not self.logger.hasHandlers():
            # Créer un gestionnaire de fichiers avec rotation
            handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count, encoding='utf-8')
            handler.setLevel(log_level)
            # Format des messages de log
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)d - %(message)s")
            handler.setFormatter(formatter)
            # Ajouter le gestionnaire au logger
            self.logger.addHandler(handler)
            # Gestionnaire de log pour la console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.logger.info("------------ Starting --------------")

    def get_logger(self):
        """
        Retourne l'instance configurée du logger.
        :return: Logger configuré.
        """
        return self.logger

