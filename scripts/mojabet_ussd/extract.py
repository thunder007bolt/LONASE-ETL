### system ###
### base ###
from datetime import timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait

from base.web_scrapper import BaseScrapper

### utils ###
from utils.date_utils import get_yesterday_date, sleep
from pathlib import Path

from utils.file_manipulation import rename_file


class ExtractMojabetUSSD(BaseScrapper):
    def __init__(self, env_variables_list):
        chrome_options_arguments = [
            "--unsafely-treat-insecure-origin-as-secure=http://115.110.148.83/bwinnersmis/Administration/"
        ]
        super().__init__('mojabet_ussd', env_variables_list, 'logs/extract_mojabet_ussd.log',
                         chrome_options_arguments=chrome_options_arguments)

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.set_page_load_timeout(600)
        browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        usernameId = html_elements["username_element_id"]
        passwordId = html_elements["password_element_id"]
        submit_button_xpath = html_elements["login_submit_button_element_xpath"]
        username = secret_config["ACAJOU_DIGITAL_LOGIN_USERNAME"]
        password = secret_config["ACAJOU_DIGITAL_LOGIN_PASSWORD"]

        self.logger.info("Saisie des identifiants...")
        self.wait_and_send_keys(usernameId, locator_type='id', timeout=10, keys=username, raise_error=True)
        self.wait_and_send_keys(passwordId, locator_type='id', timeout=10, keys=password, raise_error=True)

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type='xpath', timeout=10)

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath, raise_error=True, timeout=10 * 9)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        pass

    def _download_files(self):
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.set_page_load_timeout(600)
        browser.get(reports_url)

        xpath_1 = '//*[@id="searchFilters"]/div/div[1]/div[4]/span/span[1]/span/ul/li/input'
        element = self.wait_for_presence(xpath_1)
        element.send_keys("USSD")
        element.send_keys(Keys.ENTER)

        self.logger.info("Remplissage des champs de date...")
        html_elements = self.config['html_elements']
        date_element_name = html_elements["date_element_name"]

        produit = ['DIGITAIN', 'PICKTHREE', 'SCRATCHCARD']
        start_date = self.start_date
        delta = timedelta(days=1)
        end_date = self.start_date + delta

        while end_date <= (self.end_date + delta):
            formatted_date = f"{start_date.strftime('%Y/%m/%d')} 00:00:00 - {start_date.strftime('%Y/%m/%d')} 23:59:59"

            date_element = self.wait_for_click(date_element_name, locator_type='name', timeout=15, raise_error=True)
            date_element.clear()
            date_element.send_keys(formatted_date)
            date_element.send_keys(Keys.ENTER)

            newlist = []

            for product in produit:

                game_element = self.wait_for_click("game", locator_type='name', timeout=10 * 9, raise_error=True)
                game_element.send_keys(product)

                self.wait_and_click("search-button")

                WebDriverWait(self.browser, timeout=60).until(
                    EC.text_to_be_present_in_element_attribute((By.ID, "results-jackpot_processing"), "style", "none"))

                sleep(1)

                table = self.browser.find_element(by=By.CSS_SELECTOR, value="table")
                html = table.get_attribute('outerHTML')
                import pandas as pd
                import numpy as np

                df = pd.read_html(html, index_col=False)
                df = pd.DataFrame(df[0])
                df = df.replace(np.nan, '')
                df = df.applymap(lambda x: str(x).replace(' ', ''))

                if "No data available in table" in df['Date Created'][0] and len(df) == 1:
                    print(f"le fichier ACAJOU {product} du {start_date} au {end_date} est vide")
                    continue

                for file in self.extraction_dest_path.glob("Account*csv"):
                    file.unlink()

                xpath = "/html/body/div[1]/div[1]/section[2]/div/div/div/div/div[3]/button"
                self.wait_and_click(xpath, locator_type="xpath")

                timer = 60 * 2
                while timer >= 0:
                    sleep(2)
                    timer -= 2
                    file = None
                    for file in self.extraction_dest_path.glob("Account*csv"):
                        file = file
                    if file is not None:
                        df = pd.read_csv(file, delimiter=",")

                        df['jour'] = str(str(start_date.strftime('%d/%m/%Y')))
                        df['mois'] = str(str(start_date.strftime('%m')))
                        df['annee'] = str(str(start_date.strftime('%Y')))
                        df['produit'] = product

                        newlist.append(df[["jour", "mois", "annee", "Access Channel", "Purchase Method", "Collection",
                                           "Gross Payout", "Status", "Disbursement", "produit"]])
                        break

                if timer < 0:
                    print("le fichier n'a pas pu etre telecharge")
                    continue

            if len(newlist)== 0:
                print(f"les données Mojabet du {start_date} sont vides")
                start_date += delta
                end_date += delta
                continue

            newlist = pd.concat(newlist, ignore_index=True)
            newlist = newlist.astype(str)
            filename = f"mojabet_ussd_transformed_{start_date}.csv"
            full_path = self.transformation_dest_path / filename
            newlist.to_csv(full_path, index=False, sep=';', encoding='utf8')

            start_date += delta
            end_date += delta

    def _process_download(self, start_date, end_date):
        pass


def run_mojabet_ussd():
    env_variables_list = ["ACAJOU_DIGITAL_LOGIN_USERNAME", "ACAJOU_DIGITAL_LOGIN_PASSWORD"]
    job = ExtractMojabetUSSD(env_variables_list)
    job.process_extraction()


if __name__ == "__main__":
    run_mojabet_ussd()
