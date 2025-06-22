from .base_inserter import ProductInserter
from product_queries import afitech_daily_payment_activity_queries
import pandas as pd
import numpy as np
import glob
from datetime import datetime

class AfitechDailyPaymentActivityInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path

        # date_debut est DD/MM/YYYY (correspond à start_date du script original)
        # date_fin est DD/MM/YYYY (correspond à end_date du script original)

        # Pour le nom du fichier AFITECH_DailyPaymentActivity {start_date}_{start_date}.csv (note: le script original utilise start_date deux fois)
        # Nous utilisons self.date_debut (qui est start_date) pour le nom du fichier.
        day_sd, month_sd, year_sd = self.date_debut.split('/')
        self.file_date_str = f"{year_sd}-{month_sd}-{day_sd}"

        self.file_pattern_template = r"AFITECH/DailyPaymentActivity/**/AFITECH_DailyPaymentActivity {date_str}_{date_str}.csv"

    def get_queries(self) -> dict[str, str]:
        return afitech_daily_payment_activity_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour AFITECH Daily Payment Activity.
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour AfitechDailyPaymentActivityInserter. Chargement partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')
                self.insert_dataframe_to_temp(data)
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, étapes temp table sautées.")

            if 'delete_main_dtm_table' in queries:
                self._execute_query('delete_main_dtm_table', params=params_dates)

            if data is not None and not data.empty: # L'insertion dépend des données
                if 'insert_main_dtm_table' in queries:
                    self._execute_query('insert_main_dtm_table')

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
            self.logger.info(f"Début du traitement Afitech Daily Payment Activity. Période: {self.date_debut} - {self.date_fin}")
            self.logger.info(f"Cherche fichier avec date={self.file_date_str}")

        file_to_load = self.file_pattern_template.format(date_str=self.file_date_str)
        full_file_path_pattern = self.base_path + file_to_load

        if self.logger:
            self.logger.info(f"Pattern de fichier complet: {full_file_path_pattern}")

        files_found = glob.glob(full_file_path_pattern, recursive=True)
        data_df = None

        if not files_found:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour Afitech Daily Payment (pattern: {full_file_path_pattern}).")
        else:
            actual_file_path = files_found[0]
            if self.logger:
                self.logger.info(f"Lecture du fichier: {actual_file_path}")
            try:
                data_df = pd.read_csv(actual_file_path, sep=';', index_col=False, dtype=str)

                # Transformations du script original:
                # data['Date'] = [str(datetime.strptime(i, '%d/%m/%Y').strftime('%Y-%m-%d')) for i in data['Date']]
                # data = data.replace(np.nan, '')
                # data = data.applymap(lambda x: str(x).replace('.',','))
                # data['Partner'] = data['Partner'].str.replace(',', '.',regex=False)
                # data['Date'] = data['Date'].str.replace('-', '/',regex=False)

                if 'Date' in data_df.columns:
                    data_df['Date'] = [str(datetime.strptime(i, '%d/%m/%Y').strftime('%Y-%m-%d')) if pd.notna(i) and i.strip() else None
                                       for i in data_df['Date']]

                data_df = data_df.replace(np.nan, '')

                cols_to_transform = [col for col in data_df.columns if col not in ['Partner', 'Date']]
                for col in cols_to_transform:
                    if data_df[col].dtype == 'object':
                        data_df[col] = data_df[col].str.replace('.', ',', regex=False)

                if 'Partner' in data_df.columns and data_df['Partner'].dtype == 'object':
                     data_df['Partner'] = data_df['Partner'].str.replace(',', '.', regex=False)

                if 'Date' in data_df.columns and data_df['Date'].dtype == 'object':
                    data_df['Date'] = data_df['Date'].str.replace('-', '/', regex=False)


                # Mapping des noms de colonnes du CSV vers ceux de la table temporaire
                # "JOUR", "PARTNER", "PAYMENT_PROVIDER", "TOTAL_AMOUNT_OF_DEPOSIT", "TOTAL_NUMBER_OF_DEPOSIT",
                # "TOTAL_AMOUNT_OF_WITHDRAWALS", "TOTAL_NUMBER_OF_WITHDRAWALS", "TOTAL_COMMISSIONS"
                rename_map = {
                    "Date": "JOUR", # Après transformation, Date est YYYY/MM/DD
                    "Partner": "PARTNER",
                    "Payment Provider": "PAYMENT_PROVIDER",
                    "Total Amount of Deposit": "TOTAL_AMOUNT_OF_DEPOSIT",
                    "Total Number of Deposit": "TOTAL_NUMBER_OF_DEPOSIT",
                    "Total Amount of Withdrawals": "TOTAL_AMOUNT_OF_WITHDRAWALS",
                    "Total Number of Withdrawals": "TOTAL_NUMBER_OF_WITHDRAWALS",
                    "Total Commissions": "TOTAL_COMMISSIONS"
                    # "T_AMOUNT_OF_PARTNER_DEPOSITS", "T_AM_OF_PARTNER_WITHDRAWALS" ne sont pas dans le mapping car non utilisés dans les requêtes suivantes.
                }
                data_df.rename(columns=rename_map, inplace=True)

                expected_cols = list(rename_map.values())
                data_df = data_df[expected_cols] # Sélectionner et réordonner

                if self.logger:
                    self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {actual_file_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {actual_file_path}: {e}")
                data_df = None

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Afitech Daily Payment Activity.")
