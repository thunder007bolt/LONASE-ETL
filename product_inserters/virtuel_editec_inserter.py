from .base_inserter import ProductInserter
from product_queries import virtuel_editec_queries
import pandas as pd
import numpy as np
import glob # Pour trouver les fichiers

class VirtuelEditecInserter(ProductInserter):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None, base_path:str = ""):
        super().__init__(db_config, date_debut, date_fin, logger)
        self.base_path = base_path # K:\DATA_FICHIERS\

    def get_queries(self) -> dict[str, str]:
        return virtuel_editec_queries.get_queries()

    def _load_single_temp_table(self, file_pattern: str, columns: list[str], temp_table_truncate_key: str, temp_table_insert_key: str, sep: str = ';'):
        """
        Charge un fichier CSV dans une table temporaire spécifiée.
        """
        # Construire le chemin complet du pattern de fichier
        # date_debut est au format 'DD/MM/YYYY', nous avons besoin de YYYY-MM-DD pour le nom de fichier
        # ou du format utilisé par le script original (YYYY-MM-DD)
        # Le script original utilise str(start_date) qui donne YYYY-MM-DD
        # Notre self.date_debut est DD/MM/YYYY, il faut le convertir pour le nom du fichier.
        try:
            day, month, year = self.date_debut.split('/')
            date_for_file = f"{year}-{month}-{day}"
        except ValueError:
            if self.logger:
                self.logger.error(f"Format de date_debut incorrect ({self.date_debut}) pour construire le nom de fichier. Attendu DD/MM/YYYY.")
            # Utiliser self.date_debut directement si c'est déjà YYYY-MM-DD, ou gérer l'erreur.
            # Pour l'instant, on suppose que date_debut est bien DD/MM/YYYY.
            # Le script original utilise start_date (qui est la veille de end_date)
            # Si self.date_debut correspond à 'debut' (start_date du script original), alors c'est bon.
            # Si self.date_debut est 'fin' (end_date du script original), il faut ajuster.
            # Le plan indique que date_debut/date_fin sont passés au constructeur.
            # On va supposer que self.date_debut est le jour J-1 pour lequel on charge les fichiers.
            date_for_file = self.date_debut.replace('/', '-') # Tentative simple si le format est déjà inversé
            # Il faut clarifier comment les dates sont passées et utilisées pour les noms de fichiers.
            # Le script original utilise `str(start_date)` qui est `YYYY-MM-DD`.
            # Notre `self.date_debut` est `DD/MM/YYYY`.
            # Prenons `self.date_debut` (qui est le `debut` du script principal, donc `start_date` du script original)
            # et formattont-le en `YYYY-MM-DD`.
            parts = self.date_debut.split('/') # DD/MM/YYYY
            formatted_date_for_file = f"{parts[2]}-{parts[1]}-{parts[0]}"


        full_file_pattern = self.base_path + file_pattern.format(date_str=formatted_date_for_file)

        if self.logger:
            self.logger.info(f"Recherche du fichier avec le pattern: {full_file_pattern}")

        files = glob.glob(full_file_pattern, recursive=True)
        if not files:
            if self.logger:
                self.logger.warning(f"Aucun fichier trouvé pour le pattern {full_file_pattern} pour VirtuelEditec. Table temporaire {temp_table_truncate_key.split('_')[-1]} non alimentée.")
            return False # Indique qu'aucun fichier n'a été traité

        file_path = files[0]
        if self.logger:
            self.logger.info(f"Lecture du fichier {file_path} pour la table {temp_table_truncate_key.split('_')[-1]}")

        try:
            data_df = pd.read_csv(file_path, sep=sep, index_col=False, dtype=str, encoding='utf-8') # encoding peut varier
            data_df = data_df.reindex(columns=columns) # S'assure que les colonnes sont dans le bon ordre et nommées correctement
            data_df = data_df.replace(np.nan, '')

            # Truncate et Insert
            self._execute_query(temp_table_truncate_key)
            self.insert_dataframe_to_temp(data_df, query_key=temp_table_insert_key) # Doit passer la clé de la requête d'insertion
            if self.logger:
                self.logger.info(f"Données de {file_path} chargées dans la table temporaire via {temp_table_insert_key}.")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors du chargement du fichier {file_path} dans la table temporaire: {e}")
            # Ne pas lever d'exception ici pour permettre aux autres fichiers d'être traités si possible.
            return False

    def insert_dataframe_to_temp(self, df: pd.DataFrame, query_key: str = None):
        """
        Surcharge pour permettre de spécifier la clé de la requête d'insertion.
        Si query_key n'est pas fourni, utilise 'insert_temp' par défaut.
        """
        actual_query_key = query_key if query_key else 'insert_temp'

        queries = self.get_queries()
        if actual_query_key not in queries:
            if self.logger:
                self.logger.warning(f"Requête '{actual_query_key}' non définie pour {self.__class__.__name__}. Skipping DataFrame insertion.")
            return

        sql_insert_temp = queries[actual_query_key]

        if df is None or df.empty:
            if self.logger:
                self.logger.info(f"DataFrame vide pour {self.__class__.__name__} via {actual_query_key}, aucune insertion.")
            return

        if self.logger:
            self.logger.info(f"Insertion de {len(df)} lignes via {actual_query_key} pour {self.__class__.__name__}...")

        try:
            data_to_insert = [tuple(x) for x in df.to_numpy()]

            if not self.cursor:
                self._connect_db()
                if not self.cursor:
                    msg = f"Curseur non initialisé avant insert_dataframe_to_temp pour {self.__class__.__name__}"
                    if self.logger: self.logger.error(msg)
                    raise Exception(msg)

            self.cursor.executemany(sql_insert_temp, data_to_insert, batcherrors=True)
            self.conn.commit()
            if self.logger:
                self.logger.info(f"{self.cursor.rowcount} lignes insérées/affectées via {actual_query_key} pour {self.__class__.__name__}.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'insertion du DataFrame via {actual_query_key} pour {self.__class__.__name__}: {e}")
            if self.conn:
                self.conn.rollback()
            raise


    def load_data(self, data: pd.DataFrame = None): # data n'est pas utilisé ici car les données viennent de plusieurs fichiers
        """
        Charge les données pour VirtuelEditec.
        Surcharge pour gérer les trois sources de données et l'ordre spécifique des opérations.
        """
        self._connect_db()
        try:
            queries = self.get_queries()
            params_dates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}

            # Suppressions initiales des tables principales
            if 'delete_main_fait_vente' in queries:
                self._execute_query('delete_main_fait_vente', params=params_dates)
            if 'delete_main_fait_lots' in queries:
                self._execute_query('delete_main_fait_lots', params=params_dates)

            # Insertion dans dim_terminal (avant les faits car les faits en dépendent)
            # Cette requête se base sur le contenu des tables temporaires, donc elles doivent être remplies avant.
            # Exécutée après le chargement des tables temporaires.

            # Insertions principales (fait_vente, fait_lots)
            # Ces requêtes se basent sur le contenu des tables temporaires.
            if 'insert_main_fait_vente' in queries:
                self._execute_query('insert_main_fait_vente') # Pas de params de date ici, utilise les tables temp
            if 'insert_main_fait_lots' in queries:
                self._execute_query('insert_main_fait_lots') # Pas de params de date ici

            # Merge pour DTM_CA_DAILY
            if 'merge_dtm_ca_daily' in queries:
                 self._execute_query('merge_dtm_ca_daily', params=params_dates)

            # Truncate finales des tables temporaires
            if 'truncate_temp_zone_betting_final' in queries:
                self._execute_query('truncate_temp_zone_betting_final')
            if 'truncate_temp_financial_final' in queries:
                self._execute_query('truncate_temp_financial_final')
            if 'truncate_temp_sb_vdr_final' in queries:
                self._execute_query('truncate_temp_sb_vdr_final')

            if self.logger:
                self.logger.info(f"Processus load_data (partie base de données) complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def process(self, source_file_path: str = None): # source_file_path n'est pas utilisé directement
        """
        Orchestre la lecture des fichiers et le chargement des données pour VirtuelEditec.
        Le `source_file_path` fourni à `process_product` dans le script principal sera le `generalDirectory`.
        """
        if self.logger:
            self.logger.info(f"Début du traitement VirtuelEditec. Période: {self.date_debut} - {self.date_fin}")
            self.logger.info(f"Chemin de base pour les fichiers : {self.base_path}")

        # Indicateurs pour savoir si au moins une table temporaire a été chargée
        financial_loaded = False
        zone_betting_loaded = False
        sb_vdr_loaded = False

        # Connexion pour les opérations sur les tables temporaires
        self._connect_db()
        try:
            # 1. Charger Financial data
            financial_loaded = self._load_single_temp_table(
                file_pattern=r"VIRTUEL_EDITEC/FINANCIAL/**/Financial {date_str}.csv",
                columns=['Name', 'Total In', 'Total Out', 'date', 'Reversal', 'Currency'],
                temp_table_truncate_key='truncate_temp_financial',
                temp_table_insert_key='insert_temp_financial'
            )

            # 2. Charger Zone Betting data
            zone_betting_loaded = self._load_single_temp_table(
                file_pattern=r"VIRTUEL_EDITEC/ZONE BETTING/**/zone betting {date_str}.csv",
                columns=['Shop name', 'date', 'Cancelled', 'Stake', 'Won'],
                temp_table_truncate_key='truncate_temp_zone_betting',
                temp_table_insert_key='insert_temp_zone_betting'
            )

            # 3. Charger PremierSN (GLOB_SB_VDR) data
            sb_vdr_loaded = self._load_single_temp_table(
                file_pattern=r"VIRTUEL_EDITEC/PREMIERSN/**/{date_str}-Premier SN.csv",
                columns=['Outlet', 'Reported', 'Sales', 'Redeems', 'Voided'],
                temp_table_truncate_key='truncate_temp_sb_vdr',
                temp_table_insert_key='insert_temp_sb_vdr'
            )

            # Si aucune donnée n'a été chargée dans les tables temporaires, on peut choisir de ne pas continuer.
            if not (financial_loaded or zone_betting_loaded or sb_vdr_loaded):
                if self.logger:
                    self.logger.warning(f"Aucun fichier de données trouvé pour VirtuelEditec pour la date {self.date_debut}. "
                                     "Les opérations sur la base de données principale seront exécutées mais pourraient ne rien traiter.")
                # On continue quand même pour exécuter les delete et merge qui pourraient nettoyer ou mettre à jour des états.

            # Insertion dans dim_terminal (après le remplissage des tables temp)
            queries = self.get_queries()
            if 'insert_dim_terminal' in queries:
                self._execute_query('insert_dim_terminal')


        except Exception as e:
            # Si une erreur survient pendant le chargement des fichiers temporaires, logguer et potentiellement arrêter.
            if self.logger:
                self.logger.error(f"Erreur critique lors du chargement des données dans les tables temporaires pour VirtuelEditec: {e}")
            # Fermer la connexion si elle est ouverte avant de lever l'exception
            self._close_db()
            raise
        finally:
            # Fermer la connexion utilisée pour les tables temporaires si elle n'est pas déjà fermée par une erreur.
            # La méthode load_data() rouvrira/fermera sa propre connexion.
            # Pour éviter les conflits, fermons celle-ci.
            if self.conn: # Vérifier si la connexion est active
                 self._close_db()


        # Appeler la logique de base de données principale (delete, insert, merge)
        # load_data() gère sa propre connexion.
        self.load_data() # Pas besoin de passer data_df ici.

        if self.logger:
            self.logger.info(f"Fin du traitement VirtuelEditec.")
