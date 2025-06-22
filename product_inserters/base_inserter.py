from abc import ABC, abstractmethod
import pandas as pd
from utils.db_utils import get_oracle_connection # Assurez-vous que le chemin d'importation est correct

class ProductInserter(ABC):
    def __init__(self, db_config: dict, date_debut: str, date_fin: str, logger=None):
        """
        Initialise le ProductInserter avec la configuration de la base de données et les dates.

        :param db_config: Dictionnaire contenant les informations de connexion
                          (username, password, host, port, service_name, lib_dir).
        :param date_debut: Date de début pour le traitement des données.
        :param date_fin: Date de fin pour le traitement des données.
        :param logger: Logger pour enregistrer les messages.
        """
        self.db_config = db_config
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.logger = logger
        self.conn = None
        self.cursor = None

    def _connect_db(self):
        """Établit la connexion à la base de données Oracle."""
        if self.logger:
            self.logger.info(f"Tentative de connexion à la base de données Oracle pour {self.__class__.__name__}")

        try:
            self.conn, self.cursor = get_oracle_connection(
                username=self.db_config['username'],
                password=self.db_config['password'],
                host=self.db_config['host'],
                port=self.db_config['port'],
                service_name=self.db_config['service_name'],
                lib_dir=self.db_config.get('lib_dir'), # lib_dir est optionnel
                logger=self.logger
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur de connexion à la base de données pour {self.__class__.__name__}: {e}")
            raise

    def _close_db(self):
        """Ferme la connexion à la base de données."""
        if self.cursor:
            self.cursor.close()
            if self.logger:
                self.logger.info(f"Curseur fermé pour {self.__class__.__name__}")
        if self.conn:
            self.conn.close()
            if self.logger:
                self.logger.info(f"Connexion à la base de données fermée pour {self.__class__.__name__}")

    @abstractmethod
    def get_queries(self) -> dict[str, str]:
        """
        Méthode abstraite pour obtenir les requêtes SQL spécifiques au produit.
        Doit être implémentée par les sous-classes.

        :return: Un dictionnaire où les clés sont des identifiants de requête
                 (ex: 'truncate_temp', 'insert_temp') et les valeurs sont les requêtes SQL.
        """
        pass

    def _execute_query(self, query_key: str, params: dict = None):
        """
        Exécute une requête SQL obtenue à partir de get_queries.

        :param query_key: La clé de la requête dans le dictionnaire retourné par get_queries.
        :param params: Un dictionnaire de paramètres pour la requête SQL (optionnel).
        """
        queries = self.get_queries()
        if query_key not in queries:
            msg = f"La clé de requête '{query_key}' n'a pas été trouvée pour {self.__class__.__name__}."
            if self.logger:
                self.logger.error(msg)
            raise ValueError(msg)

        sql = queries[query_key]
        if self.logger:
            self.logger.info(f"Exécution de la requête '{query_key}' pour {self.__class__.__name__}: {sql[:100]}...") # Log tronqué

        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            if not query_key.lower().startswith("select"): # Ne pas commiter pour les SELECTs
                 self.conn.commit()

            if self.logger:
                self.logger.info(f"Requête '{query_key}' exécutée avec succès pour {self.__class__.__name__}.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'exécution de la requête '{query_key}' pour {self.__class__.__name__}: {e}")
            if self.conn: # Rollback en cas d'erreur si une transaction est active
                try:
                    self.conn.rollback()
                    if self.logger: self.logger.info(f"Rollback effectué suite à l'erreur sur '{query_key}'.")
                except Exception as rb_e:
                    if self.logger: self.logger.error(f"Erreur lors du rollback: {rb_e}")
            raise

    def load_data(self, data: pd.DataFrame = None):
        """
        Méthode principale pour charger les données.
        Cette implémentation de base suppose une séquence typique d'opérations:
        1. Truncate table temporaire
        2. Insert into table temporaire (si des données sont fournies)
        3. Delete from table principale (basé sur les dates)
        4. Insert into table principale from table temporaire
        5. Potentiellement une mise à jour d'agrégats ou d'autres opérations post-insertion.

        Les sous-classes peuvent surcharger cette méthode si un flux différent est nécessaire.

        :param data: DataFrame pandas contenant les données à insérer dans la table temporaire.
                     Si None, l'étape d'insertion dans la table temporaire peut être sautée
                     ou gérée différemment par la sous-classe.
        """
        self._connect_db()
        try:
            queries = self.get_queries()

            # 1. Truncate table temporaire (si la requête existe)
            if 'truncate_temp' in queries:
                self._execute_query('truncate_temp')

            # 2. Insert into table temporaire (si des données et la requête existent)
            # Cette partie nécessitera une gestion plus spécifique dans les sous-classes
            # pour l'insertion de DataFrames, car _execute_query est générique.
            # Pour l'instant, on suppose que si 'insert_temp' existe, elle est appelée.
            # La transformation de DataFrame en DML sera gérée par les sous-classes
            # ou par une méthode helper si un pattern commun émerge.
            if data is not None and not data.empty and 'insert_temp' in queries:
                # Exemple de gestion (à adapter/améliorer)
                # Ceci est une simplification. L'insertion de DataFrames peut être complexe.
                if self.logger:
                    self.logger.info(f"Préparation de l'insertion des données du DataFrame dans la table temporaire pour {self.__class__.__name__}.")
                # La logique spécifique d'itération sur le DataFrame et d'exécution
                # de la requête 'insert_temp' avec les données de chaque ligne
                # sera généralement dans la sous-classe ou une méthode dédiée.
                # self._execute_query('insert_temp', params=data.to_dict(orient='records')) # Ceci ne fonctionnera pas directement pour tous les SGBD/drivers
                self.insert_dataframe_to_temp(data)


            # 3. Delete from table principale (basé sur les dates)
            if 'delete_main' in queries:
                params_delete = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
                self._execute_query('delete_main', params=params_delete)

            # 4. Insert into table principale from table temporaire
            if 'insert_main_from_temp' in queries:
                params_insert_main = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
                self._execute_query('insert_main_from_temp', params=params_insert_main)

            # 5. Autres opérations (ex: mise à jour d'agrégats)
            if 'update_aggregates' in queries: # Exemple
                 params_aggregates = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
                 self._execute_query('update_aggregates', params=params_aggregates)

            if self.logger:
                self.logger.info(f"Processus load_data complété pour {self.__class__.__name__}.")

        finally:
            self._close_db()

    def insert_dataframe_to_temp(self, df: pd.DataFrame):
        """
        Méthode à implémenter ou surcharger par les sous-classes pour gérer
        l'insertion d'un DataFrame dans la table temporaire.
        La requête 'insert_temp' doit être définie dans get_queries().
        """
        queries = self.get_queries()
        if 'insert_temp' not in queries:
            if self.logger:
                self.logger.warning(f"Requête 'insert_temp' non définie pour {self.__class__.__name__}. Skipping DataFrame insertion.")
            return

        sql_insert_temp = queries['insert_temp']

        if df is None or df.empty:
            if self.logger:
                self.logger.info(f"DataFrame vide pour {self.__class__.__name__}, aucune insertion dans la table temporaire.")
            return

        if self.logger:
            self.logger.info(f"Insertion de {len(df)} lignes dans la table temporaire pour {self.__class__.__name__}...")

        try:
            # La méthode d'insertion peut varier (executemany, itération, etc.)
            # Utilisation de executemany pour la performance si le driver le supporte bien.
            # Les colonnes du DataFrame doivent correspondre aux placeholders dans la requête.
            # Exemple: INSERT INTO temp_table (col1, col2) VALUES (:1, :2)
            # Les données doivent être une liste de tuples/listes
            data_to_insert = [tuple(x) for x in df.to_numpy()]

            # S'assurer que le curseur est bien initialisé
            if not self.cursor:
                self._connect_db() # Tentative de reconnexion si curseur non existant (ne devrait pas arriver dans le flux normal)
                if not self.cursor: # Si toujours pas de curseur, c'est une erreur
                    msg = f"Curseur non initialisé avant insert_dataframe_to_temp pour {self.__class__.__name__}"
                    if self.logger: self.logger.error(msg)
                    raise Exception(msg)

            self.cursor.executemany(sql_insert_temp, data_to_insert, batcherrors=True)

            # Gestion des erreurs de lot si nécessaire
            # for error in self.cursor.getbatcherrors():
            #     if self.logger: self.logger.error(f"Error in batch insert: {error.message} at row offset {error.offset}")

            self.conn.commit()
            if self.logger:
                self.logger.info(f"{self.cursor.rowcount} lignes insérées/affectées dans la table temporaire pour {self.__class__.__name__}.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erreur lors de l'insertion du DataFrame dans la table temporaire pour {self.__class__.__name__}: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def process(self, source_file_path: str = None, specific_data: pd.DataFrame = None):
        """
        Méthode d'orchestration principale pour un produit.
        Les sous-classes peuvent la surcharger pour des logiques de lecture de fichier spécifiques
        ou si les données ne proviennent pas d'un fichier CSV/Excel standard.

        :param source_file_path: Chemin vers le fichier de données source (si applicable).
        :param specific_data: DataFrame déjà chargé (si applicable).
        """
        if self.logger:
            self.logger.info(f"Début du traitement pour {self.__class__.__name__} avec dates: {self.date_debut} - {self.date_fin}.")

        data_df = None
        if specific_data is not None:
            data_df = specific_data
            if self.logger: self.logger.info("Utilisation d'un DataFrame fourni directement.")
        elif source_file_path:
            if self.logger: self.logger.info(f"Lecture des données depuis {source_file_path}")
            try:
                # Hypothèse: les fichiers sont CSV. Adapter si Excel ou autre.
                # La gestion des types de fichiers pourrait être plus sophistiquée.
                if source_file_path.endswith('.csv'):
                    data_df = pd.read_csv(source_file_path)
                elif source_file_path.endswith(('.xls', '.xlsx')):
                    data_df = pd.read_excel(source_file_path)
                else:
                    msg = f"Type de fichier non supporté pour la lecture automatique: {source_file_path}"
                    if self.logger: self.logger.error(msg)
                    raise ValueError(msg)
                if self.logger: self.logger.info(f"{len(data_df)} lignes lues depuis {source_file_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erreur lors de la lecture du fichier {source_file_path} pour {self.__class__.__name__}: {e}")
                # Décider si l'erreur de lecture est fatale ou si on continue sans données pour cette source
                # Pour l'instant, on propage l'erreur.
                raise
        else:
            if self.logger:
                self.logger.info(f"Aucun fichier source ni DataFrame fourni pour {self.__class__.__name__}. "
                                 "Certaines opérations de load_data pourraient ne pas s'exécuter.")

        # Appeler load_data avec le DataFrame potentiellement chargé
        self.load_data(data=data_df)

        if self.logger:
            self.logger.info(f"Fin du traitement pour {self.__class__.__name__}.")

# Exemple de configuration de base de données (à remplir avec les vraies valeurs)
# DB_CONFIG_EXAMPLE = {
#     'username': 'your_username',
#     'password': 'your_password',
#     'host': 'your_host',
#     'port': 'your_port', # ex: 1521
#     'service_name': 'your_service_name',
#     'lib_dir': r'C:\path\to\your\oracle\instantclient' # Optionnel, seulement si nécessaire
# }
# Assurez-vous que pandas est installé: pip install pandas oracledb
# Et que le client Oracle est correctement configuré si vous utilisez le mode Thick.
