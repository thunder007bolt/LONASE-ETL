### system ###
import glob, os
from datetime import datetime
import pandas as pd
### base ###
from base.logger import Logger
from base.web_scrapper import BaseScrapper
### selenium ###
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
### utils ###
from utils.config_utils import get_config, get_secret
from utils.date_utils import get_yesterday_date, sleep
from utils.other_utils import move_file, loading


class ExtractVirtualAmabel(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('virtual_amabel', env_variables_list, 'logs/extract_virtual_amabel.log')
        self.file_path = None


    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        login_url = self.config['urls']['login']
        self.browser.get(login_url)

        html_elements = self.config['html_elements']
        secret_config = self.secret_config
        username_xpath= html_elements["username_element_xpath"]
        password_xpath= html_elements["password_element_xpath"]
        domain_xpath= html_elements["domain_element_xpath"]
        submit_button_xpath= html_elements["login_submit_button_element_xpath"]
        username = secret_config["VIRTUAL_AMABEL_LOGIN_USERNAME"]
        password = secret_config["VIRTUAL_AMABEL_LOGIN_PASSWORD"]
        domain = secret_config["VIRTUAL_AMABEL_DOMAIN"]

        self.logger.info("Saisie des identifiants...")
        sleep(5)
        # reessayer plusieurs fois
        attempts = 6
        for attempt in range(attempts):
            self.logger.info(f"Tentative {attempt}")
            try:
                browser = self.browser
                username = 'sadio.fall'

                WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[3]/div/input"))).send_keys(
                    username)

                password = "Passer1234!"
                WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[4]/div/p-password/div/input"))).send_keys(
                    password)

                domain = "LONASE-CG"
                WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[2]/div/input"))).send_keys(
                    domain)

                WebDriverWait(browser, timeout=10 * 9).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         "/html/body/app-root/ng-component/div/div[1]/div/div[2]/div[1]/form/div/div[5]/div/button"))).click()

                #self.wait_and_send_keys2(username_xpath,keys=username, locator_type="xpath", timeout=60*2, raise_error=True)
                #self.wait_and_send_keys2(password_xpath,keys=password, locator_type="xpath", timeout=60*2, raise_error=True)
                #self.wait_and_send_keys2(domain_xpath, keys=domain, locator_type="xpath", timeout=60*2, raise_error=True)
                break
            except Exception as e:
                self.browser.get(login_url)
                if attempt == attempts:
                    raise e

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type="xpath")

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            self.browser.quit()

        sleep(10)
        pass

    def _download_files(self):
        self._process_multiple_files()

    def _process_download(self, start_date, end_date):
        browser = self.browser
        logger = self.logger
        # todo: extraire les xpath du code
        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)
        # Constantes pour les XPATH
        CALENDAR_BUTTON_XPATH = "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[1]/div[1]/form/calendar-custom-fc-component/div/p-button/button"
        MONTH_YEAR_XPATH = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div"
        DATE_CELLS_XPATH = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[2]/table/tbody/*/*/span[not(contains(@class,'p-disabled'))]"
        NEXT_MONTH_XPATH = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[2]/div[1]/button"
        PREV_MONTH_XPATH = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/button[1]"
        CONFIRM_DATE_XPATH = "/html/body/div/div/div[3]/div/p-button[1]/button"
        SEARCH_BUTTON_XPATH = "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[1]/div[1]/form/p-button[1]/button"
        EXPAND_TABLE_XPATH_1 = "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[2]/td[1]/div/p-treetabletoggler/button"
        EXPAND_TABLE_XPATH_2 = "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[3]/td[1]/div/p-treetabletoggler/button"
        EXPAND_TABLE_XPATH_3 = "/html/body/app-root/app-logged-in/div/div/div/app-turnover-component/div/div[2]/div/p-treetable/div/div/table/tbody/tr[4]/td[1]/div/p-treetabletoggler/button"
        DATA_ROWS_XPATH = "//tr[@class='UNIT ng-star-inserted']"
        # Fonction pour sélectionner une date dans le calendrier
        excl_list = []
        # Fonction principale
        # Ouvre le calendrier et sélectionne la date
        self.wait_and_click(CALENDAR_BUTTON_XPATH, locator_type="xpath")
        date_not_picked = True
        while date_not_picked:
            self.wait_for_presence(MONTH_YEAR_XPATH)
            month_year = browser.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div").text
            current_month_year = datetime.strptime(month_year, "%B %Y")
            target_month_year = start_date.replace(day=1)
            target_month_year = datetime.strptime(target_month_year.strftime('%d/%m/%Y'), '%d/%m/%Y')

            if current_month_year == target_month_year:
                for tr in browser.find_elements(by=By.XPATH, value=DATE_CELLS_XPATH):
                    if tr.text.strip() == start_date.strftime("%#d"):
                        tr.click()
                        tr.click()
                        date_not_picked = False
                        break
            elif current_month_year < target_month_year:
                self.wait_and_click(NEXT_MONTH_XPATH, locator_type="xpath")
            else:
                self.wait_and_click(PREV_MONTH_XPATH, locator_type="xpath")

        self.wait_and_click(CONFIRM_DATE_XPATH, locator_type="xpath")
        self.wait_and_click(SEARCH_BUTTON_XPATH, locator_type="xpath")

        # Expansion de la table
        self.wait_and_click(EXPAND_TABLE_XPATH_1, locator_type="xpath")
        try:
            self.wait_and_click(EXPAND_TABLE_XPATH_3, locator_type="xpath")
        except :
            pass  # Ignorer si l'élément n'est pas présent
        self.wait_and_click(EXPAND_TABLE_XPATH_2, locator_type="xpath")

        # Attend que les données soient visibles
        self.wait_for_presence(DATA_ROWS_XPATH, timeout=60)
        # WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, DATA_ROWS_XPATH)))

        # Récupération des données
        data = []
        for row in browser.find_elements(by=By.XPATH, value=DATA_ROWS_XPATH):
            # cells = row.find_elements(by=By.TAG_NAME, value="td")
            # data.append([cells[0].text, cells[4].text, cells[5].text, cells[7].text])
            temp = str(row.text)
            temp = temp.strip().replace('\u202f',' ')
            temp = temp.splitlines()
            data.append(temp)

        # Création et nettoyage du DataFrame
        df = pd.DataFrame(data)
        df = df.iloc[:,[0,4,5,7]]
        df[5] = [str(i).split(' ')[-1] for i in df[5]]
        df.columns = ["AgentFirstName","TotalStake","TotalTickets","TotalWonAmount"]

        df["TotalTickets"] = df["TotalTickets"].str.split().str[-1]  # Extrait la dernière partie
        df = df.replace({',': '', '\u202f': ' ', '_': '0', '-': '0'}, regex=True)
        df[["TotalStake", "TotalWonAmount", "TotalTickets"]] = df[["TotalStake", "TotalWonAmount", "TotalTickets"]].replace(r'\.', ',', regex=True)
        df["date"] = start_date.strftime('%d/%m/%Y')

        # Ajout à la liste et sauvegarde
        excl_list.append(df[["AgentFirstName", "TotalStake", "TotalTickets", "TotalWonAmount", "date"]])
        output_file = os.path.join(self.config["download_path"], f"virtuelAmabel{start_date.strftime('%d-%m-%Y')}.csv") #todo: changer le nom du fichier

        if os.path.exists(output_file):
            os.remove(output_file)

        df.to_csv(output_file, sep=';', index=False)
        logger.info(f"Le fichier virtuel Amabel du {start_date} a bien été téléchargé")


    def process_extraction(self):
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()

def run_virtual_amabel():
    env_variables_list = ["VIRTUAL_AMABEL_LOGIN_USERNAME", "VIRTUAL_AMABEL_LOGIN_PASSWORD","VIRTUAL_AMABEL_DOMAIN"]
    job = ExtractVirtualAmabel(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_virtual_amabel()
