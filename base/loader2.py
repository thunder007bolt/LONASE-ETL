from numpy.ma.extras import column_stack

from base.logger import Logger
from utils.config_utils import get_config, get_transformation_configurations, get_loading_configurations
from pathlib import Path
from abc import ABC, abstractmethod
from utils.db_utils import get_db_connection, get_oracle_connection
from utils.file_manipulation import move_file
import numpy as np

class Loader(ABC):
    def __init__(self, name, log_file):
        env_variables_list = [
            "SQL_SERVER_HOST",
            "SQL_SERVER_TEMPDB_NAME",
            "SQL_SERVER_TEMPDB_USERNAME",
            "SQL_SERVER_TEMPDB_PASSWORD",
            "ORACLE_TARGET_USERNAME",
            "ORACLE_TARGET_PASSWORD",
            "ORACLE_TARGET_HOST",
            "ORACLE_TARGET_PORT",
            "ORACLE_TARGET_SERVICE",
            "ORACLE_CLIENT_LIB_DIR"
        ]
        self.error_file_count = 0
        self.error_file_names_list = []
        (
            self.secret_config,
            self.logger,
            self.loaded_path,
            self.source_path,
            self.error_path,
            self.file_pattern
        ) = get_loading_configurations(name, log_file, env_variables_list=env_variables_list)

        # Oracle Specifics
        self.oracle_cursor, self.oracle_connexion, self.oracle_table_name, self.oracle_columns = None, None, None, None

        # Sql server Specifics
        self.sql_server_cursor, self.sql_server_connexion, self.sql_server_table_name, self.sql_server_columns= None, None, None, None


    def check_error(self):
        if self.error_file_count > 0:
            self.logger.info(f"Certains fichiers n'ont pas été chargé")
            # Todo: Lister les fichiers qui n'ont pas été tranformés

    def set_error(self, filename):
        self.error_file_count += 1
        self.error_file_names_list.append(filename)

    # SQL Server  Methods
    def _connect_sql_server_target(self):
        secret_config = self.secret_config
        SERVER = secret_config['SQL_SERVER_HOST']
        DATABASE = secret_config['SQL_SERVER_TEMPDB_NAME']
        USERNAME = secret_config['SQL_SERVER_TEMPDB_USERNAME']
        PASSWORD = secret_config['SQL_SERVER_TEMPDB_PASSWORD']
        self.sql_server_connexion, self.sql_server_cursor = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD, logger=self.logger)

    def _delete_sql_server_data(self):
        self.logger.info(f"Suppression des données dans la table")
        self.sql_server_cursor.execute(f"TRUNCATE TABLE {self.sql_server_table_name}")
        self.sql_server_connexion.commit()

    def _load_sql_server_data(self, data):
        self.logger.info("Chargement des données dans la base SQL SERVER...")
        insert_query = f"""
            INSERT INTO {self.sql_server_table_name} ({", ".join([f'[{col}]' for col in self.sql_server_columns])})
            VALUES
                ({", ".join(["?"] * len(self.sql_server_columns))})
        """
        self.sql_server_cursor.executemany(insert_query, data)
        self.sql_server_connexion.commit()

        self.logger.info(f"{len(data)} rows loaded successfully into SQL SERVER.")

    @abstractmethod
    def _convert_file_to_dataframe(self, file):
        pass

    def _dataframe_to_tuples(self, df):
        self.logger.info("Conversion des données en tuples...")
        df = df.replace(np.nan, '')
        return list(df.itertuples(index=False, name=None))

    # ORACLE Methods
    def _connect_oracle_target(self):
        ORACLE_TARGET_USERNAME = self.secret_config['ORACLE_TARGET_USERNAME']
        ORACLE_TARGET_PASSWORD = self.secret_config['ORACLE_TARGET_PASSWORD']
        ORACLE_TARGET_HOST = self.secret_config['ORACLE_TARGET_HOST']
        ORACLE_TARGET_PORT = self.secret_config['ORACLE_TARGET_PORT']
        ORACLE_TARGET_SERVICE = self.secret_config['ORACLE_TARGET_SERVICE']
        ORACLE_CLIENT_LIB_DIR = self.secret_config.get('ORACLE_CLIENT_LIB_DIR')
        self.oracle_connexion, self.oracle_cursor = get_oracle_connection(
            username=ORACLE_TARGET_USERNAME,
            password=ORACLE_TARGET_PASSWORD,
            host=ORACLE_TARGET_HOST,
            port=ORACLE_TARGET_PORT,
            service_name=ORACLE_TARGET_SERVICE,
            lib_dir=ORACLE_CLIENT_LIB_DIR,
            logger=self.logger
        )
        nls_setting = ', '
        self.oracle_cursor.execute(f"ALTER SESSION SET NLS_NUMERIC_CHARACTERS = '{nls_setting}'")
        self.oracle_connexion.commit()
        return True

    def _delete_oracle_data(self):
        self.logger.info(f"Truncating Oracle table: {self.oracle_table_name}")
        self.oracle_cursor.execute(f"TRUNCATE TABLE {self.oracle_table_name}")
        self.oracle_connexion.commit()
        self.logger.info(f"Oracle table {self.oracle_table_name} truncated.")

    def _load_oracle_data(self, data: list):

        # Quote column names for Oracle to preserve case and handle special chars, if any in self.columns
        cols_oracle = ", ".join([f'"{col.upper()}"' for col in self.oracle_columns])
        placeholders = ", ".join([f":{i + 1}" for i in range(len(self.oracle_columns))])
        insert_query = f"INSERT INTO {self.oracle_table_name} ({cols_oracle}) VALUES ({placeholders})"

        self.oracle_cursor.executemany(insert_query, data)
        self.oracle_connexion.commit()
        self.logger.info(f"{len(data)} rows loaded successfully into Oracle.")

    def process_loading(self):

        # Connect to Sql server
        self._connect_sql_server_target()
        self._delete_sql_server_data()

        # Connect to Oracle and truncate if enabled
        if  self.oracle_table_name:
            self._connect_oracle_target()
            self._delete_oracle_data()

        for file in self.source_path.glob(self.file_pattern):
            try:
                df = self._convert_file_to_dataframe(file)
                tuples_data = self._dataframe_to_tuples(df)

                # Load to Sql server
                self._load_sql_server_data(tuples_data)

                # Load to Oracle if enabled
                if self.oracle_table_name:
                    self._load_oracle_data(tuples_data)

                self.logger.info(f"Fichier {file} traité avec succès.")
                move_file(file, self.loaded_path)

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du fichier {file} : {e}")
                move_file(file, self.error_path)
                raise e

    def __del__(self):
        self.logger.info('------------ Ending --------------')
