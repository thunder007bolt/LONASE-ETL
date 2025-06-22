import glob
import time
from datetime import timedelta, date
import pandas as pd
import os

from base.web_scrapper import BaseScrapper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.date_utils import sleep

class ExtractLonasebetGlobal(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('lonasebet_global', env_variables_list,
                         'logs/extract_lonasebet_global.log')
        self.excl_list = []
        self.type_canal = ''
        self.categorie_jeux = ''

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        username = self.secret_config["LONASEBET_GLOBAL_LOGIN_USERNAME"]
        password = self.secret_config["LONASEBET_GLOBAL_LOGIN_PASSWORD"]

        username_xpath = html_elements["username_element_xpath"]
        password_xpath = html_elements["password_element_xpath"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(username_xpath, locator_type='xpath', timeout=90, keys=username, raise_error=True)
        self.wait_and_send_keys(password_xpath, locator_type='xpath', timeout=10, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath', timeout=10)
        sleep(2)

        try:
            self.logger.info("Vérification de la connexion...")
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, raise_error=True, timeout=90)
            self.logger.info("Connexion à la plateforme réussie.")
        except Exception as error:
            self.logger.error(f"Connexion à la plateforme n'a pas pu être établie: {error}")
            self._quit(error)

    def _navigate_to_analysis_page(self):
        self.logger.info("Navigation vers la page d'analyse des paris...")
        analysis_url = self.config['urls']['analysis']
        self.browser.get(analysis_url)
        self.wait_for_presence(self.config['html_elements']['date_picker_button_xpath'], timeout=60)
        self.logger.info("Page d'analyse chargée.")
        sleep(5)

    def _click_categorie_type(self, category_method_name):
        self.logger.debug(f"Ouverture du dropdown catégorie.")
        self.wait_and_click(self.config['html_elements']['category_dropdown_xpath'], locator_type='xpath')
        sleep(0.5)

        category_methods = {
            'click_masse_commune': self._select_masse_commune,
            'click_masse_separee': self._select_masse_separee,
            'click_sport': self._select_sport,
            'click_virtuel': self._select_virtuel,
            'click_casino': self._select_casino,
        }
        if category_method_name in category_methods:
            category_methods[category_method_name]()
        else:
            self.logger.error(f"Méthode de catégorie inconnue: {category_method_name}")
            self._close_category_dropdown()
            raise ValueError(f"Méthode de catégorie inconnue: {category_method_name}")

    def _select_masse_commune(self):
        self.categorie_jeux = 'Hippique masse commune internationale'
        self.logger.info(f"Sélection de la catégorie: {self.categorie_jeux}")
        self.wait_and_click(self.config['html_elements']['masse_commune_option_xpath'], locator_type='xpath')
        self._close_category_dropdown()

    def _select_masse_separee(self):
        self.categorie_jeux = 'Hippique masse séparée'
        self.logger.info(f"Sélection de la catégorie: {self.categorie_jeux}")
        self.wait_and_click(self.config['html_elements']['masse_separee_option_xpath'], locator_type='xpath')
        self._close_category_dropdown()

    def _select_sport(self):
        self.categorie_jeux = 'Sports'
        self.logger.info(f"Sélection de la catégorie: {self.categorie_jeux}")
        self.wait_and_click(self.config['html_elements']['sports_option_xpath'], locator_type='xpath')
        self._close_category_dropdown()

    def _select_virtuel(self):
        self.categorie_jeux = 'Virtuel'
        self.logger.info(f"Sélection de la catégorie: {self.categorie_jeux}")
        self.wait_and_click(self.config['html_elements']['virtuel_option_xpath'], locator_type='xpath')
        self._close_category_dropdown()

    def _select_casino(self):
        self.categorie_jeux = 'Jeux instantanés'
        self.logger.info(f"Sélection de la catégorie: {self.categorie_jeux}")
        self.wait_and_click(self.config['html_elements']['casino_option_xpath'], locator_type='xpath')
        self._close_category_dropdown()

    def _close_category_dropdown(self):
        self.logger.debug(f"Fermeture du dropdown catégorie.")
        self.wait_and_click(self.config['html_elements']['close_category_dropdown_xpath'], locator_type='xpath')
        sleep(0.5)

    def _click_canal_type(self, canal_method_name):
        self.logger.debug(f"Ouverture du dropdown canal.")
        self.wait_and_click(self.config['html_elements']['channel_dropdown_xpath'], locator_type='xpath')
        sleep(0.5)

        canal_methods = {
            'click_canal_online': self._select_canal_online,
            'click_canal_retail': self._select_canal_retail,
        }
        if canal_method_name in canal_methods:
            canal_methods[canal_method_name]()
        else:
            self.logger.error(f"Méthode de canal inconnue: {canal_method_name}")
            self._close_canal_dropdown()
            raise ValueError(f"Méthode de canal inconnue: {canal_method_name}")

    def _select_canal_online(self):
        self.type_canal = 'online'
        self.logger.info(f"Sélection du canal: {self.type_canal}")
        self.wait_and_click(self.config['html_elements']['online_channel_option_xpath'], locator_type='xpath')
        self._close_canal_dropdown()

    def _select_canal_retail(self):
        self.type_canal = 'retail'
        self.logger.info(f"Sélection du canal: {self.type_canal}")
        self.wait_and_click(self.config['html_elements']['retail_channel_option_xpath'], locator_type='xpath')
        self._close_canal_dropdown()

    def _close_canal_dropdown(self):
        self.logger.debug(f"Fermeture du dropdown canal.")
        self.wait_and_click(self.config['html_elements']['close_channel_dropdown_xpath'], locator_type='xpath')
        sleep(0.5)

    def _pick_date_on_calendar(self, current_date):
        self.logger.info(f"Sélection de la date: {current_date.strftime('%Y-%m-%d')}")
        html_elements = self.config['html_elements']

        self.wait_and_click(html_elements['date_picker_button_xpath'], locator_type='xpath')
        sleep(0.5)

        self.wait_and_click(html_elements['year_picker_button_xpath'], locator_type='xpath')
        sleep(0.5)
        year_elements = self.browser.find_elements(by=By.XPATH, value=html_elements['year_list_xpath'])
        for el in year_elements:
            if current_date.strftime('%Y') in el.text:
                el.click()
                sleep(0.5)
                break

        month_elements = self.browser.find_elements(by=By.XPATH, value=html_elements['month_list_xpath'])
        for el in month_elements:
            if current_date.strftime('%b').lower() in el.text.lower():
                el.click()
                sleep(0.5)
                break

        day_elements = self.browser.find_elements(by=By.XPATH, value=html_elements['day_list_xpath'])
        day_str = current_date.strftime('%d')
        for el in day_elements:
            if el.text.strip() == day_str.lstrip('0'):
                el.click()
                sleep(0.5)
                el.click()
                sleep(0.5)
                break

        self.logger.info(f"Date {current_date.strftime('%Y-%m-%d')} sélectionnée.")

    def _click_search_button(self):
        self.logger.info("Clic sur le bouton de recherche...")
        self.wait_and_click(self.config['html_elements']['search_button_xpath'], locator_type='xpath')
        sleep(3)

    def _extract_data_from_table(self, current_date):
        self.logger.info(f"Extraction des données pour le {current_date.strftime('%Y-%m-%d')}, Canal: {self.type_canal}, Catégorie: {self.categorie_jeux}")

        my_dict = {}
        try:
            self.wait_for_presence(self.config['html_elements']['data_table_rows_xpath'], timeout=10)
            data_rows = self.browser.find_elements(by=By.XPATH, value=self.config['html_elements']['data_table_rows_xpath'])
            if not data_rows:
                self.logger.warning("Aucune ligne de données trouvée dans le tableau.")

            for line_element in data_rows:
                parts = line_element.text.strip().split('\n')
                if len(parts) == 2:
                    key = parts[0]
                    value = parts[1].replace("FCFA","").replace(" ","")
                    my_dict[key] = value
                else:
                    self.logger.warning(f"Ligne de données malformée: {line_element.text.strip()}")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données du tableau: {e}")

        df = pd.DataFrame([my_dict])
        df['JOUR'] = str(current_date.strftime('%d/%m/%Y'))
        df['ANNEE'] = str(current_date.strftime('%Y'))
        df['MOIS'] = str(current_date.strftime('%m'))
        df['CANAL'] = self.type_canal
        df['CATEGORIE'] = self.categorie_jeux

        self.excl_list.append(df)
        self.logger.info(f"Données extraites et ajoutées. Lignes pour cette combinaison: {len(df)}")

    def _generate_and_extract_for_date(self, current_date):
        self.logger.info(f"Début de la génération et extraction pour la date: {current_date.strftime('%Y-%m-%d')}")
        self.excl_list = []

        self._pick_date_on_calendar(current_date)

        categories_methods_names = [
            'click_masse_commune', 'click_masse_separee', 'click_sport',
            'click_virtuel', 'click_casino'
        ]
        canaux_methods_names = ['click_canal_online', 'click_canal_retail']

        for canal_method_name in canaux_methods_names:
            self._click_canal_type(canal_method_name)

            for cat_method_name in categories_methods_names:
                self._click_categorie_type(cat_method_name)

                self._click_search_button()
                self._extract_data_from_table(current_date)

                self._click_categorie_type(cat_method_name)
                sleep(0.5)

            self._click_canal_type(canal_method_name)
            sleep(0.5)

        if self.excl_list:
            current_date_df = pd.concat(self.excl_list, ignore_index=True)

            output_dir = self.extracted_path

            os.makedirs(output_dir, exist_ok=True)

            filename = f"globalLonasebet_{current_date.strftime('%Y-%m-%d')}.csv"
            filepath = os.path.join(output_dir, filename)

            self.logger.info(f"Sauvegarde du fichier: {filepath}")
            current_date_df.to_csv(filepath, index=False, sep=';', encoding='latin1')
            self.logger.info(f"Fichier {filename} sauvegardé avec {len(current_date_df)} lignes.")
        else:
            self.logger.warning(f"Aucune donnée à sauvegarder pour le {current_date.strftime('%Y-%m-%d')}")

    def process_extraction(self):
        self._set_date()
        self._open_browser()

        try:
            self._connection_to_platform()
            self._navigate_to_analysis_page()

            current_processing_date = self.start_date
            delta = timedelta(days=1)

            while current_processing_date <= self.end_date:
                self.logger.info(f"Traitement pour la date : {current_processing_date.strftime('%Y-%m-%d')}")
                try:
                    self._generate_and_extract_for_date(current_processing_date)
                except Exception as e:
                    self.logger.error(f"Erreur majeure lors du traitement de la date {current_processing_date.strftime('%Y-%m-%d')}: {e}")
                current_processing_date += delta

            self.logger.info("Extraction terminée pour toutes les dates.")

        except Exception as e:
            self.logger.critical(f"Erreur critique pendant le processus d'extraction, arrêt: {e}")
            self._quit(e)
        finally:
            self._close_browser()

def run_lonasebet_global_extractor():
    env_vars = ["LONASEBET_GLOBAL_LOGIN_USERNAME", "LONASEBET_GLOBAL_LOGIN_PASSWORD"]
    job = ExtractLonasebetGlobal(env_variables_list=env_vars)
    job.process_extraction()

if __name__ == "__main__":
    run_lonasebet_global_extractor()
