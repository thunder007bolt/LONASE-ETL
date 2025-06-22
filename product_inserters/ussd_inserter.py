from .base_inserter import ProductInserter
from product_queries import ussd_queries
import pandas as pd
import numpy as np
from datetime import datetime

class UssdInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path

        # date_debut est DD/MM/YYYY (correspond à start_date du script original)
        day_sd, month_sd, year_sd = self.date_debut.split('/')
        self.file_date_str = f"{year_sd}-{month_sd}-{day_sd}" # YYYY-MM-DD pour le nom de fichier
        self.file_pattern_template = rf"USSD/**/GFM_CDR_DETAILS_{self.file_date_str}.csv"

        # Pour les requêtes merge_dtm_ca_daily et merge_dtm_ca qui utilisent :current_year
        self.current_year_for_query = year_sd # Utiliser l'année de date_debut

    def get_queries(self) -> dict[str, str]:
        return ussd_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour USSD.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour UssdInserter. Chargement partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            params_merge_ca = {
                'date_debut': self.date_debut,
                'date_fin': self.date_fin,
                'current_year': self.current_year_for_query
            }

            if data is not None and not data.empty:
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')
                self.insert_dataframe_to_temp(data) # Utilise 'insert_temp'

                if 'insert_dim_terminal' in queries: # Se base sur la table temp
                    self._execute_query('insert_dim_terminal')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, étapes temp table sautées.")


            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            if data is not None and not data.empty: # Dépend des données chargées
                if 'insert_main_fait_vente' in queries:
                    self._execute_query('insert_main_fait_vente')
                if 'insert_main_fait_lots' in queries:
                    self._execute_query('insert_main_fait_lots')

            if 'merge_dtm_ca_daily' in queries: # Utilise current_year
                 self._execute_query('merge_dtm_ca_daily', params=params_merge_ca)
            if 'merge_dtm_ca' in queries: # Utilise current_year
                 self._execute_query('merge_dtm_ca', params=params_merge_ca)

            if data is not None and not data.empty: # Archivage et nettoyage si données traitées
                if 'delete_ar_ussd_ivr' in queries:
                    self._execute_query('delete_ar_ussd_ivr') # Se base sur le contenu de la temp
                if 'insert_ar_ussd_ivr' in queries:
                    self._execute_query('insert_ar_ussd_ivr')
                if 'truncate_temp' in queries: # Nettoyage final de la temp
                    self._execute_query('truncate_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")
        finally:
            self._close_db()

    def process(self, source_file_path: str): # generalDirectory
        """
        Orchestre la lecture du fichier et le chargement des données pour USSD.
        """
        if self.logger:
            self.logger.info(f"Début du traitement USSD pour la date de fichier : {self.file_date_str}")
            self.logger.info(f"Période de données du {self.date_debut} au {self.date_fin}")

        full_file_path = self.base_path + self.file_pattern_template

        if self.logger:
            self.logger.info(f"Recherche du fichier USSD avec pattern: {full_file_path}")

        files_found = glob.glob(full_file_path, recursive=True)
        data_df = None

        if not files_found:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour USSD (pattern: {full_file_path}).")
        else:
            actual_file_path = files_found[0]
            if self.logger:
                self.logger.info(f"Lecture du fichier: {actual_file_path}")
            try:
                data_df = pd.read_csv(actual_file_path, sep=';', index_col=False, dtype=str)

                # Transformations du script original:
                # data['Jour'] = pd.to_datetime(data['Jour'], errors='coerce').dt.strftime('%d/%m/%Y')
                # data['Date Appel'] = pd.to_datetime(data['Date Appel'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
                # data = pd.DataFrame(data, columns=['Date Appel', 'Jour', 'Numéro Serveur', 'Numéro Appelant', 'Durée Appel', 'Total Appels', 'Total CA'])
                # data = data.replace(np.nan, '')

                if 'Jour' in data_df.columns:
                    data_df['Jour'] = pd.to_datetime(data_df['Jour'], errors='coerce').dt.strftime('%d/%m/%Y')
                if 'Date Appel' in data_df.columns:
                     data_df['Date Appel'] = pd.to_datetime(data_df['Date Appel'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')

                expected_cols_temp = ['Date Appel', 'Jour', 'Numéro Serveur', 'Numéro Appelant', 'Durée Appel', 'Total Appels', 'Total CA']
                # S'assurer que toutes les colonnes existent, ajouter celles qui manquent avec des valeurs par défaut
                for col in expected_cols_temp:
                    if col not in data_df.columns:
                        data_df[col] = ''
                data_df = data_df[expected_cols_temp] # Sélectionner et réordonner
                data_df = data_df.replace(np.nan, '')

                if self.logger:
                    self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {actual_file_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {actual_file_path}: {e}")
                data_df = None # Assurer que load_data sait qu'il n'y a pas de données

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement USSD.")
