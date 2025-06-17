### system ###
### base ###
from pathlib import Path

import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait

from base.web_scrapper import BaseScrapper
### utils ###
from utils.date_utils import sleep
from utils.file_manipulation import move_file


class ExtractZeturf(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('zeturf', env_variables_list, 'logs/extract_zeturf.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_id = html_elements["username_element_id"]
        password_id = html_elements["password_element_id"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["ZETURF_LOGIN_USERNAME"]
        password = secret_config["ZETURF_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_id, locator_type='id', timeout=10, keys=username, raise_error=True)
        self.wait_and_send_keys(password_id, locator_type='id', timeout=10, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath', timeout=10)

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_element_visible(verification_xpath, timeout=10)
            self.logger.info("Connexion à la plateforme réussie.")
        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()
        sleep(10)
        pass

    def _download_files(self):
        self._process_multiple_files(ignore=True)

    def _process_download(self, start_date, end_date):
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        download_path = Path(self.config["download_path"])
        file_pattern = self.config["file_pattern"]
        data_path = Path(self.base_config["paths"]["data_path"])
        browser.get(reports_url)

        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        date_selector_form_ui_from_id = html_elements["date_selector_form_ui_from_id"]
        date_selector_form_ui_to_id = html_elements["date_selector_form_ui_to_id"]
        date_selector_form_ui_submit_id = html_elements["date_selector_form_ui_submit_id"]

        start_date_formated = start_date.strftime('%d/%m/%Y')
        end_date_formated = end_date.strftime('%d/%m/%Y')

        self.wait_for_presence(date_selector_form_ui_from_id, locator_type="id", timeout=60)

        start = browser.find_element(by=By.ID, value=date_selector_form_ui_from_id)
        start.click()
        start.clear()
        start.send_keys(start_date_formated)
        sleep(1)

        end = browser.find_element(by=By.ID, value=date_selector_form_ui_to_id)
        end.click()
        end.clear()
        end.send_keys(end_date_formated)
        sleep(1)

        self.logger.info("Soumission du formulaire...")
        self.wait_and_click(date_selector_form_ui_submit_id, timeout=10)
        sleep(1)

        self.logger.info("Télechargement du fichier")
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        download_button_element_xpath = html_elements["download_button_element_xpath"]
        WebDriverWait(browser, timeout=15).until(
            EC.element_to_be_clickable((By.XPATH, download_button_element_xpath))).click()
        self._verify_download()
        self.logger.info("Transformation du fichier...")

        transformation_dest_path = data_path / self.config["transformation_dest_relative_path"]
        processed_dest_path = data_path / self.config["processed_dest_relative_path"]
        for file in download_path.glob(file_pattern):
            self.logger.info(f"Transformation du fichier {file}")
            df = pd.read_csv(file, delimiter=";")

            enjeux_vertical_element_xpath = self.config["html_elements"]["enjeux_vertical_element_xpath"]
            marge_vertical_element_xpath = self.config["html_elements"]["marge_vertical_element_xpath"]

            enjeux_vertical = self.browser.find_element(By.XPATH, enjeux_vertical_element_xpath).text
            marge_vertical = self.browser.find_element(By.XPATH, marge_vertical_element_xpath).text

            pari = df['Paris'][0]
            date = start_date.strftime('%d/%m/%Y')
            df.loc[len(df.index)] = ["", "", "",str(pari), str(enjeux_vertical), "",str(marge_vertical), date]

            df["Course"] = [str(i).replace(";",",") for i in df["Course"] ]
            df = df.replace(np.nan, '')
            df = df.astype(str)
            df['Date du départ'] = date
            df['Annulations'] = ''
            filename = f"{self.name}_{start_date.strftime('%Y-%m-%d')}.csv"
            df.to_csv(transformation_dest_path / filename, index=False, sep=";", encoding='utf8')


            filesInitialDirectory = r"K:\DATA_FICHIERS\ZETURF\\"
            df['Date du dÃ©part'] = start_date.strftime('%d/%m/%Y')
            df.to_csv(filesInitialDirectory + "ZEturf " + start_date.strftime('%Y-%m-%d') + ".csv", index=False, sep=';', encoding='utf8')

            move_file(file, processed_dest_path)

    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()

def run_zeturf():
    env_variables_list = ["ZETURF_LOGIN_USERNAME", "ZETURF_LOGIN_PASSWORD"]
    job = ExtractZeturf(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_zeturf()
