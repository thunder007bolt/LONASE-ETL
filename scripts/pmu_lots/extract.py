### system ###
### base ###
from pathlib import Path

import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys

from base.web_scrapper import BaseScrapper
### utils ###
from utils.date_utils import sleep
from utils.file_manipulation import move_file


class ExtractPmuLots(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('pmu_lots', env_variables_list, 'logs/extract_pmu_lots.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        login_step1_xpath = html_elements["login_step1_xpath"]
        login_step2_xpath = html_elements["login_step2_xpath"]
        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["PMU_LOGIN_USERNAME"]
        password = secret_config["PMU_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_click(login_step1_xpath, locator_type='xpath')
        self.wait_and_click(login_step2_xpath, locator_type='xpath')
        self.wait_and_send_keys(username_xpath, locator_type='xpath', keys=username, raise_error=True)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath')

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_element_visible(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")
        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()
        sleep(10)
        pass

    def _download_files(self):
       self._process_multiple_files()

    def _process_download(self, start_date, end_date):
        browser = self.browser
        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        products = self.config['produits']

        datas = []
        for product in products:
            browser.get(reports_url)
            self.logger.info("Remplissage des champs de date...")
            html_elements = self.config['html_elements']

            date_element_xpath = html_elements["date_element_xpath"]
            product_element_xpath = html_elements["product_element_xpath"]
            submit_button_element_xpath = html_elements["submit_button_element_xpath"]
            step1_element_xpath = html_elements["step1_element_xpath"]
            step2_element_xpath = html_elements["step2_element_xpath"]
            step_element_xpath = html_elements["step_element_xpath"]

            date_element = self.wait_for_click(date_element_xpath, locator_type="xpath")
            date_element.clear()
            date_element.send_keys(str(start_date))

            self.fill_select(product_element_xpath, "xpath", value=product)

            self.logger.info("Soumission du formulaire...")
            self.wait_and_click(submit_button_element_xpath, locator_type="xpath")

            self.wait_for_invisibility(step_element_xpath, locator_type="xpath")
            sleep(2)

            while True:
                try:
                    table = self.wait_for_click(step1_element_xpath, locator_type="xpath", raise_error=True)
                except:
                    break

                df = pd.read_html(table.get_attribute('outerHTML'))
                df = df[0].dropna(axis=0, thresh=4)

                for index, row in df.iterrows():
                    for column in df.columns:
                        df.at[index, column] = str(row[column]).strip().replace('\u202f', ' ')
                    if len(str(df.at[index, 'Joueur'])) < 9:
                        df = df.drop(index=(index))

                df['produit'] = str(product)
                datas.append(df)

                step2_element = browser.find_elements(by=By.XPATH, value=step2_element_xpath)[-2]
                if 'disabled' in str(step2_element.get_attribute('class')):
                    break
                step2_element.click()

                try:
                    self.wait_for_invisibility(step_element_xpath, locator_type="xpath", raise_error=True)
                    sleep(2)
                except:
                    continue

        df = pd.concat(datas, ignore_index=True)
        try:
            df = df.drop(['Unnamed: 6'], axis=1)
        except:
            pass
        try:
            df = df.drop(['Unnamed: 7'], axis=1)
        except:
            pass
        try:
            df = df.drop(['Unnamed: 8'], axis=1)
        except:
            pass

        df['JOUR'] = str(start_date.strftime('%d/%m/%Y'))
        df['ANNEE'] = str(start_date.strftime('%Y'))
        df['MOIS'] = str(start_date.strftime('%m'))

        try:
            self.logger.info(f"Enregistrement du fichier PMU Senegal du {start_date} ...")
            filename = "Pmu_Senegal_lots_" + str(start_date) + ".csv"
            # todo: update path
            destination = Path(self.config["download_path"])
            final_file = destination / filename
            df.to_csv(final_file, index=False, sep=';', encoding='latin1')

        except Exception as e:
            self.logger.error(f"Erreur lors de la telechargement du fichier PMU Senegal : {e}")
            raise e
    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()


def run_pmu_lots():
    env_variables_list = ["PMU_LOGIN_USERNAME", "PMU_LOGIN_PASSWORD"]
    job = ExtractPmuLots(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_pmu_lots()
