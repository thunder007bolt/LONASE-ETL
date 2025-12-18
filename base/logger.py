import logging
from logging.handlers import RotatingFileHandler
import colorlog
import inspect
import re # Import the regular expression module
from datetime import datetime

# We need to access the escape codes directly from the module
from colorlog.escape_codes import escape_codes


class AnsiEscapeCodeFilter(logging.Filter):
    """
    A logging filter that removes ANSI escape codes from log messages.
    This is useful for ensuring log files do not contain uninterpreted color codes.
    """
    # Regular expression to match ANSI escape codes
    # This pattern covers common SGR (Select Graphic Rendition) codes
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def filter(self, record):
        """
        Filters the log record, removing ANSI escape codes from the message.
        """
        if isinstance(record.msg, str):
            record.msg = self.ANSI_ESCAPE_PATTERN.sub('', record.msg)
        return True


class Logger:
    def __init__(self, log_file="app.log", log_level=logging.INFO, max_size=5 * 1024 * 1024, backup_count=1):
        """
        Initializes the Logger setup.
        Configures file and console handlers with specific formatting and rotation.
        """
        # Use the name of the calling module to get a unique logger instance
        # inspect.stack()[1].filename gives the name of the file that called Logger()
        caller_name = inspect.stack()[1].filename
        self.logger = logging.getLogger(caller_name)
        self.logger.setLevel(log_level)

        # Prevents adding handlers multiple times if the class is instantiated more than once
        if not self.logger.hasHandlers():
            # --- File Handler Setup ---
            # This handler writes log messages to a file, with rotation.
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'  # Using utf-8 is generally safer
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            # Add the filter to the file handler to strip ANSI codes
            # file_handler.addFilter(AnsiEscapeCodeFilter())
            self.logger.addHandler(file_handler)

            # --- Console Handler Setup ---
            # This handler prints log messages to the console with colors.
            console_handler = colorlog.StreamHandler()
            console_handler.setLevel(log_level)

            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(levelname)s - %(lineno)d - %(message)s%(reset)s',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red,bg_white',  # Made critical more prominent
                }
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # --- Initial startup message ---
            # The escape_codes dictionary is directly from the colorlog.escape_codes module.
            codes = escape_codes
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formate la date et l'heure
            start_message = (
                f"{codes['bold']}{codes['white']}{codes['bg_black']}"
                f"  --- DÉMARRAGE DU SCRIPT ({current_time}) ---  "  # Message mis à jour avec date/heure
                f"{codes['reset']}"
            )
            self.logger.info(start_message)

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger


# --- Example of how to use the logger ---
if __name__ == "__main__":
    # Get the logger instance. It will be configured on the first call.
    my_logger_instance = Logger(log_file="example_app.log").get_logger()

    my_logger_instance.debug("Ceci est un message de débogage.")
    my_logger_instance.info("L'opération a démarré avec succès.")
    my_logger_instance.warning("Attention : l'espace disque est faible.")
    my_logger_instance.error("Une erreur critique est survenue.")
    my_logger_instance.critical("Le système est sur le point de s'arrêter.")

    # Subsequent calls in the same application will retrieve the same logger instance
    another_instance = Logger().get_logger()
    another_instance.info("This message comes from a second handle to the same logger.")
