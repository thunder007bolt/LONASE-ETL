### system ###
import glob
import pandas as pd
from lxml.html.defs import table_tags

### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import sleep
from datetime import timedelta
from pathlib import Path


class ExtractGitechTirage(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('gitech_tirage', env_variables_list, 'logs/extract_gitech_tirage.log')
        self.file_path = None

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        usernameId = html_elements["username_element_id"]
        passwordId = html_elements["password_element_id"]
        submit_buttonId = html_elements["login_submit_button_element_id"]
        username = secret_config["GITECH_LOGIN_USERNAME"]
        password = secret_config["GITECH_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(element=usernameId, keys=username, raise_error=True)
        self.wait_and_send_keys(element=passwordId, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(element=submit_buttonId)

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, raise_error=True)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        sleep(10)
        pass

    def _download_files(self):
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        # start_date
        start_date_day_element_id = html_elements["start_date_day_element_id"]
        start_date_month_element_id = html_elements["start_date_month_element_id"]
        start_date_year_element_id = html_elements["start_date_year_element_id"]
        # end_date
        end_date_day_element_id = html_elements["end_date_day_element_id"]
        end_date_month_element_id = html_elements["end_date_month_element_id"]
        end_date_year_element_id = html_elements["end_date_year_element_id"]
        error_message_element_xpath = html_elements["error_message_element_xpath"]

        start_date = self.start_date
        # todo: +1 if include_sup equals true
        end_date = self.start_date
        delta = timedelta(days=1)
        sleep(2)
        while end_date <= self.end_date:
            year, month, day = start_date.strftime("%Y-%m-%d").split("-")
            sleep(2)
            self.fill_select(start_date_day_element_id, value=day)
            self.fill_select(start_date_month_element_id, value=month)
            self.fill_select(start_date_year_element_id, value=year)

            self.fill_select(end_date_day_element_id, value=day)
            self.fill_select(end_date_month_element_id, value=month)
            self.fill_select(end_date_year_element_id, value=year)


            self.logger.info("Soumission du formulaire...")
            submit_button_element_id = html_elements["submit_button_element_id"]
            self.wait_and_click(submit_button_element_id, locator_type='id', timeout=15)

            self.logger.info("Vérification du resultat...")
            try:
                self.wait_for_presence(error_message_element_xpath, locator_type='xpath', timeout=5, raise_error=True)
                self.logger.error(f"Le fichier du {year}-{month}-{day} n'existe pas")
                self._quit()
            except:
                pass

            table_xpath = html_elements['table_xpath']
            mini_table_xpath = html_elements['mini_table_xpath']
            button_xpath = html_elements['button_xpath']
            table = self.wait_for_click(table_xpath)
            df_combined = pd.DataFrame()
            dfs = pd.read_html(table.get_attribute('outerHTML'), encoding='ISO-8859-1', thousands='.') 
            df = dfs[0].dropna(axis=0, thresh=4)

            
            for i in  range(0,len(table.find_elements(by=By.TAG_NAME, value='a'))):
                table = self.wait_for_click(table_xpath)
                a = table.find_elements(by=By.TAG_NAME, value="a")[i]
                a.click()
                
                mini_table = self.wait_for_click(mini_table_xpath)
                
                mini_dfs = pd.read_html(mini_table.get_attribute('outerHTML'), encoding='ISO-8859-1',thousands='.')

                mini_df = mini_dfs[0].dropna(axis=0, thresh=4)
                mini_df['Nom des jeux'] = df.iloc[i, 2]
                mini_df['Date du tirage'] = df.iloc[i, 4]
                mini_df['Lieu de jeu'] = df.iloc[i, 1]
                mini_df['N° Tirage'] = df.iloc[i, 3]
                mini_df['Heure de la course'] = df.iloc[i, 5]
                mini_df['Clôture des paris'] = df.iloc[i, 6]
                mini_df['N° Ticket'] = df.iloc[i, 7]

                df_combined = pd.concat([df_combined, mini_df], ignore_index=True)

                self.wait_and_click(button_xpath, locator_type="xpath")

            self.logger.info("Déplacement du fichier...")
            name = f"{self.name}_{start_date.strftime('%Y-%m-%d')}.csv"
            file = Path(self.config["download_path"]) / name
            df_combined.to_csv(file,sep=';',index=False, encoding='ISO-8859-1')
            start_date += delta
            end_date += delta

def run_gitech_tirage():
    env_variables_list = ["GITECH_LOGIN_USERNAME", "GITECH_LOGIN_PASSWORD"]
    job = ExtractGitechTirage(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_gitech_tirage()
