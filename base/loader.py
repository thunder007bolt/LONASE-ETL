from pathlib import Path
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd # Importer pandas pour les type hints et opérations

from utils.config_utils import get_loading_configurations # Fonction utilitaire existante
from utils.db_utils import get_db_connection # Fonction utilitaire existante
from utils.file_manipulation import move_file # Fonction utilitaire existante
# Logger est fourni par get_loading_configurations

# Exceptions personnalisées
class LoaderConfigurationError(Exception):
    pass

class DataLoaderError(Exception):
    pass

class Loader(ABC):
    """
    Classe de base abstraite pour charger des données depuis des fichiers vers une base de données.
    Gère la configuration, la connexion à la BD, la lecture des fichiers,
    la transformation basique (DataFrame en tuples) et le chargement des données.
    """

    def __init__(self, job_name: str, log_file_path: str, db_env_vars_mapping: dict,
                 target_table_name: str, target_columns: list[str]):
        """
        Initialise le Loader.

        Args:
            job_name (str): Nom du job, utilisé pour la configuration.
            log_file_path (str): Chemin vers le fichier de log.
            db_env_vars_mapping (dict): Mapping des variables d'environnement pour la connexion BD.
                                       Ex: {'SQL_SERVER_HOST': 'DB_PROD_HOST', ...}
            target_table_name (str): Nom de la table de destination dans la base de données.
            target_columns (list[str]): Liste ordonnée des colonnes de la table de destination.
        """
        self.name = job_name
        self.log_file_path = log_file_path
        self.db_env_vars_mapping = db_env_vars_mapping # Utilisé par get_loading_configurations

        self.target_table_name = target_table_name
        self.target_columns = target_columns
        if not self.target_table_name or not self.target_columns:
            # Le logger n'est pas encore initialisé ici.
            raise LoaderConfigurationError("Le nom de la table cible et les colonnes cibles doivent être fournis.")

        self.logger = None # Sera initialisé par get_loading_configurations
        self.db_connection = None
        self.db_cursor = None

        # Attributs pour le suivi des erreurs de fichiers
        self.files_with_errors_count = 0
        self.files_with_errors_list: list[Path] = []

        try:
            (
                self.secret_config, # Contient les credentials BD mappés
                self.logger,        # Initialisé ici
                self.local_loaded_path, # Dossier pour les fichiers chargés avec succès
                self.local_source_path, # Dossier source des fichiers à charger
                self.local_error_path,  # Dossier pour les fichiers en erreur
                self.source_file_pattern # Motif des fichiers à chercher dans source_path
            ) = get_loading_configurations(
                name=self.name,
                log_file=self.log_file_path,
                env_variables_list=self.db_env_vars_mapping # La fonction attend 'env_variables_list'
            )
            # S'assurer que les chemins essentiels sont des Path et existent
            for path_attr in ['local_loaded_path', 'local_source_path', 'local_error_path']:
                path_val = getattr(self, path_attr)
                if not isinstance(path_val, Path):
                    # Le logger est disponible ici
                    self.logger.error(f"L'attribut de chemin '{path_attr}' n'est pas un objet Path ({type(path_val)}).")
                    raise LoaderConfigurationError(f"Chemin mal configuré: {path_attr}")
                path_val.mkdir(parents=True, exist_ok=True) # Crée le dossier s'il n'existe pas

        except KeyError as e:
            msg = f"Clé manquante lors de la configuration du Loader pour {self.name}: {e}."
            if self.logger: self.logger.critical(msg, exc_info=True)
            raise LoaderConfigurationError(msg) from e
        except Exception as e:
            msg = f"Erreur inattendue lors de la configuration du Loader pour {self.name}: {e}."
            if self.logger: self.logger.critical(msg, exc_info=True)
            raise LoaderConfigurationError(msg) from e


    def _connect_to_db(self):
        """Établit la connexion à la base de données."""
        self.logger.info(f"Connexion à la base de données pour le chargement (job: {self.name})...")
        try:
            # Les clés attendues par get_db_connection sont SERVER, DATABASE, USERNAME, PASSWORD
            # get_loading_configurations devrait déjà avoir mappé les variables d'env
            # aux clés attendues par secret_config (ex: SQL_SERVER_HOST -> SERVER si c'est ce que get_secret fait)
            # Si ce n'est pas le cas, il faut mapper ici ou dans get_loading_configurations.
            # Pour l'instant, on suppose que secret_config contient les clés directes ou celles attendues par get_db_connection.
            # On va utiliser les clés de l'ancienne version pour la compatibilité avec get_db_connection.
            server = self.secret_config['SQL_SERVER_HOST']
            database = self.secret_config['SQL_SERVER_TEMPDB_NAME'] # Ou une autre config pour la BD cible
            username = self.secret_config['SQL_SERVER_TEMPDB_USERNAME']
            password = self.secret_config['SQL_SERVER_TEMPDB_PASSWORD']
            db_type = self.job_config.get('db_type', 'sql_server') # Configurable, défaut sql_server

        except KeyError as e:
            self.logger.error(f"Paramètre de connexion BD manquant dans secret_config pour {self.name}: {e}. "
                              "Vérifiez db_env_vars_mapping et le fichier .env.")
            raise LoaderConfigurationError(f"Paramètre de connexion BD manquant: {e}") from e

        try:
            self.db_connection, self.db_cursor = get_db_connection(
                db_server=server, db_name=database, db_user=username,
                db_password=password, db_type=db_type, logger=self.logger
            )
            if not self.db_connection or not self.db_cursor:
                raise ConnectionError(f"Échec de l'établissement de la connexion BD pour {self.name}.")
            self.logger.info(f"Connexion à la BD '{database}' sur '{server}' pour chargement réussie.")
        except Exception as e:
            self.logger.error(f"Échec critique de la connexion BD pour chargement ({self.name}): {e}", exc_info=True)
            raise ConnectionError(f"Impossible de se connecter à la BD pour chargement ({self.name}).") from e


    def _truncate_target_table(self, table_name: str = None):
        """Supprime toutes les données de la table cible. À utiliser avec prudence."""
        target = table_name or self.target_table_name
        if not self.db_cursor:
            self.logger.error("Aucun curseur de base de données disponible pour TRUNCATE. Opération annulée.")
            raise ConnectionError("Curseur BD non disponible pour TRUNCATE.")

        self.logger.warning(f"Tentative de suppression de toutes les données de la table : {target}. Cette opération est irréversible.")
        # Optionnel: demander confirmation ou avoir un paramètre de config pour l'autoriser.
        # allow_truncate = self.job_config.get("allow_truncate_table", False)
        # if not allow_truncate:
        #     self.logger.error(f"TRUNCATE TABLE {target} n'est pas autorisé par la configuration. Opération annulée.")
        #     return

        try:
            # S'assurer que le nom de la table est sécurisé (éviter injection SQL si dynamique)
            # Ici, on suppose que target_table_name vient d'une config fiable.
            self.db_cursor.execute(f"TRUNCATE TABLE [{target}]") # Syntaxe SQL Server pour TRUNCATE
            self.db_connection.commit()
            self.logger.info(f"Toutes les données de la table [{target}] ont été supprimées avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression des données de la table [{target}]: {e}", exc_info=True)
            # Renvoyer l'erreur car c'est une opération critique qui a échoué.
            raise DataLoaderError(f"Échec de TRUNCATE TABLE [{target}].") from e


    def _insert_data_into_table(self, data_tuples: list[tuple]):
        """Insère les données (une liste de tuples) dans la table cible."""
        if not data_tuples:
            self.logger.info("Aucune donnée à insérer dans la table.")
            return
        if not self.db_cursor:
            self.logger.error("Aucun curseur de base de données disponible pour INSERT. Opération annulée.")
            raise ConnectionError("Curseur BD non disponible pour INSERT.")

        self.logger.info(f"Chargement de {len(data_tuples)} enregistrement(s) dans la table [{self.target_table_name}]...")

        # Préparer la requête d'insertion
        # Utiliser des placeholders pour les valeurs pour éviter les injections SQL.
        # S'assurer que les noms de colonnes sont correctement échappés si nécessaire (ex: avec des crochets pour SQL Server).
        column_names_str = ", ".join([f"[{col}]" for col in self.target_columns])
        placeholders_str = ", ".join(["?"] * len(self.target_columns))

        insert_query = f"INSERT INTO [{self.target_table_name}] ({column_names_str}) VALUES ({placeholders_str})"
        self.logger.debug(f"Requête d'insertion (tronquée si longue): {insert_query[:200]}")

        try:
            self.db_cursor.fast_executemany = True # Optimisation pour pyodbc si disponible et supporté
            self.db_cursor.executemany(insert_query, data_tuples)
            self.db_connection.commit()
            self.logger.info(f"{len(data_tuples)} enregistrement(s) chargé(s) avec succès dans [{self.target_table_name}].")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion des données dans [{self.target_table_name}]: {e}", exc_info=True)
            # Renvoyer l'erreur pour que le fichier puisse être déplacé vers le dossier d'erreur.
            raise DataLoaderError(f"Échec de l'insertion des données dans [{self.target_table_name}].") from e


    @abstractmethod
    def _read_and_convert_file_to_dataframe(self, file_path: Path) -> pd.DataFrame | None:
        """
        Méthode abstraite pour lire un fichier et le convertir en DataFrame pandas.
        Doit être implémentée par les classes filles pour gérer des formats de fichiers spécifiques (CSV, Excel, etc.).

        Args:
            file_path (Path): Chemin du fichier à lire.

        Returns:
            pd.DataFrame | None: DataFrame contenant les données du fichier, ou None en cas d'erreur de lecture/conversion.
                                 Si None est retourné, le fichier sera probablement déplacé vers le dossier d'erreur.
        """
        pass


    def _prepare_dataframe_for_loading(self, df: pd.DataFrame) -> list[tuple]:
        """
        Prépare le DataFrame pour le chargement :
        1. S'assure que les colonnes du DataFrame correspondent à self.target_columns (ordre et nom).
        2. Remplace les NaN par des valeurs appropriées (ex: None ou chaîne vide pour la BD).
        3. Convertit le DataFrame en une liste de tuples.
        """
        self.logger.info("Préparation du DataFrame pour le chargement en base de données...")

        # 1. Vérifier et réordonner les colonnes
        if not all(col in df.columns for col in self.target_columns):
            missing_cols = [col for col in self.target_columns if col not in df.columns]
            self.logger.error(f"Colonnes cibles manquantes dans le DataFrame: {missing_cols}. "
                              f"Colonnes DataFrame: {list(df.columns)}. Colonnes cibles attendues: {self.target_columns}")
            raise DataLoaderError(f"Colonnes DataFrame incompatibles avec les colonnes cibles. Manquantes: {missing_cols}")

        try:
            df_ordered = df[self.target_columns] # Sélectionne et réordonne les colonnes
        except KeyError as e: # Devrait être attrapé par la vérification précédente, mais par sécurité
            self.logger.error(f"Erreur de clé lors de la tentative de réorganisation des colonnes du DataFrame: {e}", exc_info=True)
            raise DataLoaderError("Échec de la réorganisation des colonnes du DataFrame.") from e

        # 2. Gérer les NaN. np.nan n'est pas toujours bien géré par les drivers DB.
        # Remplacer par None (qui devient NULL en SQL) ou par une chaîne vide si la colonne est de type texte.
        # Pour une approche générale, on remplace par None.
        # df_prepared = df_ordered.replace({np.nan: None})
        # df.fillna(value=np.nan, inplace=True) # Assure que tous les "absents" sont np.nan
        # df_prepared = df_ordered.where(pd.notnull(df_ordered), None) # Plus robuste pour tous types

        # Une approche plus simple et souvent efficace pour les tuples :
        # Convertir d'abord en liste de listes/tuples, puis remplacer les np.nan
        # Cependant, df.itertuples gère cela nativement si on ne fait rien.
        # Le remplacement par '' de l'ancienne version peut être problématique si la colonne attend un nombre ou une date.
        # On va utiliser une méthode plus sûre: remplacer np.nan par None, qui est le standard pour NULL en SQL.
        df_prepared = df_ordered.astype(object).where(pd.notnull(df_ordered), None)


        # 3. Convertir en liste de tuples
        try:
            list_of_tuples = list(df_prepared.itertuples(index=False, name=None))
            self.logger.info(f"DataFrame converti en {len(list_of_tuples)} tuples pour le chargement.")
            return list_of_tuples
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion du DataFrame en tuples: {e}", exc_info=True)
            raise DataLoaderError("Échec de la conversion DataFrame en tuples.") from e


    def process_loading_from_files(self):
        """
        Orchestre le processus complet de chargement des données depuis les fichiers sources.
        """
        self.logger.info(f"Démarrage du processus de chargement pour le job: {self.name}")
        self.files_with_errors_count = 0
        self.files_with_errors_list = []

        try:
            self._connect_to_db()

            # Option de tronquer la table avant le chargement (configurable)
            if self.job_config.get("truncate_table_before_load", False):
                self._truncate_target_table()

            files_to_process = list(self.local_source_path.glob(self.source_file_pattern))
            if not files_to_process:
                self.logger.info(f"Aucun fichier trouvé dans {self.local_source_path} correspondant au motif '{self.source_file_pattern}'.")
            else:
                self.logger.info(f"{len(files_to_process)} fichier(s) trouvé(s) à traiter dans {self.local_source_path}.")

            for file_path in files_to_process:
                self.logger.info(f"Traitement du fichier : {file_path.name}")
                try:
                    dataframe = self._read_and_convert_file_to_dataframe(file_path)
                    if dataframe is None: # Erreur de lecture/conversion déjà loggée
                        self.logger.error(f"Échec de la lecture ou conversion du fichier {file_path.name}. Il sera déplacé vers le dossier d'erreurs.")
                        raise DataLoaderError(f"DataFrame nul retourné pour {file_path.name}") # Force le catch

                    if dataframe.empty:
                        self.logger.info(f"Le fichier {file_path.name} est vide ou n'a produit aucune donnée. Déplacement vers 'loaded'.")
                        move_file(file_path, self.local_loaded_path) # Utilise la fonction importée
                        self.logger.info(f"Fichier {file_path.name} déplacé vers {self.local_loaded_path} (vide).")
                        continue

                    data_tuples = self._prepare_dataframe_for_loading(dataframe)
                    if not data_tuples: # Si le dataframe était vide après préparation
                        self.logger.info(f"Aucune donnée à charger depuis {file_path.name} après préparation. Déplacement vers 'loaded'.")
                        move_file(file_path, self.local_loaded_path)
                        self.logger.info(f"Fichier {file_path.name} déplacé vers {self.local_loaded_path} (données vides).")
                        continue

                    self._insert_data_into_table(data_tuples)

                    # Déplacer le fichier traité avec succès vers le dossier 'loaded'
                    move_file(file_path, self.local_loaded_path)
                    self.logger.info(f"Fichier {file_path.name} traité avec succès et déplacé vers {self.local_loaded_path}.")

                except (DataLoaderError, Exception) as e: # Attrape les erreurs spécifiques au chargement ou autres
                    self.logger.error(f"Erreur lors du traitement du fichier {file_path.name}: {e}", exc_info=True)
                    self.files_with_errors_count += 1
                    self.files_with_errors_list.append(file_path.name)
                    try:
                        move_file(file_path, self.local_error_path)
                        self.logger.info(f"Fichier {file_path.name} déplacé vers le dossier d'erreurs: {self.local_error_path}.")
                    except Exception as move_e:
                        self.logger.error(f"Impossible de déplacer le fichier {file_path.name} vers {self.local_error_path}: {move_e}", exc_info=True)

            self._report_loading_summary()

        except (LoaderConfigurationError, ConnectionError) as e:
            self.logger.critical(f"Arrêt du processus de chargement ({self.name}) en raison d'une erreur critique: {e}", exc_info=True)
        except Exception as e:
            self.logger.critical(f"Erreur inattendue majeure durant process_loading_from_files ({self.name}): {e}", exc_info=True)
        finally:
            self._close_db_connection()
            self.logger.info(f"Processus de chargement pour {self.name} terminé.")

    def _report_loading_summary(self):
        """Affiche un résumé des erreurs de chargement des fichiers."""
        # Anciennement check_error et set_error
        if self.files_with_errors_count > 0:
            self.logger.warning(f"Résumé du chargement: {self.files_with_errors_count} fichier(s) n'ont pas pu être chargé(s) complètement.")
            self.logger.warning("Liste des fichiers avec erreurs (noms uniquement):")
            for filename in self.files_with_errors_list:
                self.logger.warning(f"  - {filename}")
        else:
            self.logger.info("Résumé du chargement: Tous les fichiers (le cas échéant) ont été traités sans erreur critique de chargement.")


    def _close_db_connection(self):
        """Ferme la connexion à la base de données si elle est ouverte."""
        if self.db_cursor:
            try:
                self.db_cursor.close()
                self.logger.debug("Curseur de base de données fermé.")
            except Exception as e:
                self.logger.warning(f"Erreur lors de la fermeture du curseur BD ({self.name}): {e}", exc_info=True)
            finally:
                self.db_cursor = None
        if self.db_connection:
            try:
                self.db_connection.close()
                self.logger.info("Connexion à la base de données fermée avec succès.")
            except Exception as e:
                self.logger.warning(f"Erreur lors de la fermeture de la connexion BD ({self.name}): {e}", exc_info=True)
            finally:
                self.db_connection = None

    def __del__(self):
        """Destructeur pour s'assurer que la connexion à la base de données est fermée."""
        # Éviter de logger dans __del__ car le logger peut être déjà nettoyé.
        self._close_db_connection()
        # print(f"Destructeur de Loader pour '{self.name}' appelé, connexion BD fermée.")
