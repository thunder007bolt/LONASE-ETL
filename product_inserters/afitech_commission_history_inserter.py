from .base_inserter import ProductInserter
from product_queries import afitech_commission_history_queries
import pandas as pd
import numpy as np
import glob
from datetime import datetime, timedelta

class AfitechCommissionHistoryInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path

        # date_debut est DD/MM/YYYY (correspond à start_date du script original)
        # date_fin est DD/MM/YYYY (correspond à end_date du script original)

        # Pour le nom du fichier AFITECH_CommissionHistory {firstDay}_{start_date}.csv
        # start_date pour le nom du fichier est self.date_debut formaté en YYYY-MM-DD
        day_sd, month_sd, year_sd = self.date_debut.split('/')
        self.start_date_for_file = f"{year_sd}-{month_sd}-{day_sd}"

        # firstDay est le premier jour du mois de self.date_debut
        current_date_obj = datetime.strptime(self.date_debut, '%d/%m/%Y')
        self.first_day_of_month_for_file = current_date_obj.replace(day=1).strftime('%Y-%m-%d')

        self.file_pattern_template = r"AFITECH/CommissionHistory/**/AFITECH_CommissionHistory {first_day}_{start_date}.csv"

        # Pour la requête delete_main_dtm_table qui utilise :first_day_of_month et :date_fin
        # self.date_fin est déjà au bon format DD/MM/YYYY
        self.first_day_of_month_for_query = current_date_obj.replace(day=1).strftime('%d/%m/%Y')


    def get_queries(self) -> dict[str, str]:
        return afitech_commission_history_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour AFITECH Commission History.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour AfitechCommissionHistoryInserter. Le chargement sera partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            # params_dates pour delete_main_dtm_table
            params_delete = {
                'first_day_of_month': self.first_day_of_month_for_query,
                'date_fin': self.date_fin # self.date_fin correspond à end_date du script original
            }

            if data is not None and not data.empty:
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')
                self.insert_dataframe_to_temp(data)
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, les étapes liées à la table temporaire sont sautées.")


            if 'delete_main_dtm_table' in queries:
                self._execute_query('delete_main_dtm_table', params=params_delete)

            if data is not None and not data.empty: # L'insertion dépend des données chargées
                if 'insert_main_dtm_table' in queries:
                    self._execute_query('insert_main_dtm_table') # Se base sur la table temp et DIM_TEMPS

                if 'cleanup_temp' in queries:
                    self._execute_query('cleanup_temp')

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # generalDirectory
        """
        Orchestre la lecture du fichier et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Afitech Commission History. Période: {self.date_debut} - {self.date_fin}")
            self.logger.info(f"Cherche fichier avec first_day={self.first_day_of_month_for_file}, start_date={self.start_date_for_file}")


        file_to_load = self.file_pattern_template.format(
            first_day=self.first_day_of_month_for_file,
            start_date=self.start_date_for_file
        )
        full_file_path_pattern = self.base_path + file_to_load

        if self.logger:
            self.logger.info(f"Pattern de fichier complet: {full_file_path_pattern}")

        files_found = glob.glob(full_file_path_pattern, recursive=True)
        data_df = None

        if not files_found:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour Afitech Commission History (pattern: {full_file_path_pattern}).")
            # On continue pour exécuter le delete sur DTM si besoin, même si pas de nouvelles données.
        else:
            actual_file_path = files_found[0]
            if self.logger:
                self.logger.info(f"Lecture du fichier: {actual_file_path}")
            try:
                data_df = pd.read_csv(actual_file_path, sep=';', index_col=False, dtype=str)
                # Transformation des données comme dans le script original
                data_df = data_df.replace(np.nan, '')
                # Remplacer '.' par ',' sauf pour la colonne 'Partner'
                cols_to_transform = [col for col in data_df.columns if col != 'Partner']
                for col in cols_to_transform:
                    if data_df[col].dtype == 'object': # S'applique seulement aux colonnes string/object
                        data_df[col] = data_df[col].str.replace('.', ',', regex=False)

                # Reformater les dates si nécessaire (le script original le fait après le remplacement point/virgule)
                if 'Début de la période' in data_df.columns:
                    data_df['Début de la période'] = data_df['Début de la période'].str.replace('-', '/', regex=False)
                if 'Fin de la période' in data_df.columns:
                    data_df['Fin de la période'] = data_df['Fin de la période'].str.replace('-', '/', regex=False)


                # Mapping des noms de colonnes du CSV vers ceux de la table temporaire
                # "DEBUT_PERIODE", "FIN_PERIODE", "PARTNER", "PAYEMENT_PROVIDER", "TOTAL_COMMISSON",
                # "DEPOSIT_TOTAL_AMOUNT", "DEPOSIT_COUNT", "WITHDRAWAL_TOTAL_AMOUNT", "WITHDRAWAL_COUNT"
                rename_map = {
                    "Début de la période": "DEBUT_PERIODE",
                    "Fin de la période": "FIN_PERIODE",
                    "Partner": "PARTNER", # Majuscule P dans le CSV
                    "Payment Provider": "PAYEMENT_PROVIDER", # Espace dans le CSV
                    "Total Commission": "TOTAL_COMMISSON", # 2 S à commission
                    "Total Amount of Deposit": "DEPOSIT_TOTAL_AMOUNT",
                    "Total Number of Deposit": "DEPOSIT_COUNT",
                    "Total Amount of Withdrawals": "WITHDRAWAL_TOTAL_AMOUNT",
                    "Total Number of Withdrawals": "WITHDRAWAL_COUNT"
                }
                data_df.rename(columns=rename_map, inplace=True)

                expected_cols = list(rename_map.values())
                data_df = data_df[expected_cols]


                if self.logger:
                    self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {actual_file_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {actual_file_path}: {e}")
                # Ne pas lever d'exception pour permettre le delete sur DTM
                data_df = None # Assurer que load_data sait qu'il n'y a pas de données

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Afitech Commission History.")
