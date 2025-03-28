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


class ExtractVirtualAmabelPivot(BaseScrapper):
    def __init__(self, env_variables_list):
        super().__init__('virtual_amabel_pivot', env_variables_list, 'logs/extract_virtual_amabel_pivot.log')
        self.file_path = None


    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
        browser.get(login_url)

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
        self.wait_and_send_keys(username_xpath,keys=username, locator_type="xpath")
        self.wait_and_send_keys(password_xpath,keys=password, locator_type="xpath")
        self.wait_and_send_keys(domain_xpath, keys=domain, locator_type="xpath")

        self.logger.info("Envoi du formulaire...")
        self.wait_and_click(submit_button_xpath, locator_type="xpath")

        self.logger.info("Vérification de la connexion...")
        try:
            verification_xpath = html_elements["verification_xpath"]
            self.wait_for_presence(verification_xpath)
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
        logger = self.logger
        # todo: extraire les xpath du code
        logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)
        # Constantes pour les XPATH
        XPATH_1 = "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[1]/p-button[1]/button"
        XPATH_2 = "/html/body/div/div/form/div/div/div[1]/calendar-custom-fc-component/div/p-button/button"
        XPATH_3 = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/div"
        XPATH_4 = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[2]/table/tbody/*/*/span[not(contains(@class,'p-disabled'))]"
        XPATH_5 = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[2]/div[1]/button"
        XPATH_6 = "/html/body/div/div/div[2]/p-calendar/span/div/div/div[1]/div[1]/button[1]"
        XPATH_7 = "/html/body/div[2]/div/div[4]/div[2]/p-button[1]/button"
        XPATH_8 = "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[1]/p-button[2]/button"
        XPATH_9 = "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/div/div[1]/div[2]/div[3]/p-button[1]/button"
        XPATH_10 = "/html/body/app-root/app-logged-in/div/div/div/app-pivot-table-component/p-dialog[2]/div/div/div[4]/p-button[1]/button"

        self.wait_and_click(XPATH_1, locator_type="xpath")
        self.wait_and_click(XPATH_2, locator_type="xpath")
        date_not_picked = True
        while date_not_picked:
            self.wait_for_presence(XPATH_3)
            month_year = browser.find_element(by=By.XPATH, value=XPATH_3).text
            current_month_year = datetime.strptime(month_year, "%B %Y")
            target_month_year = start_date.replace(day=1)
            target_month_year = datetime.strptime(target_month_year.strftime('%d/%m/%Y'), '%d/%m/%Y')

            if current_month_year == target_month_year:
                for tr in browser.find_elements(by=By.XPATH, value=XPATH_4):
                    if tr.text.strip() == start_date.strftime("%d"):
                        tr.click()
                        tr.click()
                        date_not_picked = False
                        break
            elif current_month_year < target_month_year:
                self.wait_and_click(XPATH_5, locator_type="xpath")
            else:
                self.wait_and_click(XPATH_6, locator_type="xpath")

        self.wait_and_click(XPATH_7, locator_type="xpath")
        self.wait_and_click(XPATH_8, locator_type="xpath")
        self.wait_and_click(XPATH_9, locator_type="xpath")
        self.wait_and_click(XPATH_10, locator_type="xpath")


    def process_extraction(self):
        self._delete_old_files()
        self._set_date()
        self._open_browser()
        self._connection_to_platform()
        self._download_files()

def run_virtual_amabel_pivot():
    env_variables_list = ["VIRTUAL_AMABEL_LOGIN_USERNAME", "VIRTUAL_AMABEL_LOGIN_PASSWORD","VIRTUAL_AMABEL_DOMAIN"]
    job = ExtractVirtualAmabelPivot(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_virtual_amabel_pivot()
