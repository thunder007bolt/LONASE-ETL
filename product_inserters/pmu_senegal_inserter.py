from .base_inserter import ProductInserter
from product_queries import pmu_senegal_queries
import pandas as pd
import numpy as np
import glob
from datetime import datetime, timedelta

class PmuSenegalInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path
        # date_debut est DD/MM/YYYY (correspond à la date des fichiers à lire)
        try:
            date_obj = datetime.strptime(self.date_debut, '%d/%m/%Y')
            self.file_date_str = date_obj.strftime('%Y-%m-%d') # Format YYYY-MM-DD pour les noms de fichiers
            self.year_debut_str = date_obj.strftime('%Y')
            # date_fin (pour les requêtes) est aussi self.date_debut dans ce contexte de chargement journalier
            date_obj_fin = datetime.strptime(self.date_fin, '%d/%m/%Y')
            self.year_fin_str = date_obj_fin.strftime('%Y')

        except ValueError as e:
            if self.logger:
                self.logger.error(f"Erreur de format de date pour PmuSenegalInserter ({self.date_debut} ou {self.date_fin}): {e}")
            raise

        self.ca_file_pattern_template = self.base_path + rf"PMUSENEGAL/**/Pmu_Senegal_ca_{self.file_date_str}.csv"
        self.lots_file_pattern_template = self.base_path + rf"PMUSENEGAL/**/Pmu_Senegal_lots_{self.file_date_str}.csv"

    def get_queries(self) -> dict[str, str]:
        return pmu_senegal_queries.get_queries()

    def _read_csv_to_df(self, file_pattern: str, columns: list[str], encoding: str = 'utf-8') -> pd.DataFrame | None:
        """Lit un fichier CSV et le retourne en DataFrame, ou None si non trouvé/erreur."""
        files = glob.glob(file_pattern, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour le pattern: {file_pattern}")
            return None

        file_path = files[0]
        if self.logger:
            self.logger.info(f"Lecture du fichier: {file_path}")
        try:
            df = pd.read_csv(file_path, sep=';', index_col=False, dtype=str, encoding=encoding)
            df = pd.DataFrame(df, columns=columns) # Assure l'ordre et la présence des colonnes
            df = df.replace(np.nan, '')
            return df
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            return None

    def load_data(self, data_ca: pd.DataFrame = None, data_lots: pd.DataFrame = None):
        """
        Charge les données pour PmuSenegal après que les CSV ont été lus.
        """
        self._connect_db()
        try:
            queries = self.get_queries()
            # Params pour les requêtes (date_debut et date_fin sont au format DD/MM/YYYY)
            params_dates_simple = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
            params_dates_merge_dtm_ca = {
                'year_debut': self.year_debut_str,
                'year_fin': self.year_fin_str
                # Note: la requête originale utilise aussi debut/fin pour Te.ANNEEC in,
                # mais ici on passe les années pour être plus précis si la requête est adaptée.
                # Si la requête reste Te.ANNEEC in ('{debut_year}', '{fin_year}'),
                # alors il faut passer ces années comme chaînes.
            }


            # 1. Truncate temp tables
            if 'truncate_temp_ca' in queries:
                self._execute_query('truncate_temp_ca')
            if 'truncate_temp_lots' in queries:
                self._execute_query('truncate_temp_lots')

            # 2. Insert data from DataFrames into temp tables
            if data_ca is not None and not data_ca.empty:
                self.insert_dataframe_to_temp(data_ca, query_key='insert_temp_ca')
            else:
                if self.logger: self.logger.info("Pas de données CA à insérer dans la table temporaire.")

            if data_lots is not None and not data_lots.empty:
                self.insert_dataframe_to_temp(data_lots, query_key='insert_temp_lots')
            else:
                if self.logger: self.logger.info("Pas de données Lots à insérer dans la table temporaire.")

            # 3. SQL operations from the original chargePmuSenegal function
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates_simple)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates_simple)

            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente')
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots')

            if 'merge_dtm_ca_daily' in queries:
                self._execute_query('merge_dtm_ca_daily', params=params_dates_simple)

            # Pour merge_dtm_ca_original, les paramètres de date sont formatés dans la requête elle-même
            # dans le script original. Ici, nous passons les années.
            # La requête SQL elle-même devra être adaptée si elle utilise f-string pour les années.
            # Ou alors, on passe date_debut, date_fin et la requête utilise TO_CHAR pour extraire l'année.
            # Le fichier de requêtes a :year_debut, :year_fin
            if 'merge_dtm_ca_original' in queries:
                 self._execute_query('merge_dtm_ca_original', params=params_dates_merge_dtm_ca)

            # Archive
            if 'delete_archive_ca' in queries:
                self._execute_query('delete_archive_ca')
            if 'delete_archive_lots' in queries:
                self._execute_query('delete_archive_lots')
            if 'insert_archive_ca' in queries:
                self._execute_query('insert_archive_ca')
            if 'insert_archive_lots' in queries:
                self._execute_query('insert_archive_lots')

            # Final truncate of temp tables (already done at the beginning, but good for idempotency)
            if 'truncate_temp_ca' in queries: # Re-truncate
                self._execute_query('truncate_temp_ca')
            if 'truncate_temp_lots' in queries: # Re-truncate
                self._execute_query('truncate_temp_lots')

            if self.logger:
                self.logger.info(f"Processus load_data (opérations BDD) complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # generalDirectory est dans self.base_path
        """
        Orchestre la lecture des fichiers CSV pour PMU Senegal et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement PMU Senegal. Date pour fichiers: {self.file_date_str}")
            self.logger.info(f"Période de données du {self.date_debut} au {self.date_fin}")

        df_ca = self._read_csv_to_df(
            file_pattern=self.ca_file_pattern_template,
            columns=['PRODUIT','CA','SHARING','JOUR','ANNEE','MOIS']
        )

        df_lots = self._read_csv_to_df(
            file_pattern=self.lots_file_pattern_template,
            columns=['Joueur','Nombre de fois gagné','Montant','Type','Combinaison','Offre','produit','JOUR','ANNEE','MOIS'],
            encoding='latin1' # Spécifié dans le script original
        )

        if df_ca is None and df_lots is None:
            if self.logger:
                self.logger.warning(f"Aucun fichier de données (CA ou Lots) trouvé pour PMU Senegal pour la date {self.file_date_str}. Traitement arrêté.")
            return

        self.load_data(data_ca=df_ca, data_lots=df_lots)

        if self.logger:
            self.logger.info(f"Fin du traitement PMU Senegal.")
