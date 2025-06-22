import pandas as pd
import numpy as np
from base.loader import Loader
from utils.config_utils import get_config
from utils.file_manipulation import move_file # For moving files in the overridden process_loading

class LonasebetGlobalLoad(Loader):
    def __init__(self):
        name = 'lonasebet_global'
        log_file = 'logs/loader_lonasebet_global.log'

        # Get specific config for lonasebet_global to fetch columns and table names
        # These are passed to super().__init__ as per base.loader.Loader's expectation
        specific_config = get_config(name) # Gets the 'lonasebet_global' section from config
        self.table_name_from_config = specific_config[name].get('db_table_name', '[DWHPR_TEMP].[OPTIWARETEMP].[src_prd_globalLonasebet]')
        self.columns_from_config = specific_config[name].get('columns', [])
        self.db_archive_table_name = specific_config[name].get('db_archive_table_name', '[DWHPR_TEMP].[OPTIWARETEMP].[ar_globalLonasebet]')

        # Call super().__init__ with values expected by base.loader.Loader
        # 'name' is the job name, 'log_file' is for the logger,
        # 'columns_from_config' are the DB columns, 'table_name_from_config' is the target table.
        super().__init__(name, log_file, self.columns_from_config, self.table_name_from_config)

    def _convert_file_to_dataframe(self, file_path):
        """
        Reads a CSV file into a pandas DataFrame.
        This method is required by the abstract base class Loader.
        """
        self.logger.info(f"Lecture du fichier transformé : {file_path}")
        try:
            # Transformed files are saved in UTF-8 by LonasebetGlobalTransformer
            df = pd.read_csv(file_path, sep=';', dtype=str, encoding='utf8')
            # Ensure columns are in the correct order as per self.columns (from base class, set by __init__)
            # And handle any missing columns by adding them with empty strings
            for col in self.columns: # self.columns is set in base Loader's __init__
                if col not in df.columns:
                    self.logger.warning(f"Colonne manquante '{col}' dans {file_path.name}. Ajout avec des valeurs vides.")
                    df[col] = ''
            df = df[self.columns] # Ensure correct order and selection

            # Base loader's _dataframe_to_tuples handles np.nan replacement
            # but doing it here ensures consistency if that method is ever bypassed or changed.
            df.replace(np.nan, '', inplace=True)
            df = df.astype(str)
            return df
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture ou de la conversion du fichier {file_path}: {e}")
            # self.set_error(file_path.name) # Base class might handle this in its loop
            raise # Re-raise for the base class to handle error file moving

    def _archive_data(self):
        """
        Custom method for LonasebetGlobal to archive data from the temporary table
        to the archive table after successful insertion into the temp table.
        This uses self.connexion and self.cursor established by the base Loader.
        """
        if not self.cursor:
            self.logger.error("Aucun curseur de base de données disponible pour archiver les données.")
            raise Exception("Cursor not initialized for _archive_data")

        try:
            # Delete existing data in archive table for the dates being processed
            delete_query = f"""
                DELETE FROM {self.db_archive_table_name}
                WHERE CAST(jour AS DATE) IN (
                    SELECT DISTINCT CAST(jour AS DATE) FROM {self.table_name}
                )
            """
            self.logger.info(f"Suppression des données existantes dans {self.db_archive_table_name} pour les jours concernés...")
            self.cursor.execute(delete_query)
            self.connexion.commit() # Use self.connexion from base class
            self.logger.info("Données existantes supprimées avec succès de la table d'archive.")

            # Insert data from temp table to archive table
            insert_archive_query = f"""
                INSERT INTO {self.db_archive_table_name} ({', '.join([f'[{col}]' for col in self.columns])})
                SELECT {', '.join([f'[{col}]' for col in self.columns])} FROM {self.table_name}
            """
            self.logger.info(f"Archivage des données de {self.table_name} vers {self.db_archive_table_name}...")
            self.cursor.execute(insert_archive_query)
            self.connexion.commit()
            self.logger.info("Données archivées avec succès.")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'archivage des données: {e}")
            # self.connexion.rollback() # If using transactions per operation
            raise

    def process_loading(self):
        """
        Overrides the base Loader's process_loading to:
        1. Consolidate data from all files before inserting (as per original insert_lonasebet_global.py).
        2. Add the custom _archive_data step.
        """
        self.logger.info(f"Démarrage du chargement personnalisé pour {self.name}...")

        self._connection_to_db() # Establish DB connection using base class method

        try:
            self._delete_table_datas() # Truncate the temp table using base class method

            all_data_to_load_tuples = []
            files_processed_successfully_paths = []

            # Glob files from source_path (set in base Loader __init__)
            for file_path in self.source_path.glob(self.file_pattern):
                try:
                    self.logger.info(f"Traitement du fichier pour consolidation : {file_path.name}")
                    df = self._convert_file_to_dataframe(file_path)
                    tuples_data = self._dataframe_to_tuples(df) # Use base class method
                    all_data_to_load_tuples.extend(tuples_data)
                    files_processed_successfully_paths.append(file_path)
                    self.logger.info(f"Fichier {file_path.name} consolidé pour chargement.")
                except Exception as e:
                    self.logger.error(f"Impossible de traiter le fichier {file_path.name} pour consolidation: {e}")
                    self.set_error(file_path.name) # Record error
                    move_file(file_path, self.error_path) # Move to error path

            if all_data_to_load_tuples:
                self.logger.info(f"Total de {len(all_data_to_load_tuples)} lignes à charger.")
                self._load_datas(all_data_to_load_tuples) # Load all consolidated data using base method

                # Archive data after successful load into temp table
                self._archive_data()

                # Move successfully processed and loaded files
                for file_path in files_processed_successfully_paths:
                    move_file(file_path, self.loaded_path)
                self.logger.info("Tous les fichiers traités et consolidés ont été déplacés vers le dossier 'loaded'.")
            else:
                self.logger.info("Aucune donnée à charger après consolidation des fichiers.")

            self.check_error() # Log summary of errors if any

        except Exception as e:
            self.logger.error(f"Erreur majeure lors du processus de chargement pour {self.name}: {e}")
            # Further error handling or re-raising might be needed
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connexion: # self.connexion is the name in base class
                self.connexion.close()
            self.logger.info("Connexion à la base de données fermée.")

def run_lonasebet_global_loader():
    loader = LonasebetGlobalLoad()
    loader.process_loading()

if __name__ == "__main__":
    run_lonasebet_global_loader()
