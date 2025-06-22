from .base_inserter import ProductInserter
from product_queries import sunubet_queries
import pandas as pd
import numpy as np
import glob

class SunubetInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path: str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path

        # date_debut est DD/MM/YYYY (correspond à start_date du script original)
        day_sd, month_sd, year_sd = self.date_debut.split('/')
        self.file_date_str = f"{year_sd}-{month_sd}-{day_sd}" # YYYY-MM-DD pour les noms de fichiers

        self.online_file_pattern = rf"SUNUBET/ONLINE/**/onlineSunubet {self.file_date_str}.csv"
        self.casino_file_pattern = rf"SUNUBET/CASINO/**/casinoSunubet {self.file_date_str}.csv"

    def get_queries(self) -> dict[str, str]:
        return sunubet_queries.get_queries()

    def _load_sunubet_type_to_temp(self, file_pattern_template: str, product_type: str, temp_truncate_key: str, temp_insert_key: str, col_rename_map: dict, expected_cols: list):
        """Charge un type de fichier Sunubet (Online ou Casino) dans sa table temporaire dédiée."""
        full_file_pattern = self.base_path + file_pattern_template
        if self.logger:
            self.logger.info(f"Recherche du fichier Sunubet ({product_type}) avec pattern: {full_file_pattern}")

        files = glob.glob(full_file_pattern, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour Sunubet {product_type} (pattern: {full_file_pattern}).")
            return False

        file_path = files[0]
        if self.logger:
            self.logger.info(f"Lecture du fichier {file_path} pour Sunubet {product_type}")

        try:
            data_df = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
            data_df.rename(columns=col_rename_map, inplace=True)
            data_df = data_df.replace(np.nan, '')

            # S'assurer que toutes les colonnes attendues sont présentes et dans le bon ordre
            for col in expected_cols:
                if col not in data_df.columns:
                    data_df[col] = ''
            data_df = data_df[expected_cols]

            self._execute_query(temp_truncate_key)
            # La méthode `insert_dataframe_to_temp` doit être capable d'utiliser une clé de requête spécifique
            self.insert_dataframe_to_temp(data_df, query_key=temp_insert_key)

            if self.logger:
                self.logger.info(f"Données de {file_path} (Sunubet {product_type}) chargées dans sa table temporaire.")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chargement du fichier {file_path} (Sunubet {product_type}): {e}")
            return False

    def load_data(self, data: pd.DataFrame = None): # data n'est pas utilisé directement
        """
        Charge les données pour Sunubet.
        Les chargements des fichiers dans les tables temporaires sont gérés par `process`.
        Cette méthode se concentre sur les opérations BDD après le remplissage des tables temporaires.
        """
        # La connexion est gérée par process() pour le chargement des temp, puis ici.
        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            # Merge Online data into DTM_MISE_SUNUBET_ONLINE
            if 'merge_dtm_mise_sunubet_online_from_online' in queries:
                self._execute_query('merge_dtm_mise_sunubet_online_from_online', params=params_dates)

            # Merge Casino data into DTM_MISE_SUNUBET_ONLINE
            if 'merge_dtm_mise_sunubet_online_from_casino' in queries:
                self._execute_query('merge_dtm_mise_sunubet_online_from_casino', params=params_dates)

            # Nettoyage des tables temporaires après le merge
            if 'truncate_temp_online' in queries: # Clé pour SRC_PRD_SUNUBET_ONLINE
                 self._execute_query('truncate_temp_online')
            if 'truncate_temp_casino' in queries: # Clé pour SRC_PRD_SUNUBET_CASINO
                 self._execute_query('truncate_temp_casino')

            if self.logger:
                self.logger.info(f"Processus load_data (opérations BDD) complété pour {self.__class__.__name__}.")
        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # generalDirectory
        """
        Orchestre la lecture des fichiers Sunubet Online et Casino et le chargement des données.
        """
        if self.logger:
            self.logger.info(f"Début du traitement Sunubet (Online & Casino). Période: {self.date_debut} - {self.date_fin}")
            self.logger.info(f"Cherche fichiers avec date={self.file_date_str}")

        online_loaded = False
        casino_loaded = False

        # Gérer la connexion BDD pour les opérations sur les tables temporaires
        self._connect_db()
        try:
            # Charger Sunubet Online
            online_rename_map = {
                "JOUR": "ISSUEDATETIME", "Stake": "STAKE", "PaidAmount": "PAIDAMOUNT",
                "BetCategory": "BETCATEGORYTYPE", "Freebet": "FREEBET"
            }
            online_expected_cols = ["ISSUEDATETIME", "STAKE", "PAIDAMOUNT", "BETCATEGORYTYPE", "FREEBET"]
            online_loaded = self._load_sunubet_type_to_temp(
                file_pattern_template=self.online_file_pattern,
                product_type="Online",
                temp_truncate_key='truncate_temp_online',
                temp_insert_key='insert_temp_online',
                col_rename_map=online_rename_map,
                expected_cols=online_expected_cols
            )

            # Charger Sunubet Casino
            casino_rename_map = {"JOUR": "ISSUEDATETIME", "Stake": "STAKE", "PaidAmount": "PAIDAMOUNT"}
            casino_expected_cols = ["ISSUEDATETIME", "STAKE", "PAIDAMOUNT"]
            casino_loaded = self._load_sunubet_type_to_temp(
                file_pattern_template=self.casino_file_pattern,
                product_type="Casino",
                temp_truncate_key='truncate_temp_casino',
                temp_insert_key='insert_temp_casino',
                col_rename_map=casino_rename_map,
                expected_cols=casino_expected_cols
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur critique pendant le chargement des fichiers Sunubet: {e}")
            if self.conn: self._close_db()
            raise
        finally:
            if self.conn: # Fermer la connexion après le chargement des fichiers temp
                self._close_db()

        if not (online_loaded or casino_loaded):
            if self.logger:
                self.logger.warning(f"Aucun fichier Sunubet Online ou Casino trouvé pour la date {self.file_date_str}. "
                                 "Les opérations sur la base de données principale seront exécutées mais pourraient ne rien traiter.")

        # Appeler la logique de base de données principale (merge, cleanup)
        self.load_data() # gère sa propre connexion

        if self.logger:
            self.logger.info(f"Fin du traitement Sunubet (Online & Casino).")
