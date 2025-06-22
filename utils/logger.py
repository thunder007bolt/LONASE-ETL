import logging
import sys

def setup_logger(name, log_file, level=logging.INFO, console_out=True):
    """Configure et retourne un logger."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Créer un handler pour écrire dans le fichier de log
    file_handler = logging.FileHandler(log_file, mode='a') # 'a' pour append
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    # Optionnel: Ajouter un handler pour afficher les logs sur la console
    if console_out:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
