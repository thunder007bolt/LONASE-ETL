from abc import ABC, abstractmethod

from utils.config_utils import get_secret, get_config
from pathlib import Path
from utils.config_utils import get_database_extractor_configurations
from utils.db_utils import get_db_connection
from utils.file_manipulation import move_file
from utils.date_utils import get_yesterday_date
from datetime import timedelta

delta = timedelta(days=1)

class DatabaseExtractor(ABC):
    def __init__(self, name, log_file, env_variables_list):
        self.name = name
        self.log_file = log_file
        (
            self.secret_config,
            self.config,
            self.logger,
            self.extraction_dest_path
        ) = get_database_extractor_configurations(name, log_file, env_variables_list)
        self.connection = None

    def _connection_to_db(self):
        secret_config = self.secret_config
        SERVER = secret_config['SERVER']
        DATABASE = secret_config['DATABASE']
        USERNAME = secret_config['USERNAME']
        PASSWORD = secret_config['PASSWORD']
        self.connexion,_ = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD, logger=self.logger)

    @abstractmethod
    def _load_data_from_db(self, start_date, end_date=None):
        pass

    def _set_date(self):
        _, _, _, yesterday_date = get_yesterday_date()
        if self.config["start_date"] is not None:
            self.start_date = self.config["start_date"]
        else:
            self.start_date = yesterday_date

        if self.config["end_date"] is not None:
            self.end_date = self.config["end_date"]
        else:
            self.end_date = yesterday_date

    def _process_download(self, start_date, end_date=None):
        pass

    def _download_files(self):
        start_date = self.start_date
        end_date = self.start_date
        while start_date <= self.end_date:
            self._load_data_from_db(start_date, end_date)
            start_date += delta
            end_date += delta

    def _save_file(self, data, type="csv" ,name=None,**kwargs):
        output_file = self.extraction_dest_path / name
        try:
            if output_file.exists():
                output_file.unlink()
            if type == "csv":
                data.to_csv(output_file, **kwargs)
            elif type == "excel":
                data.to_excel(output_file, **kwargs)

            self.logger.info(f"Le fichier {name} a été  sauvegardé avec succès.")

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du fichier {name} : {e}")
            return


    def process_extraction(self):
        self._set_date()
        self._connection_to_db()
        self._download_files()