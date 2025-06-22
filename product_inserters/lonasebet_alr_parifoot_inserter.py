from .base_inserter import ProductInserter
from product_queries import lonasebet_alr_parifoot_queries
import pandas as pd
import numpy as np

class LonasebetAlrParifootInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return lonasebet_alr_parifoot_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Lonasebet ALR et Parifoot.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour LonasebetAlrParifootInserter. Chargement partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {
                'date_debut': self.date_debut,
                'date_fin': self.date_fin,
                'year_debut': self.date_debut.split('/')[2], # Pour la requête merge_dtm_ca_virtuel
                'year_fin': self.date_fin.split('/')[2]   # Pour la requête merge_dtm_ca_virtuel
            }


            if data is not None and not data.empty:
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')
                self.insert_dataframe_to_temp(data)
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, étapes temp table sautées.")

            # Deletes
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # Inserts
            if data is not None and not data.empty: # Dépend des données chargées
                if 'insert_main_fait_vente' in queries:
                    self._execute_query('insert_main_fait_vente')
                if 'insert_main_fait_lots' in queries:
                    self._execute_query('insert_main_fait_lots')

            # Merges
            if 'merge_dtm_ca_daily_alr' in queries:
                 self._execute_query('merge_dtm_ca_daily_alr', params=params_dates)
            if 'merge_dtm_ca_daily_parifoot' in queries:
                 self._execute_query('merge_dtm_ca_daily_parifoot', params=params_dates)
            if 'merge_dtm_ca_daily_virtuel' in queries: # Concerne idjeux 467 qui est aussi dans ce flux
                 self._execute_query('merge_dtm_ca_daily_virtuel', params=params_dates)
            if 'merge_dtm_ca_virtuel' in queries: # Concerne idjeux 467
                 self._execute_query('merge_dtm_ca_virtuel', params=params_dates) # year_debut/fin sont dans params_dates

            if data is not None and not data.empty and 'cleanup_temp' in queries:
                 self._execute_query('cleanup_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")
        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Lonasebet ALR/Parifoot pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: "BetId","JOUR","Stake","BetCategory","State","PaidAmount","CustomerLogin","Freebet"
            # Requête insert_temp: "ID","ISSUEDATETIME","STAKE","BETCATEGORYTYPE","STATE","PAIDAMOUNT","CUSTOMERLOGIN","FREEBET"
            rename_map = {
                "BetId": "ID",
                "JOUR": "ISSUEDATETIME", # JOUR dans le CSV correspond à ISSUEDATETIME
                "Stake": "STAKE",
                "BetCategory": "BETCATEGORYTYPE",
                "State": "STATE",
                "PaidAmount": "PAIDAMOUNT",
                "CustomerLogin": "CUSTOMERLOGIN",
                "Freebet": "FREEBET"
            }
            data_df.rename(columns=rename_map, inplace=True)
            data_df = data_df.replace(np.nan, '')

            expected_cols = list(rename_map.values())
            data_df = data_df[expected_cols]

            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {source_file_path}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Lonasebet ALR/Parifoot pour le fichier : {source_file_path}")
