from abc import ABC, abstractmethod

from utils.config_utils import get_secret, get_config
from pathlib import Path
from utils.config_utils import get_database_extractor_configurations
from utils.db_utils import get_db_connection, get_oracle_connection
from utils.file_manipulation import move_file
from utils.date_utils import get_yesterday_date
from datetime import timedelta

delta = timedelta(days=1)

class DatabaseExtractor(ABC):
    def __init__(self, name, log_file, env_variables_list, config_path = None):
        self.name = name
        self.log_file = log_file
        (
            self.secret_config,
            self.config,
            self.logger,
            self.extraction_dest_path
        ) = get_database_extractor_configurations(name, log_file, env_variables_list, config_path=config_path)
        self.connection = None
        self.conn_oracle, self.cursor_oracle = None, None
        self.conn_sql_server, self.cursor_sql_server = None, None
        
    def _connection_to_db(self):
        SERVER = self.secret_config['SERVER']
        DATABASE = self.secret_config['DATABASE']
        USERNAME = self.secret_config['USERNAME']
        PASSWORD = self.secret_config['PASSWORD']
        self.conn_sql_server,self.cursor_sql_server = get_db_connection(SERVER, DATABASE, USERNAME, PASSWORD, logger=self.logger)
        self.connexion = self.conn_sql_server
        return True
    
    def _connect_oracle_target(self):
        ORACLE_TARGET_USERNAME = self.secret_config['ORACLE_TARGET_USERNAME']
        ORACLE_TARGET_PASSWORD = self.secret_config['ORACLE_TARGET_PASSWORD']
        ORACLE_TARGET_HOST = self.secret_config['ORACLE_TARGET_HOST']
        ORACLE_TARGET_PORT = self.secret_config['ORACLE_TARGET_PORT']
        ORACLE_TARGET_SERVICE = self.secret_config['ORACLE_TARGET_SERVICE']
        ORACLE_CLIENT_LIB_DIR = self.secret_config.get('ORACLE_CLIENT_LIB_DIR') 
        self.conn_oracle, self.cursor_oracle = get_oracle_connection(
            username=ORACLE_TARGET_USERNAME,
            password=ORACLE_TARGET_PASSWORD,
            host=ORACLE_TARGET_HOST,
            port=ORACLE_TARGET_PORT,
            service_name=ORACLE_TARGET_SERVICE,
            lib_dir=ORACLE_CLIENT_LIB_DIR, 
            logger=self.logger
        )
        nls_setting = ', '
        self.cursor_oracle.execute(f"ALTER SESSION SET NLS_NUMERIC_CHARACTERS = '{nls_setting}'")
        self.conn_oracle.commit()
        return True
           
    def _close_oracle_connection(self):
        if self.conn_oracle:
            try:
                self.conn_oracle.close()
                self.logger.info("Oracle connection closed.")
            except Exception as e:
                self.logger.warning(f"Could not close Oracle connection: {e}")

    def _close_sql_server_connection(self):
        if self.conn_sql_server:
            try:
                self.conn_sql_server.close()
                self.logger.info("SQL Server connection closed.")
            except Exception as e:
                self.logger.warning(f"Could not close SQL Server connection: {e}")
                
    @abstractmethod
    def _load_data_from_db(self, start_date, end_date=None):
        pass

    def _set_date(self):
        _, _, _, yesterday_date = get_yesterday_date()
        self.start_date = self.config.get("start_date") or yesterday_date
        self.end_date =  self.config.get("end_date") or yesterday_date

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