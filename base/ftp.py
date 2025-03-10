from abc import ABC, abstractmethod

from base.logger import Logger
from utils.config_utils import get_secret, get_config

from datetime import datetime
from ftplib import FTP
from pathlib import Path
import time, os, glob

class BaseFTP(ABC):
    def __init__(self, name: str, log_file: str, env_variables_list: list):
        self.name = name
        self.log_file = log_file
        self.secret_config = get_secret(env_variables_list)
        self.ftp = None

        configs = get_config(name)
        config = configs[name]
        base_config = configs['base']
        data_path = Path(base_config["paths"]["data_path"])
        self.source_path = config["ftp_remote_path"]
        self.extraction_dest_relative_path = data_path / config["extraction_dest_relative_path"]
        self.loaded_path = data_path / config['loaded_dest_relative_path']
        self.error_path = data_path / config['error_dest_relative_path']

        self.files_pattern = ''

        ### Dates
        self.date: datetime | None = config["date"]

        # wait time
        self.wait_time = config["wait_time"]

        logger = Logger(log_file=log_file).get_logger()
        self.logger = logger
        self.logger.info("Initialisation...")

    @abstractmethod
    def _setup_files_pattern(self):
        pass

    def _login(self):
        try:
            self.logger.info(f"Connexion FTP...")
            host = self.secret_config["FTP_HOST"]
            username = self.secret_config["FTP_USERNAME"]
            password = self.secret_config["FTP_PASSWORD"]
            ftp = FTP(host)
            ftp.login(username, password)
            if self.logger:
                self.logger.info(f"Connexion FTP réussie")
            self.ftp = ftp
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la connexion FTP : {e}")
            raise e

    def _download_files(self):
        try:
            self.ftp.cwd(self.source_path)
            files = self.ftp.nlst()
            for filename in files:
                if self.files_pattern in filename:
                    destination = self.extraction_dest_relative_path / filename
                    self.logger.info(f"Téléchargement du fichier {filename}")
                    self.ftp.retrbinary("RETR %s" %filename, open(destination,'wb').write)
        except Exception as e:
            self.logger.error(f"Erreur lors du téléchargement des fichiers : {e}")
            raise e

    def _verify_download(self):
        def wait_for_download(pattern, timeout=120, poll_interval=2):
            """Attend l'apparition d'un fichier correspondant au motif donné."""
            start_time = time.time()
            while time.time() - start_time < 120 if timeout is None else timeout:
                files = glob.glob(pattern)
                if files:
                    return files[0]
                time.sleep(poll_interval)
            return None

        tmp_file = wait_for_download(os.path.join(self.extraction_dest_relative_path, self.files_pattern), timeout=self.wait_time, poll_interval=2)
        if not tmp_file:
            print("Téléchargement anormalement long, nous allons recommencer")
            self._download_files()
        else:
            self.logger.info(f"Le fichier du {self.date} a bien ete telecharge")

    def _close_ftp_connection(self):
        try:
            self.ftp.close()
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de la connexion FTP : {e}")
            raise e