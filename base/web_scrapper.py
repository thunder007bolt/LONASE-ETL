from selenium import webdriver
from pathlib import Path

from abc import ABC, abstractmethod
import time, os, glob
from datetime import timedelta
from time import sleep

from base.logger import Logger
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.file_manipulation import rename_file, delete_file
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


"""
Classe pour scrapper un site Web.
"""


class BaseScrapper(ABC):
    def __init__(
            self,
            name: str,
            env_variables_list: list,
            log_file: str,
            chrome_options_arguments: list = [],
            start_date = None,
            end_date= None
    ):
        configs = get_config(name)
        self.base_config = configs["base"]
        self.config = configs[name]
        self.name = name
        self.chrome_options_arguments = chrome_options_arguments
        self.secret_config = get_secret(env_variables_list)
        self.browser = None
        # logger
        logger = Logger(log_file=log_file).get_logger()
        self.logger = logger
        self.logger.info("Initialisation...")

        self.retry_count = 0

        data_path = Path(self.base_config["paths"]["data_path"])
        self.extraction_dest_path = data_path / self.config["extraction_dest_relative_path"]
        self.transformation_dest_path = data_path / self.config["transformation_dest_relative_path"]

        ### Dates
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date

    def process_extraction(self):
        self._set_date()
        self._delete_old_files()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()

    def _open_browser(self):
        """Ouvre le navigateur Chrome avec les options de téléchargement configurées."""
        self.logger.info("Ouverture du navigateur")
        for _ in range(5):
            try:
                #os.system("taskkill /im chrome.exe /f")
                download_path = fr"{self.config["download_path"].replace('/', '\\')}"
                chrome_options = webdriver.ChromeOptions()
                prefs = {
                    "download.default_directory": download_path
                }
                chrome_options.add_experimental_option("prefs", prefs)
                #chrome_options.add_argument("--headless")
                #chrome_options.add_argument("--disable-gpu")
                if len(self.chrome_options_arguments) > 0:
                    for argument in self.chrome_options_arguments:
                        chrome_options.add_argument(argument)
                browser = webdriver.Chrome(options=chrome_options)
                self.browser = browser
                break

            except Exception as e:
                self.logger.error(f"Erreur lors de l'ouverture du navigateur : {e}")

    def _set_date(self):
        _, _, _, yesterday_date = get_yesterday_date()
        self.start_date = self.start_date or self.config.get("start_date") or yesterday_date
        self.end_date = self.end_date or self.config.get("end_date") or yesterday_date

    @staticmethod
    def _get_by_type(locator_type):
        """Retourne le type de localisateur Selenium correspondant."""
        if locator_type == 'id':
            return By.ID
        elif locator_type == 'xpath':
            return By.XPATH
        elif locator_type == 'name':
            return By.NAME
        elif locator_type == 'tag':
            return By.TAG_NAME

    @abstractmethod
    def _connection_to_platform(self):
        pass

    @abstractmethod
    def _download_files(self):
        pass

    def _process_download(self, start_date, end_date):
        pass

    def _delete_old_files(self):
        self.logger.info("Suppression des fichiers existant...")
        delete_file(self.config["download_path"], "*")

    def _process_transformation(self, file_pattern, date):
        pass
    def _handle_success_download(self, start_date):
        pass
    def _handle_failed_download(self, start_date):
        return True

    def _process_multiple_files(self, ignore=False):
        start_date = self.start_date
        # todo: +1 if include_sup equals true
        end_date = self.start_date
        delta = timedelta(days=1)
        while end_date <= self.end_date:
            try:
                sleep(2)
                self._process_download(start_date, end_date)
                # todo: renomer ignore
                if ignore is False:
                    try:
                        self.start_date = start_date
                        self._verify_download()
                    except:
                        self.logger.error(
                            f"Le fichier du {start_date} n'a pas pu être téléchargé, Nous allons recommencer")
                        # Faire juste 3 essais
                        result = self._handle_failed_download(start_date)
                        if result:
                            continue
                        else:
                            break
                    name = f"{self.name}_{start_date.strftime('%Y-%m-%d')}"
                    file_pattern = self.config['file_pattern']
                    rename_file(file_pattern, self.config["download_path"], name, self.logger)
                    self._process_transformation(name, start_date)
                    self._handle_success_download(start_date)
            except (RuntimeError, IndexError) as e:
                self.logger.error(f"Erreur lors du traitement de start_date : {start_date}")

            start_date += delta
            end_date += delta

    def _verify_download_opt(self, file_pattern=None, start_date=None, patterns=None):
        def wait_for_download(download_path, file_pattern, patterns=None, timeout=120, poll_interval=2):
            """Attend l'apparition d'un fichier correspondant au motif donné."""
            self.logger.info(f"Attente de {timeout} secondes pour le téléchargement du fichier {file_pattern}")
            start_time = time.time()
            while time.time() - start_time < timeout:
                files = glob.glob(os.path.join(download_path, file_pattern))
                if patterns:
                    for file in files:
                        # Vérifie si tous les motifs sont présents
                        if all(pat in file for pat in patterns):
                            self.logger.info(f"Fichier trouvé correspondant aux motifs : {file}")
                            return file
                elif files:
                    self.logger.info(f"Fichier trouvé : {files[0]}")
                    return files[0]
                time.sleep(poll_interval)
            self.logger.warning(f"Aucun fichier trouvé pour {file_pattern} après {timeout} secondes")
            return None

        file_pattern = file_pattern or self.config["file_pattern"]
        download_path = self.config["download_path"]
        tmp_file = wait_for_download(download_path, file_pattern, patterns, timeout=self.config["wait_time"],
                                     poll_interval=2)
        if not tmp_file:
            raise Exception(f"Téléchargement anormalement long, fichier non téléchargé pour le motif {file_pattern}")
        else:
            self.logger.info(f"Le fichier du {start_date or self.start_date} a bien été téléchargé : {tmp_file}")
            return tmp_file

    def _verify_download_v2(self, file_pattern: str = None, target_date: datetime.date = None, patterns_in_name: list = None, timeout: int = None) -> Path:
        """
        Attend et vérifie l'apparition d'un fichier téléchargé correspondant
        à un motif dans le répertoire de téléchargement.

        Args:
            file_pattern (str, optional): Motif Glob pour rechercher le fichier. Utilise config['file_pattern'] si None.
            target_date (datetime.date, optional): Date concernée (pour le logging). Utilise self.start_date si None.
            patterns_in_name (list, optional): Liste de chaînes qui doivent être présentes dans le nom du fichier trouvé.
            timeout (int, optional): Temps d'attente maximum en secondes. Utilise config['wait_time'] si None.

        Raises:
            TimeoutException: Si le fichier n'est pas trouvé dans le délai imparti.

        Returns:
            Path: Chemin d'accès au fichier téléchargé vérifié.
        """
        effective_pattern = file_pattern or self.config.get("file_pattern", "*")
        effective_timeout = timeout or self.config.get("wait_time", 120)
        log_date_str = (target_date or self.start_date).strftime('%Y-%m-%d')

        self.logger.info(f"Attente ({effective_timeout}s max) du fichier pour la date {log_date_str} correspondant à '{effective_pattern}' dans {self.extraction_dest_path}")
        if patterns_in_name:
            self.logger.info(f"Le nom du fichier doit aussi contenir: {patterns_in_name}")

        start_time = time.time()
        poll_interval = 2 # secondes

        while time.time() - start_time < effective_timeout:
            # Recherche des fichiers correspondant au motif principal
            found_files = list(self.extraction_dest_path.glob(effective_pattern))

            # Filtrage supplémentaire si patterns_in_name est fourni
            valid_files = []
            if found_files:
                 # Exclure les fichiers temporaires courants
                 potential_files = [
                     f for f in found_files
                     if not f.name.endswith(('.tmp', '.crdownload', '.part'))
                        and f.stat().st_size > 1024  # Exclure les fichiers ≤ 1 Ko
                ]

                 if patterns_in_name:
                    for file_path in potential_files:
                         # Vérifie si TOUS les motifs requis sont dans le nom du fichier
                         if all(p in file_path.name for p in patterns_in_name):
                             valid_files.append(file_path)
                 else:
                     valid_files = potential_files # Prend tous les fichiers non temporaires si pas de motifs spécifiques

            if valid_files:
                 # Pour l'instant, on prend le premier fichier valide trouvé.
                 #Todo:  Ajouter une logique pour choisir le plus récent si plusieurs correspondent.
                 found_file_path = valid_files[0]
                 self.logger.info(f"Fichier trouvé pour la date {log_date_str}: {found_file_path.name}")
                 return found_file_path

            # Attendre avant la prochaine vérification
            time.sleep(poll_interval)

        # Si la boucle se termine sans trouver de fichier
        self.logger.error(f"Timeout: Aucun fichier correspondant trouvé pour la date {log_date_str} et le motif '{effective_pattern}' après {effective_timeout} secondes.")
        raise TimeoutException(f"Téléchargement non détecté ou anormalement long pour la date {log_date_str} (motif: {effective_pattern})")

    def _verify_download_v3(self, file_pattern: str = None, target_date: datetime.date = None,
                            patterns_in_name: list = None, timeout: int = None, files_before_click: set = None) -> Path:
        effective_pattern = file_pattern or self.config.get("file_pattern",
                                                            "*BettingOperation*xlsx")  # Soyez spécifique si possible
        effective_timeout = timeout or self.config.get("wait_time", 300)

        # Utilise target_date si fourni (date de début du rapport), sinon une date par défaut.
        log_date_str = (target_date if target_date else getattr(self, 'start_date', datetime.date.today())).strftime(
            '%Y-%m-%d')

        self.logger.info(
            f"Attente ({effective_timeout}s max) du fichier pour la date de référence {log_date_str} correspondant à '{effective_pattern}' dans {self.extraction_dest_path}")
        if patterns_in_name:
            self.logger.info(f"Le nom du fichier doit aussi contenir: {patterns_in_name}")
        if files_before_click is not None:  # Logique pour identifier le NOUVEAU fichier
            self.logger.info(
                f"Mode de détection du nouveau fichier activé (comparaison avec {len(files_before_click)} fichier(s) préexistants).")

        start_time = time.time()
        poll_interval = 2  # secondes

        while time.time() - start_time < effective_timeout:
            # Liste tous les fichiers correspondant au pattern global dans le dossier
            current_files_on_disk = list(self.extraction_dest_path.glob(effective_pattern))

            candidate_files = []
            if files_before_click is not None:
                # Si files_before_click est fourni, on ne considère que les nouveaux fichiers
                newly_appeared = [f for f in current_files_on_disk if f not in files_before_click]
                candidate_files = [f for f in newly_appeared if not f.name.endswith(('.tmp', '.crdownload', '.part'))]
            else:
                # Comportement original: considère tous les fichiers non temporaires
                candidate_files = [f for f in current_files_on_disk if
                                   not f.name.endswith(('.tmp', '.crdownload', '.part'))]

            valid_files = []
            if candidate_files:
                if patterns_in_name:  # Filtrage additionnel par `patterns_in_name`
                    for file_path in candidate_files:
                        if all(p in file_path.name for p in patterns_in_name):
                            valid_files.append(file_path)
                else:
                    valid_files = candidate_files

            if valid_files:
                # Trie les fichiers par date de modification (le plus récent en premier)
                # C'est crucial si plusieurs fichiers correspondent (ex: un ancien téléchargement partiel)
                valid_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

                # Prend le fichier le plus récent
                found_file_path = valid_files[0]

                # Vérification supplémentaire de la stabilité du fichier (taille ne change plus)
                try:
                    last_size = -1
                    stable_count = 0
                    # Attendre que la taille du fichier se stabilise pendant un court instant
                    for _ in range(3):  # Check 3 times
                        current_size = found_file_path.stat().st_size
                        if current_size > 0 and current_size == last_size:  # Fichier non vide et taille stable
                            stable_count += 1
                            break
                        elif current_size == 0 and last_size == 0:  # Fichier vide, mais taille stable (peut être un problème)
                            pass  # On continue de vérifier, peut-être qu'il va grossir
                        last_size = current_size
                        time.sleep(0.5)  # Court délai entre les vérifications de taille

                    if stable_count > 0 or (
                            found_file_path.stat().st_size > 0 and time.time() - found_file_path.stat().st_mtime > 5):  # Soit stable, soit >0 octets et existe depuis >5s
                        self.logger.info(
                            f"Fichier trouvé et considéré stable pour la date {log_date_str}: {found_file_path.name} (taille: {found_file_path.stat().st_size} octets)")
                        return found_file_path
                    else:
                        self.logger.debug(
                            f"Fichier {found_file_path.name} trouvé mais sa taille ({found_file_path.stat().st_size} octets) n'est pas encore stable ou est nulle. Attente...")
                except FileNotFoundError:
                    self.logger.debug(f"Fichier {found_file_path.name} a disparu pendant la vérification de stabilité.")
                    # Continue la boucle while pour chercher à nouveau

            time.sleep(poll_interval)

        self.logger.error(
            f"Timeout: Aucun fichier correspondant et stable trouvé pour la date {log_date_str} et le motif '{effective_pattern}' après {effective_timeout} secondes.")
        raise TimeoutException(
            f"Téléchargement non détecté, anormalement long, ou fichier vide/instable pour la date de référence {log_date_str} (motif: {effective_pattern})")

    def _verify_download(self, file_pattern=None, start_date=None, patterns=None):
        def wait_for_download(pattern, timeout=120, poll_interval=2):
            """Attend l'apparition d'un fichier correspondant au motif donné."""
            #todo: s'assurrer à un moment ou à un autre que le téléchargement progresse bien
            self.logger.info(f"Attente de {timeout} secondes pour le téléchargement du fichier {pattern}")
            start_time = time.time()
            while time.time() - start_time < timeout:
                files = glob.glob(pattern)
                if patterns is not None :
                    temp = True
                    for file in files:
                        for pat in patterns:
                            temp = True
                            if pat not in file:
                                temp = False
                                break
                        if temp == True :
                            return file
                elif files:

                    return files[0]
                time.sleep(poll_interval)
            return None
        file_pattern = file_pattern or self.config["file_pattern"]
        tmp_file = wait_for_download(os.path.join(self.config["download_path"],file_pattern), timeout=self.config["wait_time"], poll_interval=2)
        if not tmp_file:
            raise Exception("Téléchargement anormalement long, fichier non téléchargé")
            # self._download_files()
        else:
            tmp_file = Path(tmp_file)
            self.logger.info(
                f"Le fichier {tmp_file.name} a bien ete telecharge")
            return tmp_file

    def wait_and_click(self, element, locator_type='id', timeout=60, raise_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element)))
            element.click()
            return element
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_click(self, element, locator_type='xpath', timeout=60, raise_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            return  WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element)))
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_invisibility(self, element, locator_type='xpath', timeout=60, raise_error=False, exit_on_error=False):
            by_type = self._get_by_type(locator_type)
            try:
                WebDriverWait(self.browser, timeout).until(EC.invisibility_of_element((by_type, element)))
            except:
                if exit_on_error:
                    self.logger.error(f"Élément n'a pas disparu : {element}")
                    exit(1)
                if raise_error:
                    raise(f"Élément non cliquable ou introuvable : {element}")
                self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_presence(self, element, locator_type='xpath', timeout=60, raise_error=False, exit_on_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by_type, element)))
        except:
            if exit_on_error:
                self.logger.error(f"Élément n'est pas apparu : {element}")
                exit(1)
            if raise_error:
                raise(f"Élément introuvable : {element}")
            self.logger.warning(f"Élément introuvable : {element}")

    def wait_and_send_keys(self, element, locator_type='id', timeout=60, keys=None, raise_error=False):
        try:
            by_type = self._get_by_type(locator_type)
            WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element))).send_keys(keys)
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_and_send_keys2(self, element, locator_type='id', timeout=60, keys=None, raise_error=False):
        try:
            by_type = self._get_by_type(locator_type)
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by_type, element))).send_keys(keys)
        except:
            if raise_error:
                raise (f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_element_visible(self, element, type='xpath', timeout=60):
        by_type = self._get_by_type(type)
        WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by_type, element)))

    def fill_select(self, element, type='id', value=None):
        try:
            by_type = self._get_by_type(type)
            (Select(self.browser.find_element(by=by_type, value=element))).select_by_visible_text(str(value))
        except:
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_staleness(self, element, timeout=30):
        """Attend qu'un élément devienne obsolète (stale)."""
        try:
            WebDriverWait(self.browser, timeout).until(EC.staleness_of(element))
            self.logger.info("L'ancien élément table est devenu obsolète (stale).")
            return True
        except TimeoutException:
            self.logger.warning(f"Timeout ({timeout}s) en attendant que l'élément devienne obsolète.")
            return False
        except Exception as e:
            self.logger.error(f"Erreur inattendue pendant wait_for_staleness : {e}")
            return False

    def _quit(self, error=None):
        self.logger.info(f"erreur : {error}")
        self.logger.info(f"Fermeture de la fenêtre...")
        self.browser.quit()
        exit(1)

    def __del__(self):
        self.logger.info('------------ Ending --------------')
