import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path # Importer Path

# os n'est plus explicitement utilisé ici, peut être enlevé si c'est le seul usage.

class Logger:
    def __init__(self, log_file_path: str | Path = "app.log",
                 log_level: int = logging.INFO,
                 max_size_bytes: int = 5 * 1024 * 1024,
                 backup_count: int = 1,
                 logger_name: str = None,
                 add_console_handler: bool = True):
        """
        Initialise le logger avec rotation de fichiers.

        Args:
            log_file_path (str | Path): Chemin du fichier de log.
            log_level (int): Niveau de log (e.g., logging.INFO, logging.DEBUG).
            max_size_bytes (int): Taille maximale du fichier de log avant rotation (en octets).
            backup_count (int): Nombre maximum de fichiers de log sauvegardés.
            logger_name (str, optional): Nom du logger. Si None, le nom du fichier de log est utilisé.
                                         Defaults to None.
            add_console_handler (bool, optional): Si True, ajoute un handler pour logger vers la console.
                                                  Defaults to True.
        """
        # Convertir en Path et s'assurer que le répertoire parent existe
        resolved_log_file_path = Path(log_file_path).resolve()
        resolved_log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Déterminer le nom effectif du logger
        effective_logger_name = logger_name or str(resolved_log_file_path)

        self.logger = logging.getLogger(effective_logger_name)
        self.logger.setLevel(log_level)

        # Configurer les handlers seulement si ce logger spécifique (par son nom) n'en a pas déjà
        # Cela évite la duplication de logs si plusieurs instances de Logger sont créées pour le même nom/fichier.
        if not self.logger.hasHandlers():
            # Formatter commun pour tous les handlers de cette instance
            log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
            ) # Ajout de %(name)s et %(module)s pour plus de contexte

            # Handler pour le fichier avec rotation
            file_handler = RotatingFileHandler(
                resolved_log_file_path,
                maxBytes=max_size_bytes,
                backupCount=backup_count,
                encoding='utf-8' # Spécifier l'encodage
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(log_formatter)
            self.logger.addHandler(file_handler)

            # Handler optionnel pour la console
            if add_console_handler:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level) # Le niveau peut être différent pour la console si besoin
                console_handler.setFormatter(log_formatter)
                self.logger.addHandler(console_handler)

            self.logger.info(f"Logger '{effective_logger_name}' initialisé. Sauvegarde dans: {resolved_log_file_path}")
            # Le message "------------ Starting --------------" peut être remplacé par un message plus informatif.

    def get_logger(self) -> logging.Logger:
        """
        Retourne l'instance configurée du logger.

        Returns:
            logging.Logger: L'instance du logger.
        """
        return self.logger

# Exemple d'utilisation (peut être enlevé si c'est une bibliothèque)
if __name__ == '__main__':
    # Créer un dossier de logs s'il n'existe pas pour l'exemple
    Path("logs_example").mkdir(exist_ok=True)

    logger_instance1 = Logger(log_file_path="logs_example/my_app.log", logger_name="MyAppLogger")
    log1 = logger_instance1.get_logger()
    log1.info("Ceci est un message d'info de MyAppLogger.")
    log1.warning("Ceci est un avertissement.")

    logger_instance2 = Logger(log_file_path="logs_example/another_module.log", log_level=logging.DEBUG)
    log2 = logger_instance2.get_logger()
    log2.debug("Message de débogage pour another_module.")
    log2.info("Message d'info pour another_module.")

    # Test de ré-initialisation (ne devrait pas ajouter de handlers dupliqués)
    logger_instance_dup = Logger(log_file_path="logs_example/my_app.log", logger_name="MyAppLogger")
    log_dup = logger_instance_dup.get_logger()
    log_dup.info("Message après tentative de ré-initialisation (devrait apparaître une fois).")
