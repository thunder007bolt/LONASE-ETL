from base.logger import Logger
from utils.config_utils import get_config, get_transformation_configurations, get_loading_configurations
from pathlib import Path
from abc import ABC, abstractmethod
from utils.db_utils import get_db_connection, get_oracle_connection
from utils.file_manipulation import move_file
from time import perf_counter
import numpy as np

class Loader(ABC):
    def __init__(
        self,
        name,
        log_file,
        columns=None,
        table_name=None,
        sql_columns=None,
        sql_table_name=None,
        oracle_columns=None,
        oracle_table_name=None,
        config_path=None,
        env_variables_list=None
    ):
        self.error_file_count = 0
        self.error_file_names_list = []

        # SQL Server configuration (backward compatibility with columns/table_name)
        self.sql_server_columns = sql_columns or columns or []
        self.sql_server_table_name = sql_table_name or table_name
        self.sql_server_cursor, self.sql_server_connexion = None, None

        # Oracle configuration (optional)
        self.oracle_columns = oracle_columns or []
        self.oracle_table_name = oracle_table_name
        self.oracle_cursor, self.oracle_connexion = None, None

        env_vars = env_variables_list or [
            "SQL_SERVER_HOST",
            "SQL_SERVER_TEMPDB_NAME",
            "SQL_SERVER_TEMPDB_USERNAME",
            "SQL_SERVER_TEMPDB_PASSWORD",
            "ORACLE_TARGET_USERNAME",
            "ORACLE_TARGET_PASSWORD",
            "ORACLE_TARGET_HOST",
            "ORACLE_TARGET_PORT",
            "ORACLE_TARGET_SERVICE",
            "ORACLE_CLIENT_LIB_DIR",
        ]
        (
            self.secret_config,
            self.logger,
            self.loaded_path,
            self.source_path,
            self.error_path,
            self.file_pattern
        ) = get_loading_configurations(name, log_file, env_variables_list=env_vars, config_path=config_path)
        self.batch_size = 1000

    def check_error(self):
        if self.error_file_count > 0:
            self.logger.warning(f"{self.error_file_count} fichier(s) n'ont pas été chargé(s)")
            if self.error_file_names_list:
                self.logger.warning(f"Fichiers en erreur: {', '.join(self.error_file_names_list)}")
            return False
        return True

    def set_error(self, filename):
        self.error_file_count += 1
        self.error_file_names_list.append(filename)

    def _delete_table_datas(self):
        self.logger.info(f"Suppression des données dans la table")
        self.sql_server_cursor.execute(f"TRUNCATE TABLE {self.sql_server_table_name}")
        self.sql_server_connexion.commit()

    def _load_datas(self, data):
        self.logger.info("Chargement des données dans la base SQL Server...")
        insert_query = f"""
            INSERT INTO {self.sql_server_table_name} ({", ".join([f'[{col}]' for col in self.sql_server_columns])})
            VALUES
                ({", ".join(["?"] * len(self.sql_server_columns))})
        """
        start = perf_counter()
        for i in range(0, len(data), self.batch_size):
            chunk = data[i:i + self.batch_size]
            self.sql_server_cursor.executemany(insert_query, chunk)
            self.sql_server_connexion.commit()
        duration = perf_counter() - start
        self.logger.info(f"Données chargées avec succès dans SQL Server ({len(data)} lignes) en {duration:.2f}s.")

    @abstractmethod
    def _convert_file_to_dataframe(self, file):
        pass

    def _dataframe_to_tuples(self, df):
        self.logger.info("Conversion des données en tuples...")
        df = df.replace(np.nan, '')
        return list(df.itertuples(index=False, name=None))

    def _validate_dataframe(self, df):
        expected_cols = self.sql_server_columns or self.oracle_columns
        if not expected_cols:
            return
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes dans le fichier : {missing}")

    def _connect_sql_server_target(self):
        secret_config = self.secret_config
        SERVER = secret_config['SQL_SERVER_HOST']
        DATABASE = secret_config['SQL_SERVER_TEMPDB_NAME']
        USERNAME = secret_config['SQL_SERVER_TEMPDB_USERNAME']
        PASSWORD = secret_config['SQL_SERVER_TEMPDB_PASSWORD']
        self.sql_server_connexion, self.sql_server_cursor = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD, logger=self.logger)

    def _connect_oracle_target(self):
        ORACLE_TARGET_USERNAME = self.secret_config.get('ORACLE_TARGET_USERNAME')
        ORACLE_TARGET_PASSWORD = self.secret_config.get('ORACLE_TARGET_PASSWORD')
        ORACLE_TARGET_HOST = self.secret_config.get('ORACLE_TARGET_HOST')
        ORACLE_TARGET_PORT = self.secret_config.get('ORACLE_TARGET_PORT')
        ORACLE_TARGET_SERVICE = self.secret_config.get('ORACLE_TARGET_SERVICE')
        ORACLE_CLIENT_LIB_DIR = self.secret_config.get('ORACLE_CLIENT_LIB_DIR')
        if not ORACLE_TARGET_USERNAME:
            return
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

    def _delete_oracle_data(self):
        if not self.oracle_table_name:
            return
        self.logger.info(f"Truncating Oracle table: {self.oracle_table_name}")
        self.oracle_cursor.execute(f"TRUNCATE TABLE {self.oracle_table_name}")
        self.oracle_connexion.commit()
        self.logger.info(f"Oracle table {self.oracle_table_name} truncated.")

    def _load_oracle_data(self, data: list):
        if not self.oracle_table_name:
            return
        cols_oracle = ", ".join([f'"{col.upper()}"' for col in self.oracle_columns])
        placeholders = ", ".join([f":{i + 1}" for i in range(len(self.oracle_columns))])
        insert_query = f"INSERT INTO {self.oracle_table_name} ({cols_oracle}) VALUES ({placeholders})"
        start = perf_counter()
        for i in range(0, len(data), self.batch_size):
            chunk = data[i:i + self.batch_size]
            self.oracle_cursor.executemany(insert_query, chunk)
            self.oracle_connexion.commit()
        duration = perf_counter() - start
        self.logger.info(f"{len(data)} rows loaded successfully into Oracle in {duration:.2f}s.")

    def process_loading(self):
        # Connections
        if self.sql_server_table_name:
            self._connect_sql_server_target()
            self._delete_table_datas()
        if self.oracle_table_name:
            self._connect_oracle_target()
            self._delete_oracle_data()

        for file in self.source_path.glob(self.file_pattern):
            try:
                df = self._convert_file_to_dataframe(file)
                self._validate_dataframe(df)
                tuples_data = self._dataframe_to_tuples(df)

                if self.sql_server_table_name:
                    self._load_datas(tuples_data)

                if self.oracle_table_name:
                    self._load_oracle_data(tuples_data)

                move_file(file, self.loaded_path)
                self.logger.info(f"Fichier {file} traité avec succès.")

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du fichier {file} : {e}")
                move_file(file, self.error_path)
                raise

    def __del__(self):
        self.logger.info('------------ Ending --------------')
