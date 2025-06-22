from .base_inserter import ProductInserter
from product_queries import lonasebet_casino_queries
import pandas as pd
import numpy as np

class LonasebetCasinoInserter(ProductInserter):
    def get_queries(self) -> dict[str, str]:
        return lonasebet_casino_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Lonasebet Casino.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour LonasebetCasinoInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                # 1. Truncate table temporaire (SRC_PRD_CASINO_LONASEBET)
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # 2. Insert into table temporaire
                self.insert_dataframe_to_temp(data)
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes liées à la table temporaire sont sautées.")

            # 3. Delete from table principale (FAIT_VENTE et FAIT_LOTS)
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # 4. Insert into table principale from table temporaire (FAIT_VENTE et FAIT_LOTS)
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            # 5. Opération de MERGE pour dtm_ca_daily
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            # 6. Nettoyage de la table temporaire
            if data is not None and not data.empty and'cleanup_temp' in queries:
                 self._execute_query('cleanup_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données pour Lonasebet Casino.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Lonasebet Casino pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: "JOUR","Stake","PaidAmount"
            # Requête insert_temp: DATE_VENTE,MISE_TOTALE, SOMME_PAYEE
            rename_map = {
                'JOUR': 'DATE_VENTE',
                'Stake': 'MISE_TOTALE',
                'PaidAmount': 'SOMME_PAYEE'
            }
            data_df.rename(columns=rename_map, inplace=True)
            data_df = data_df.replace(np.nan, '') # Comme dans le script original

            # S'assurer que les colonnes attendues sont présentes
            expected_cols = ["DATE_VENTE", "MISE_TOTALE", "SOMME_PAYEE"]
            data_df = data_df[expected_cols]


            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Lonasebet Casino pour le fichier : {source_file_path}")
