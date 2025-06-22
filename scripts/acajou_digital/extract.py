from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from base.web_scrapper import BaseScrapper



class ExtractAcajouDigital(BaseScrapper):
    def __init__(self, env_variables_list):
        chrome_options_arguments = [
            "--unsafely-treat-insecure-origin-as-secure=http://115.110.148.83/bwinnersmis/Administration/"
        ]
        super().__init__('acajou_digital', env_variables_list, 'logs/extract_acajou_digital.log', chrome_options_arguments=chrome_options_arguments)

    def _connection_to_platform(self):
        self.logger.info("Connexion au site...")
        browser = self.browser
        login_url = self.config['urls']['login']
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
            self.wait_for_presence(verification_xpath, raise_error=True, timeout=10*9)
            self.logger.info("Connexion à la plateforme réussie.")

        except:
            self.logger.error("Connexion à la plateforme n'a pas pu être établie.")
            browser.quit()

        pass

    def _download_files(self):
        browser = self.browser

        self.logger.info("Chargement de la page des rapports...")
        reports_url = self.config['urls']['report']
        browser.get(reports_url)

        self.logger.info("Remplissage des champs de date...")
        game_element = self.wait_for_click("game", locator_type='name', timeout=10*9, raise_error=True)
        game_element.send_keys("DIGITAIN")

        self._process_multiple_files()

    def _process_download(self, start_date=None, end_date=None):
        html_elements = self.config['html_elements']
        date_element_name = html_elements["date_element_name"]
        step_x1_element_id = html_elements["step_x1_element_id"]
        step_x2_element_xpath = html_elements["step_x2_element_xpath"]

        formatted_date = f"{start_date.strftime('%Y/%m/%d')} 00:00:00 - {end_date.strftime('%Y/%m/%d')} 23:59:59"

        date_element = self.wait_for_click(date_element_name, locator_type='name', timeout=15, raise_error=True)
        date_element.clear()
        date_element.send_keys(formatted_date)
        date_element.send_keys(Keys.ENTER)
        WebDriverWait(self.browser,timeout=15).until( EC.text_to_be_present_in_element_attribute(( By.ID, step_x1_element_id),"style", "none"))

        self.logger.info("Soumission du formulaire...")
        self.wait_and_click(step_x2_element_xpath, locator_type='xpath', timeout=60)


def run_acajou_digital():
    env_variables_list = ["ACAJOU_DIGITAL_LOGIN_USERNAME", "ACAJOU_DIGITAL_LOGIN_PASSWORD"]
    job = ExtractAcajouDigital(env_variables_list)
    job.process_extraction()

if __name__ == "__main__":
    run_acajou_digital()
