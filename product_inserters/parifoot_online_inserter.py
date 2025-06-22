from .base_inserter import ProductInserter
from product_queries import parifoot_online_queries
import pandas as pd
import numpy as np

class ParifootOnlineInserter(ProductInserter): # PremierBet
    def get_queries(self) -> dict[str, str]:
        return parifoot_online_queries.get_queries()

    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour Parifoot Online (PremierBet).
        """
        if data is None or data.empty:
            if self.logger:
                self.logger.warning(f"Aucune donnée pour ParifootOnlineInserter. Chargement partiel.")

        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            if data is not None and not data.empty:
                if 'truncate_temp' in queries:
                    self._execute_query('truncate_temp')

                # La requête d'insertion est complexe, on s'assure que le DataFrame est bien formaté.
                # La méthode `insert_dataframe_to_temp` est utilisée.
                self.insert_dataframe_to_temp(data) # Utilise 'insert_temp'

                if 'remove_total_from_temp' in queries: # Spécifique à PremierBet
                    self._execute_query('remove_total_from_temp')
            else:
                if self.logger:
                    self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, étapes temp table sautées.")


            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            if data is not None and not data.empty: # Ces insertions dépendent des données chargées
                if 'insert_main_fait_vente' in queries: # Utilise la table temp
                    self._execute_query('insert_main_fait_vente')
                if 'insert_main_fait_lots' in queries: # Utilise la table temp
                    self._execute_query('insert_main_fait_lots')
                if 'insert_fact_parifoot_online' in queries: # Utilise la table temp
                    self._execute_query('insert_fact_parifoot_online')
                if 'insert_fact_voucher' in queries: # Se base sur FACT_PARIFOOT_ONLINE
                     self._execute_query('insert_fact_voucher')

                # Archivage et nettoyage
                if 'delete_ar_premierbet' in queries: # Se base sur le contenu de la temp pour les dates
                    self._execute_query('delete_ar_premierbet')
                if 'insert_ar_premierbet' in queries:
                    self._execute_query('insert_ar_premierbet')
                if 'cleanup_temp' in queries:
                    self._execute_query('cleanup_temp')

            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")
        finally:
            self._close_db()

    def process(self, source_file_path: str):
        """
        Orchestre la lecture du fichier et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Parifoot Online (PremierBet) pour le fichier : {source_file_path}")
            self.logger.info(f"Période du {self.date_debut} au {self.date_fin}")

        data_df = None
        try:
            data_df = pd.read_csv(source_file_path, sep=';', index_col=False, dtype=str)
            # Colonnes du CSV: 'Unnamed: 0','Username', 'Balance', ..., 'date'
            # Requête insert_temp attend 27 colonnes.
            # Le script original fait: data = pd.DataFrame(data,columns=['Unnamed: 0',...'date'])
            # Cela implique que les noms de colonnes du CSV sont déjà ceux attendus par le script ou qu'ils sont forcés.
            # Nous allons supposer que le CSV a les bons noms ou qu'ils sont mappés correctement.
            # La requête d'insertion est:
            # INSERT INTO OPTIWARETEMP.SRC_PRD_PREMIERBET("ID","Username", ..., "Date") VALUES(:1, ..., :27)

            # Renommer la première colonne si elle s'appelle 'Unnamed: 0' en 'ID'
            if 'Unnamed: 0' in data_df.columns:
                data_df.rename(columns={'Unnamed: 0': 'ID'}, inplace=True)
            if 'date' in data_df.columns: # La requête attend "Date" avec un D majuscule
                 data_df.rename(columns={'date': 'Date'}, inplace=True)

            data_df = data_df.replace(np.nan, '')

            # S'assurer que les 27 colonnes attendues par la requête `insert_temp` sont présentes et dans le bon ordre.
            # Ceci est crucial car `insert_dataframe_to_temp` convertit le df en tuples.
            expected_cols = [
                "ID","Username", "Balance", "Total Players","Total Players Date Range",
                "SB Bets No.", "SB Stake","SB Closed Stake", "SB Wins No.", "SB Wins",
                "SB Ref No.", "SB Refunds","SB GGR", "Cas.Bets No.", "Cas.Stake",
                "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR",
                "Total GGR", "Adjustments","Deposits", "Financial Deposits",
                "Financial Withdrawals","Transaction Fee", "Date"
            ]
            # S'assurer que toutes les colonnes existent, ajouter celles qui manquent avec des valeurs par défaut (chaîne vide)
            for col in expected_cols:
                if col not in data_df.columns:
                    data_df[col] = ''
            data_df = data_df[expected_cols] # Sélectionner et réordonner


            if self.logger:
                self.logger.info(f"{len(data_df)} lignes lues et préparées depuis {source_file_path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture ou préparation du fichier {source_file_path}: {e}")
            raise

        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement Parifoot Online (PremierBet) pour le fichier : {source_file_path}")
