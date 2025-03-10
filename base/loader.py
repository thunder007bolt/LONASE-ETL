from numpy.ma.extras import column_stack

from base.logger import Logger
from utils.config_utils import get_config, get_transformation_configurations, get_loading_configurations
from pathlib import Path
from abc import ABC, abstractmethod

from utils.db_utils import get_db_connection
from utils.file_manipulation import move_file


class Loader(ABC):
    def __init__(self, name, log_file, columns, table_name):
        self.error_file_count = 0
        self.error_file_names_list = []
        self.columns = columns
        self.table_name = table_name
        self.cursor, self.connexion = None, None
        (
            self.secret_config,
            self.logger,
            self.loaded_path,
            self.source_path,
            self.error_path,
            self.file_pattern
        ) = get_loading_configurations(name, log_file)

    def check_error(self):
        if self.error_file_count > 0:
            self.logger.info(f"Certains fichiers n'ont pas été chargé")
            # Todo: Lister les fichiers qui n'ont pas été tranformés

    def set_error(self, filename):
        self.error_file_count += 1
        self.error_file_names_list.append(filename)

    def _delete_table_datas(self):
        self.logger.info(f"Suppression des données dans la table")
        self.cursor.execute(f"TRUNCATE TABLE {self.table_name}")
        self.connexion.commit()

    def _load_datas(self, data):
        self.logger.info("Chargement des données dans la base...")
        insert_query = f"""
            INSERT INTO {self.table_name} ({", ".join([f'[{col}]' for col in self.columns])})
            VALUES
                ({", ".join(["?"] * len(self.columns))})
        """
        self.cursor.executemany(insert_query, data)
        self.connexion.commit()

        self.logger.info("Données chargées avec succès dans la base.")

    @abstractmethod
    def _convert_file_to_dataframe(self, file):
        pass

    def _dataframe_to_tuples(self, df):
        self.logger.info("Conversion des données en tuples...")
        return list(df.itertuples(index=False, name=None))

    def _connection_to_db(self):
        secret_config = self.secret_config
        SERVER = secret_config['SQL_SERVER_HOST']
        DATABASE = secret_config['SQL_SERVER_TEMPDB_NAME']
        USERNAME = secret_config['SQL_SERVER_TEMPDB_USERNAME']
        PASSWORD = secret_config['SQL_SERVER_TEMPDB_PASSWORD']
        self.connexion, self.cursor = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD, logger=self.logger)

    def process_loading(self):
        self._connection_to_db()
        self._delete_table_datas()
        for file in self.source_path.glob(self.file_pattern):
            try:
                df = self._convert_file_to_dataframe(file)
                tuples_data = self._dataframe_to_tuples(df)
                self._load_datas(tuples_data)
                move_file(file, self.loaded_path)
                self.logger.info(f"Fichier {file} traité avec succès.")

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du fichier {file} : {e}")
                move_file(file, self.error_path)

    def __del__(self):
        self.logger.info('------------ Ending --------------')
