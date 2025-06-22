from .base_inserter import ProductInserter
from product_queries import mini_shop_queries
import pandas as pd
import numpy as np
import glob
from datetime import datetime

class MiniShopInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path
        # date_debut est DD/MM/YYYY (correspond à la date du fichier à lire)
        try:
            date_obj = datetime.strptime(self.date_debut, '%d/%m/%Y')
            self.file_date_str = date_obj.strftime('%Y-%m-%d') # Format YYYY-MM-DD pour nom de fichier
            self.year_debut_str = date_obj.strftime('%Y')
            # date_fin (pour les requêtes) est aussi self.date_debut dans ce contexte de chargement journalier
            date_obj_fin = datetime.strptime(self.date_fin, '%d/%m/%Y')
            self.year_fin_str = date_obj_fin.strftime('%Y')
        except ValueError as e:
            if self.logger:
                self.logger.error(f"Erreur de format de date pour MiniShopInserter ({self.date_debut} ou {self.date_fin}): {e}")
            raise

        self.file_pattern_template = self.base_path + rf"MINI_SHOP/**/minishop_{self.file_date_str}.csv"

    def get_queries(self) -> dict[str, str]:
        return mini_shop_queries.get_queries()

    def load_data(self, data_minishop: pd.DataFrame = None):
        """
        Charge les données pour MiniShop après que le CSV a été lu.
        """
        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates_simple = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            params_dates_merge_dtm_ca = {
                'year_debut': self.year_debut_str,
                'year_fin': self.year_fin_str
            }

            # 1. Truncate temp table
            if 'truncate_temp_minishop' in queries:
                self._execute_query('truncate_temp_minishop')

            # 2. Insert data from DataFrame into temp table
            if data_minishop is not None and not data_minishop.empty:
                self.insert_dataframe_to_temp(data_minishop, query_key='insert_temp_minishop')
            else:
                if self.logger:
                    self.logger.warning(f"Aucune donnée MiniShop à insérer dans la table temporaire pour la date {self.file_date_str}.")
                # On pourrait s'arrêter ici si les données sont absolument nécessaires pour la suite.
                # Cependant, le script original exécute les suppressions et merges même si le fichier est manquant.

            # 3. SQL operations from the original chargeMinishop function
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates_simple)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates_simple)

            # Les insertions dans DIM_TERMINAL se basent sur la table temporaire
            if data_minishop is not None and not data_minishop.empty:
                if 'insert_dim_terminal_existing_systems' in queries:
                    self._execute_query('insert_dim_terminal_existing_systems')
                if 'insert_dim_terminal_solidicon' in queries:
                    self._execute_query('insert_dim_terminal_solidicon')

                if 'insert_main_fait_vente' in queries:
                    self._execute_query('insert_main_fait_vente')
                if 'insert_main_fait_lots' in queries:
                    self._execute_query('insert_main_fait_lots')

                if 'merge_dtm_mini_shop' in queries:
                    self._execute_query('merge_dtm_mini_shop')

            # Merges CA (exécutés même si pas de nouvelles données, pour la cohérence avec script original)
            if 'merge_dtm_ca_daily_minishop' in queries:
                self._execute_query('merge_dtm_ca_daily_minishop', params=params_dates_simple)
            if 'merge_dtm_ca_daily_virtuelshop' in queries:
                self._execute_query('merge_dtm_ca_daily_virtuelshop', params=params_dates_simple)

            if 'merge_dtm_ca_minishop' in queries:
                self._execute_query('merge_dtm_ca_minishop', params=params_dates_merge_dtm_ca)
            if 'merge_dtm_ca_virtuelshop' in queries:
                self._execute_query('merge_dtm_ca_virtuelshop', params=params_dates_merge_dtm_ca)

            # Archive and final truncate (seulement si des données ont été chargées dans la temp)
            if data_minishop is not None and not data_minishop.empty:
                if 'delete_archive_minishop' in queries: # Se base sur le contenu de la temp
                    self._execute_query('delete_archive_minishop')
                if 'insert_archive_minishop' in queries:
                    self._execute_query('insert_archive_minishop')
                if 'truncate_temp_minishop' in queries: # Re-truncate
                    self._execute_query('truncate_temp_minishop')

            if self.logger:
                self.logger.info(f"Processus load_data (opérations BDD) complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # generalDirectory est dans self.base_path
        """
        Orchestre la lecture du fichier CSV pour MiniShop et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement MiniShop. Date pour fichier: {self.file_date_str}")
            self.logger.info(f"Période de données du {self.date_debut} au {self.date_fin}")

        data_df = None
        files = glob.glob(self.file_pattern_template, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour MiniShop avec le pattern: {self.file_pattern_template}")
        else:
            file_to_process = files[0]
            if self.logger:
                self.logger.info(f"Lecture du fichier: {file_to_process}")
            try:
                data_df = pd.read_csv(file_to_process, sep=';', index_col=False, dtype=str)
                # Colonnes attendues par le script original pour le DataFrame après lecture:
                # ['DATE', 'ETABLISSEMENT', 'JEU', 'TERMINAL', 'VENDEUR', 'MONTANT A VERSER', 'MONTANT A PAYER']
                expected_cols = ['DATE', 'ETABLISSEMENT', 'JEU', 'TERMINAL', 'VENDEUR', 'MONTANT A VERSER', 'MONTANT A PAYER']
                data_df = pd.DataFrame(data_df, columns=expected_cols) # S'assure de l'ordre et des noms
                # data_df = data_df.astype(str) # Déjà fait par dtype=str dans read_csv
                data_df = data_df.replace(np.nan, '') # Remplacer les NaN par des chaînes vides

                if self.logger:
                    self.logger.info(f"{len(data_df)} lignes lues depuis {file_to_process}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la lecture du fichier {file_to_process}: {e}")
                data_df = None # Assurer que load_data sait qu'il n'y a pas de données

        self.load_data(data_minishop=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement MiniShop.")
