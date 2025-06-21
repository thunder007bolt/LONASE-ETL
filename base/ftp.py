from abc import ABC, abstractmethod
from ftplib import FTP, error_perm, error_temp
import time
import os
import glob
from pathlib import Path
from datetime import datetime, date # Assurez-vous que date est importé si utilisé pour self.date_to_process

from base.logger import Logger # Gardé pour l'instant
from utils.config_utils import get_config, get_secret # Fonctions de configuration existantes
# S'assurer que file_manipulation.rename_file et delete_file sont corrects ou les adapter
from utils.file_manipulation import rename_file as fm_rename_file, delete_file as fm_delete_file
from utils.date_utils import get_yesterday_date


# Exceptions personnalisées
class FTPConnectionError(Exception):
    pass

class FTPOperationError(Exception):
    pass

class FTPConfigurationError(Exception):
    pass


class BaseFTP(ABC):
    """
    Classe de base abstraite pour les opérations FTP.
    Gère la configuration, la connexion, le téléchargement, la vérification et le renommage des fichiers.
    """
    DEFAULT_FTP_PORT = 21 # Port FTP standard non sécurisé
    DEFAULT_FTP_TIMEOUT = 30 # Secondes
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_RETRY_DELAY = 5 # Secondes

    def __init__(self, job_name: str, log_file_path: str, ftp_env_vars_mapping: dict):
        self.name = job_name # Nom du job/scraper
        self.logger = Logger(log_file=log_file_path).get_logger()
        self.logger.info(f"Initialisation du client FTP pour: {self.name}")

        try:
            # Configuration générale du projet et spécifique au job
            all_configs = get_config(job_name)
            if job_name not in all_configs:
                raise FTPConfigurationError(f"Configuration pour le job '{job_name}' non trouvée.")
            self.job_config = all_configs[job_name]
            self.base_config = all_configs.get('base', {})
            if not self.base_config:
                self.logger.warning("Configuration de base ('base') non trouvée. Certaines fonctionnalités pourraient ne pas être disponibles.")

            # Configuration des secrets FTP (host, user, pass)
            # ftp_env_vars_mapping = {'FTP_HOST': 'SPECIFIC_FTP_HOST_ENV', ...}
            self.secret_config = get_secret(list(ftp_env_vars_mapping.values()))
            # Remapper les secrets aux clés attendues (FTP_HOST, FTP_USERNAME, FTP_PASSWORD)
            self.ftp_credentials = {
                k_standard: self.secret_config.get(v_specific)
                for k_standard, v_specific in ftp_env_vars_mapping.items()
            }
            if not all(self.ftp_credentials.values()): # Vérifie si une valeur est None après le mapping
                missing_creds = [k for k,v in self.ftp_credentials.items() if not v]
                raise FTPConfigurationError(f"Identifiants FTP manquants après mapping: {missing_creds}. Vérifiez ftp_env_vars_mapping et les variables d'environnement.")

        except Exception as e:
            self.logger.error(f"Erreur d'initialisation de BaseFTP pour {self.name}: {e}", exc_info=True)
            raise FTPConfigurationError(f"Échec de l'initialisation de BaseFTP: {e}") from e

        self.ftp_connection: FTP | None = None # Instance de la connexion FTP

        # Chemins (dérivés de la configuration)
        self._configure_paths()

        # Date pour le traitement (si applicable, sinon peut être None ou gérée par les classes filles)
        self._set_date_to_process()

        # Paramètres pour le fichier à télécharger
        self.file_pattern_to_download = self.job_config.get("file_pattern", "*.csv") # Ex: data_*.zip
        self.file_prefix_for_pattern = self.job_config.get("file_prefix", self.name) # Ex: specific_job_

        # Nom de fichier attendu basé sur la date (si applicable)
        self.expected_filename_on_server = self._build_expected_filename_on_server()

        # Temps d'attente pour la vérification du téléchargement
        self.download_wait_timeout = self.job_config.get("wait_time", 120) # Secondes


    def _configure_paths(self):
        """Configure les chemins locaux basés sur la configuration."""
        try:
            data_path_str = self.base_config.get("paths", {}).get("data_path")
            if not data_path_str:
                raise FTPConfigurationError("Le chemin 'data_path' de base n'est pas configuré.")

            base_data_path = Path(data_path_str)

            # Chemin distant sur le serveur FTP
            self.ftp_remote_source_path = self.job_config["ftp_remote_path"] # Doit être dans la config du job

            # Chemin local de destination pour les fichiers extraits/téléchargés
            dest_rel_path = self.job_config.get("extraction_dest_relative_path")
            if not dest_rel_path:
                raise FTPConfigurationError("Chemin 'extraction_dest_relative_path' non configuré pour le job.")
            self.local_extraction_dest_path = (base_data_path / dest_rel_path).resolve()

            # Chemins optionnels pour les fichiers après traitement (loaded, error)
            loaded_rel_path = self.job_config.get('loaded_dest_relative_path')
            self.local_loaded_path = (base_data_path / loaded_rel_path).resolve() if loaded_rel_path else None

            error_rel_path = self.job_config.get('error_dest_relative_path')
            self.local_error_path = (base_data_path / error_rel_path).resolve() if error_rel_path else None

            # S'assurer que les dossiers de destination existent
            self.local_extraction_dest_path.mkdir(parents=True, exist_ok=True)
            if self.local_loaded_path: self.local_loaded_path.mkdir(parents=True, exist_ok=True)
            if self.local_error_path: self.local_error_path.mkdir(parents=True, exist_ok=True)

        except KeyError as e:
            self.logger.error(f"Clé de configuration de chemin manquante pour {self.name}: {e}", exc_info=True)
            raise FTPConfigurationError(f"Configuration de chemin manquante: {e}") from e


    def _set_date_to_process(self):
        """Définit la date pour laquelle les fichiers doivent être traités."""
        # Logique similaire à _set_dates dans BaseScrapper/DatabaseExtractor
        _, _, _, yesterday = get_yesterday_date()
        date_config = self.job_config.get("date") # Peut être une chaîne "YYYY-MM-DD" ou None

        if date_config is None:
            self.date_to_process = datetime.now().date() # Ou yesterday, selon la logique métier
            self.logger.info(f"Aucune date spécifiée dans la config, utilisation de la date actuelle: {self.date_to_process.strftime('%Y-%m-%d')}")
        elif isinstance(date_config, str):
            try:
                self.date_to_process = datetime.strptime(date_config, "%Y-%m-%d").date()
            except ValueError:
                self.logger.error(f"Format de date invalide ('{date_config}') dans la config. Utilisation de la date d'hier.")
                self.date_to_process = yesterday
        elif isinstance(date_config, date): # Si c'est déjà un objet date
             self.date_to_process = date_config
        else: # Fallback
            self.logger.warning(f"Type de date non géré ('{type(date_config)}'). Utilisation de la date d'hier.")
            self.date_to_process = yesterday
        self.logger.info(f"Date de traitement configurée : {self.date_to_process.strftime('%Y-%m-%d')}")


    def _build_expected_filename_on_server(self) -> str:
        """Construit le nom de fichier attendu sur le serveur FTP basé sur la date et le préfixe."""
        # Exemple: "prefix_YYYYMMDD.ext" ou un motif plus complexe.
        # Cette méthode peut être surchargée par les classes filles si la logique est plus complexe.
        date_str_format = self.job_config.get("filename_date_format", "%Y%m%d") # Ex: YYYYMMDD
        filename = f"{self.file_prefix_for_pattern}{self.date_to_process.strftime(date_str_format)}"
        # L'extension fait partie de file_pattern_to_download, donc on ne l'ajoute pas forcément ici.
        # Ou si file_pattern_to_download est juste une extension comme "*.zip", alors on a besoin de l'extension.
        # Pour l'instant, on retourne le nom sans extension, le pattern s'en chargera.
        # Si le pattern est par exemple "prefix_YYYYMMDD_*.csv", alors ce nom est le début du pattern.
        self.logger.debug(f"Nom de fichier attendu (base) sur le serveur: {filename}")
        return filename


    def _ftp_connect_and_login(self):
        """Établit la connexion FTP et se logue."""
        host = self.ftp_credentials.get("FTP_HOST")
        user = self.ftp_credentials.get("FTP_USERNAME")
        passwd = self.ftp_credentials.get("FTP_PASSWORD")
        port = self.job_config.get("ftp_port", self.DEFAULT_FTP_PORT)
        timeout = self.job_config.get("ftp_timeout", self.DEFAULT_FTP_TIMEOUT)

        if not host:
            raise FTPConfigurationError("Hôte FTP (FTP_HOST) non configuré.")

        self.logger.info(f"Connexion à FTP: {host}:{port} pour l'utilisateur {user or 'anonyme'}")
        try:
            self.ftp_connection = FTP()
            self.ftp_connection.connect(host, port, timeout)
            self.ftp_connection.login(user, passwd) # login gère user='' pour anonyme
            self.logger.info("Connexion et login FTP réussis.")
            # Optionnel: Configurer le mode passif, encodage, etc.
            # self.ftp_connection.set_pasv(True)
            # self.ftp_connection.encoding = "utf-8" # Si nécessaire
        except (error_perm, error_temp, ConnectionRefusedError, OSError) as e: # OSError pour les erreurs de socket
            self.logger.error(f"Échec de la connexion ou du login FTP à {host}: {e}", exc_info=True)
            self.ftp_connection = None # S'assurer qu'il est None en cas d'échec
            raise FTPConnectionError(f"Impossible de se connecter/logger au serveur FTP {host}: {e}") from e


    def _download_matching_files(self):
        """Télécharge les fichiers du serveur FTP qui correspondent au motif attendu."""
        if not self.ftp_connection:
            self.logger.error("Aucune connexion FTP active pour télécharger les fichiers.")
            raise FTPConnectionError("Tentative de téléchargement sans connexion FTP.")

        try:
            self.ftp_connection.cwd(self.ftp_remote_source_path)
            self.logger.info(f"Changé de répertoire distant vers: {self.ftp_remote_source_path}")

            server_file_list = self.ftp_connection.nlst()
            self.logger.debug(f"Fichiers trouvés sur le serveur dans {self.ftp_remote_source_path}: {server_file_list}")

            downloaded_count = 0
            # Le expected_filename_on_server est une base, le file_pattern_to_download est un glob/regex
            # On cherche les fichiers sur le serveur qui contiennent expected_filename_on_server
            # ET qui correspondent à file_pattern_to_download (si ce dernier est plus qu'une simple extension)
            # Exemple: expected = "data_20230101", pattern = "*.csv" -> cherche "data_20230101.csv" ou "data_20230101_details.csv"
            # Si pattern = "data_YYYYMMDD_report_*.zip", et expected = "data_20230101"
            # il faut une logique de matching plus avancée.
            # Pour l'instant, on se base sur une correspondance simple : le nom de fichier sur le serveur
            # doit contenir self.expected_filename_on_server et correspondre à self.file_pattern_to_download (si c'est un glob)

            # Simplification: on cherche un fichier qui contient expected_filename_on_server
            # et qui a une extension qui fait partie de file_pattern_to_download (ex: si pattern est "*.csv")

            # Si file_pattern_to_download est un pattern glob (ex: data_*.zip)
            # on peut utiliser fnmatch pour filtrer server_file_list.
            # import fnmatch
            # matching_server_files = [f for f in server_file_list if fnmatch.fnmatch(f, self.file_pattern_to_download)]

            # Pour cet exemple, on va supposer que self.expected_filename_on_server EST le nom de fichier complet
            # ou que self.file_pattern_to_download est le nom exact à chercher.
            # Si on doit télécharger plusieurs fichiers correspondant à un pattern, cette logique doit être adaptée.

            # Logique actuelle: on cherche UN fichier qui contient `self.expected_filename_on_server`
            # La variable `self.filename` de l'ancienne version était `f"{config["file_prefix"]}{self.date.strftime("%Y%m%d")}"`
            # ce qui correspond à `self.expected_filename_on_server`

            files_to_try = [f for f in server_file_list if self.expected_filename_on_server in f]
            if not files_to_try:
                 self.logger.warning(f"Aucun fichier sur le serveur contenant '{self.expected_filename_on_server}' dans {self.ftp_remote_source_path}.")
                 # On pourrait vouloir lever une erreur ici si un fichier est absolument attendu.
                 # raise FTPFileNotFoundError(f"Fichier attendu contenant '{self.expected_filename_on_server}' non trouvé.")

            for server_filename in files_to_try: # On pourrait s'arrêter au premier trouvé si un seul est attendu.
                local_file_path = self.local_extraction_dest_path / server_filename
                self.logger.info(f"Tentative de téléchargement du fichier '{server_filename}' vers '{local_file_path}'...")
                try:
                    with open(local_file_path, 'wb') as local_file:
                        self.ftp_connection.retrbinary(f"RETR {server_filename}", local_file.write)
                    self.logger.info(f"Fichier '{server_filename}' téléchargé avec succès.")
                    downloaded_count += 1
                    # Si on ne s'attend qu'à un seul fichier, on peut `break` ici.
                except (error_perm, error_temp) as e:
                    self.logger.error(f"Erreur FTP lors du téléchargement de '{server_filename}': {e}", exc_info=True)
                    # Supprimer le fichier local potentiellement incomplet
                    if local_file_path.exists(): local_file_path.unlink()
                    # Continuer avec le fichier suivant si plusieurs sont attendus, ou lever une erreur.
                    raise FTPOperationError(f"Échec du téléchargement de {server_filename}: {e}") from e

            if downloaded_count == 0 and files_to_try: # On a essayé de télécharger mais rien n'a abouti
                self.logger.warning(f"Aucun fichier n'a pu être téléchargé parmi ceux correspondant à '{self.expected_filename_on_server}'.")
            elif downloaded_count > 0:
                self.logger.info(f"{downloaded_count} fichier(s) téléchargé(s) avec succès.")

        except (error_perm, error_temp) as e: # Erreurs FTP pour cwd ou nlst
            self.logger.error(f"Erreur FTP lors de l'accès au répertoire ou du listage des fichiers: {e}", exc_info=True)
            raise FTPOperationError(f"Opération FTP échouée (cwd/nlst): {e}") from e
        except Exception as e: # Autres erreurs
            self.logger.error(f"Erreur inattendue lors du téléchargement des fichiers: {e}", exc_info=True)
            raise


    def _delete_local_files_before_download(self):
        """Supprime les fichiers locaux existants dans le dossier de destination avant le téléchargement."""
        # L'ancienne version utilisait self.config["download_path"] et self.config["file_pattern"]
        # Ici, on utilise self.local_extraction_dest_path et un pattern générique ou celui du job.
        pattern_to_delete = self.job_config.get("delete_before_download_pattern", self.file_pattern_to_download)
        # Attention: si pattern_to_delete est trop large (ex: "*"), cela peut être dangereux.
        # Il est préférable d'être spécifique, par exemple, le nom de fichier attendu.
        # Pour l'instant, on utilise le pattern de téléchargement.

        self.logger.info(f"Suppression des fichiers existants dans {self.local_extraction_dest_path} "
                         f"correspondant au motif '{pattern_to_delete}'...")
        try:
            # fm_delete_file prend (Path, pattern_str)
            fm_delete_file(self.local_extraction_dest_path, pattern_to_delete)
            self.logger.info("Anciens fichiers locaux (si existants) supprimés.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression des anciens fichiers locaux: {e}", exc_info=True)
            # Non bloquant, on continue le téléchargement.


    def _verify_download_locally(self, expected_local_filename_part: str) -> Path | None:
        """
        Vérifie si un fichier contenant expected_local_filename_part existe localement après le téléchargement.
        Attend un certain temps.
        """
        # L'ancienne méthode _verify_download utilisait un wait_for_download interne.
        # On reproduit une logique similaire ici.
        self.logger.info(f"Vérification du téléchargement local pour un fichier contenant '{expected_local_filename_part}' "
                         f"dans {self.local_extraction_dest_path} (timeout: {self.download_wait_timeout}s).")

        start_time = time.time()
        verified_file_path = None
        while time.time() - start_time < self.download_wait_timeout:
            # Chercher tous les fichiers dans le dossier, puis filtrer par la partie attendue du nom.
            # Le file_pattern_to_download peut être utilisé ici si c'est un glob.
            candidate_files = list(self.local_extraction_dest_path.glob(self.file_pattern_to_download))

            for f_path in candidate_files:
                if expected_local_filename_part in f_path.name:
                    # Vérification de base: le fichier existe et n'est pas vide.
                    # Une vérification de stabilité (taille ne change plus) serait mieux.
                    if f_path.exists() and f_path.stat().st_size > 0:
                        self.logger.info(f"Fichier local '{f_path.name}' trouvé et vérifié (non vide).")
                        verified_file_path = f_path
                        break # Sortir de la boucle for

            if verified_file_path:
                break # Sortir de la boucle while

            time.sleep(2) # Intervalle de polling

        if not verified_file_path:
            self.logger.error(f"Timeout: Aucun fichier local contenant '{expected_local_filename_part}' "
                              f"n'a été trouvé ou vérifié dans {self.local_extraction_dest_path} "
                              f"après {self.download_wait_timeout} secondes.")
            # L'ancienne version appelait _download_files() à nouveau. Ici, on pourrait lever une exception.
            # raise FTPDownloadVerificationError(f"Vérification du téléchargement local échouée pour '{expected_local_filename_part}'.")
            return None

        return verified_file_path


    def _rename_downloaded_file(self, current_file_path: Path) -> Path | None:
        """Renomme le fichier téléchargé selon le format standard du job."""
        # L'ancienne `rename_file` utilisait self.name, self.date, self.file_pattern, etc.
        # Ici, on a le chemin du fichier actuel et on utilise self.name et self.date_to_process.
        try:
            new_stem = f"{self.name}_{self.date_to_process.strftime('%Y-%m-%d')}"
            # fm_rename_file(pattern, source_folder, rename_name, logger)
            # On a un fichier exact, pas un pattern. Il faut adapter l'appel ou la fonction.
            # Pour l'instant, on fait le renommage directement.
            new_file_path = current_file_path.with_name(f"{new_stem}{current_file_path.suffix}")

            if new_file_path.exists():
                self.logger.warning(f"Le fichier de destination '{new_file_path}' existe déjà. Il sera écrasé.")
                new_file_path.unlink()

            current_file_path.rename(new_file_path)
            self.logger.info(f"Fichier '{current_file_path.name}' renommé en '{new_file_path.name}'.")
            return new_file_path
        except Exception as e:
            self.logger.error(f"Erreur lors du renommage de '{current_file_path.name}': {e}", exc_info=True)
            return None # Retourner None mais le fichier original existe toujours.


    def _close_ftp_connection(self):
        """Ferme la connexion FTP si elle est active."""
        if self.ftp_connection:
            self.logger.info("Fermeture de la connexion FTP...")
            try:
                self.ftp_connection.quit() # Utiliser quit() pour une fermeture propre
                self.logger.info("Connexion FTP fermée avec succès.")
            except (error_perm, error_temp) as e:
                self.logger.warning(f"Erreur FTP lors de la fermeture (quit): {e}. Tentative avec close().")
                try:
                    self.ftp_connection.close() # Fallback si quit() échoue
                    self.logger.info("Connexion FTP fermée avec close().")
                except Exception as e_close: # Attraper toute exception de close()
                    self.logger.error(f"Erreur lors de la tentative de fermeture (close) de la connexion FTP: {e_close}", exc_info=True)
            except Exception as e_generic: # Autres erreurs potentielles
                 self.logger.error(f"Erreur inattendue lors de la fermeture de la connexion FTP: {e_generic}", exc_info=True)
            finally:
                self.ftp_connection = None # S'assurer qu'elle est None après tentative


    @abstractmethod
    def process_ftp_operation(self):
        """
        Méthode abstraite principale pour orchestrer l'opération FTP spécifique (ex: télécharger et renommer).
        Les classes filles doivent implémenter cette méthode.
        """
        # Exemple d'implémentation possible dans une classe fille:
        # try:
        #     self._ftp_connect_and_login()
        #     self._delete_local_files_before_download()
        #     self._download_matching_files()
        #     verified_file = self._verify_download_locally(self.expected_filename_on_server)
        #     if verified_file:
        #         renamed_file = self._rename_downloaded_file(verified_file)
        #         if renamed_file:
        #             self.logger.info(f"Opération FTP pour {self.name} terminée. Fichier final: {renamed_file}")
        # except Exception as e:
        #     self.logger.critical(f"Échec du processus FTP pour {self.name}: {e}", exc_info=True)
        # finally:
        #     self._close_ftp_connection()
        pass

    def __del__(self):
        """Destructeur pour s'assurer que la connexion FTP est fermée."""
        # Éviter de logger dans __del__ si possible, car le logger peut être déjà nettoyé.
        # print(f"Destructeur de BaseFTP pour '{self.name}' appelé.")
        self._close_ftp_connection()