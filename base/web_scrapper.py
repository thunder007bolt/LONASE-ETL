from selenium import webdriver

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
from utils.file_manipulation import rename_file
"""
Classe pour scrapper un site Web.
"""


class BaseScrapper(ABC):
    def __init__(self, name: str, env_variables_list: list, log_file: str, chrome_options_arguments: list = []):
        configs = get_config(name)
        self.base_config = configs["base"]
        print(f"{configs}")
        self.config = configs[name]
        self.name = name
        self.chrome_options_arguments = chrome_options_arguments
        self.secret_config = get_secret(env_variables_list)
        self.browser = None
        logger = Logger(log_file=log_file).get_logger()
        self.logger = logger
        self.logger.info("Initialisation...")
        self.retry_count = 0

        ### Dates
        self.start_date: datetime
        self.end_date: datetime

    def _open_browser(self):
        """Ouvre le navigateur Chrome avec les options de téléchargement configurées."""
        self.logger.info("Ouverture du navigateur")
        for _ in range(5):
            try:
                download_path = fr"{self.config["download_path"].replace('/', '\\')}"
                chrome_options = webdriver.ChromeOptions()
                prefs = {"download.default_directory": download_path}
                chrome_options.add_experimental_option("prefs", prefs)
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
        if self.config["start_date"] is not None:
            self.start_date = self.config["start_date"]
        else:
            self.start_date = yesterday_date

        if self.config["end_date"] is not None:
            self.end_date = self.config["end_date"]
        else:
            self.end_date = yesterday_date

    @staticmethod
    def _get_by_type(locator_type):
        """Retourne le type de localisateur Selenium correspondant."""
        if locator_type == 'id':
            return By.ID
        elif locator_type == 'xpath':
            return By.XPATH
        elif locator_type == 'name':
            return By.NAME

    @abstractmethod
    def _connection_to_platform(self):
        pass

    @abstractmethod
    def _download_files(self):
        pass

    def _process_download(self, start_date, end_date):
        pass

    def _process_multiple_files(self):
        start_date = self.start_date
        # todo: +1 if include_sup equals true
        end_date = self.start_date
        delta = timedelta(days=1)
        while end_date <= self.end_date:
            sleep(2)
            self._process_download(start_date, end_date)
            try:
                self.start_date = start_date
                self._verify_download()
            except:
                self.logger.error(f"Le fichier du {start_date} n'a pas pu être téléchargé, Nous allons recommencer")
                #Faire juste 3 essais
                continue
            name = f"{self.name}_{start_date.strftime('%Y-%m-%d')}"
            file_pattern = self.config['file_pattern']
            rename_file(file_pattern, self.config["download_path"], name, self.logger)
            start_date += delta
            end_date += delta

    def _verify_download(self, file_pattern=None):
        def wait_for_download(pattern, timeout=120, poll_interval=2):
            """Attend l'apparition d'un fichier correspondant au motif donné."""
            self.logger.info(f"Attente de {timeout} secondes pour le téléchargement du fichier {pattern}")
            start_time = time.time()
            while time.time() - start_time < timeout:
                files = glob.glob(pattern)
                if files:
                    return files[0]
                time.sleep(poll_interval)
            return None
        file_pattern = file_pattern or self.config["file_pattern"]
        tmp_file = wait_for_download(os.path.join(self.config["download_path"],file_pattern), timeout=self.config["wait_time"], poll_interval=2)
        if not tmp_file:
            raise Exception("Téléchargement anormalement long, fichier non téléchargé")
            # self._download_files()
        else:
            self.logger.info(f"Le fichier du {self.start_date} a bien ete telecharge")

    def wait_and_click(self, element, locator_type='id', timeout=10, raise_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element)))
            element.click()
            return element
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_click(self, element, locator_type='xpath', timeout=10, raise_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            return  WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element)))
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_invisibility(self, element, locator_type='xpath', timeout=10, raise_error=False):
            by_type = self._get_by_type(locator_type)
            try:
                WebDriverWait(self.browser, timeout).until(EC.invisibility_of_element((by_type, element))).click()
            except:
                if raise_error:
                    raise(f"Élément non cliquable ou introuvable : {element}")
                self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_for_presence(self, element, locator_type='xpath', timeout=10, raise_error=False):
        by_type = self._get_by_type(locator_type)
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by_type, element)))
        except:
            if raise_error:
                raise(f"Élément introuvable : {element}")
            self.logger.warning(f"Élément introuvable : {element}")

    def wait_and_send_keys(self, element, locator_type='id', timeout=10, keys=None, raise_error=False):
        try:
            by_type = self._get_by_type(locator_type)
            WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((by_type, element))).send_keys(keys)
        except:
            if raise_error:
                raise(f"Élément non cliquable ou introuvable : {element}")
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def wait_element_visible(self, element, type='xpath', timeout=10):
        by_type = self._get_by_type(type)
        WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by_type, element)))

    def fill_select(self, element, type='id', value=None):
        try:
            by_type = self._get_by_type(type)
            (Select(self.browser.find_element(by=by_type, value=element))).select_by_visible_text(str(value))
        except:
            self.logger.warning(f"Élément non cliquable ou introuvable : {element}")

    def _quit(self, error=None):
        self.logger.info(f"erreur : {error}")
        self.logger.info(f"Fermeture de la fenêtre...")
        self.browser.quit()
        exit(1)

    def __del__(self):
        self.logger.info('------------ Ending --------------')
