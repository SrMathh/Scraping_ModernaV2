from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.helpers import fill_field, click_element, check_text_on_page, log_message
import pyautogui
from dotenv import load_dotenv
import sys
import os
import time
import tempfile

import logging
logger = logging.getLogger(__name__)

load_dotenv(override=True)

class Browser:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.errors: list[str] = []

    def open_browser(self):
            """
            Inicializa o navegador Google Chrome com configurações específicas e carrega a extensão.

            Retorno:
            - Nenhum. Apenas inicia o navegador e acessa o site desejado.
            """
            try:
                options = webdriver.ChromeOptions()

                profile_dir = tempfile.mkdtemp(prefix="chrome_profile_", dir="/tmp")
                options.add_argument(f"--user-data-dir={profile_dir}")

                extension_dir = os.path.join(os.getcwd(), "extension") 

                options.add_argument(f"--load-extension={extension_dir}")  # Carrega a extensão

                # Define opções para melhorar a execução do Selenium
                options.add_argument("--start-maximized")  
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)

                service = Service(ChromeDriverManager().install())

                self.driver = webdriver.Chrome(service=service, options=options)
                print("Navegador inicializado.")

                self.driver.implicitly_wait(2)
                self.wait = WebDriverWait(self.driver, 10)
                #self.driver.get("chrome://extensions/shortcuts")  
                #time.sleep(2)  
                #try:
                #    shadow_host_1 = self.driver.find_element(By.XPATH, "/html/body/extensions-manager")
                #    shadow_root_1 = shadow_host_1.shadow_root  
                #    shadow_host_2 = shadow_root_1.find_element(By.ID, "container")
                #    shadow_root_2 = shadow_host_2  
                #    shadow_host_3 = shadow_root_2.find_element(By.ID, "viewManager")
                #    shadow_root_3 = shadow_host_3  
                #    shadow_host_4 = shadow_root_3.find_element(By.CSS_SELECTOR, "#viewManager > extensions-keyboard-shortcuts")
                #    shadow_root_4 = shadow_host_4.shadow_root  
                #    shadow_host_5 = shadow_root_4.find_element(By.ID, "container")
                #    shadow_root_5 = shadow_host_5  
                #    shadow_host_6 = shadow_root_5.find_element(By.CSS_SELECTOR, "#container > div > div.card-controls")
                #    shadow_root_6 = shadow_host_6 
                #    shadow_host_7 = shadow_root_6.find_element(By.CSS_SELECTOR, "#container > div > div.card-controls > div > cr-shortcut-input")
                #    shadow_root_7 = shadow_host_7.shadow_root  
                #    shadow_host_8 = shadow_root_7.find_element(By.ID, "main")
                #    shadow_root_8 = shadow_host_8  
                #    shadow_host_9 = shadow_root_8.find_element(By.ID, "input")
                #    shadow_root_9 = shadow_host_9  
                #    shadow_host_10 = shadow_root_9.find_element(By.ID, "edit")
                #    shadow_root_10 = shadow_host_10  
                #    shadow_root_10.click()
                #    actions = ActionChains(self.driver)
                #    actions.key_down(Keys.ALT).send_keys('v').key_up(Keys.ALT).perform()
                #except Exception as e:
                #    msg = f"Erro durante a inicialização do navegador: {e}"
                #    logger.exception(msg, exc_info=False)
                #    self.errors.append(msg)

                link = os.getenv('LINK1')
                if not link:
                    print("LINK1 não configurado no arquivo .env")
                    return

                print(f"Abrindo o site: {link}")
                self.driver.get(link)

                print("Site aberto com sucesso!")
            except Exception as e:
                    msg = f"Erro durante a inicialização do navegador: {e}"
                    logger.exception(msg, exc_info=False)
                    self.errors.append(msg)

    def perform_actions(self):
        try:
            pyautogui.hotkey('alt', 'v')  
            print("Extensão ativada com Alt + V")
            time.sleep(2)

            self.click_image('img/config.png')
            time.sleep(2)

            self.click_image('img/predef.png')
            time.sleep(2)  

            self.click_image('img/staging.png')
            time.sleep(2)

            self.click_image('img/close.png')

        except Exception as e:
                msg = f"Erro no perform_actions {e}"
                logger.exception(msg, exc_info=False)
                self.errors.append(msg)

    def login(self):
        """
        Realiza o login na aplicação.
        """
        email = os.getenv('EMAIL1')
        password = os.getenv('PASSWORD1')
        start_time = time.time()  
        USE_PERFORM_ACTIONS = os.getenv('USE_PERFORM_ACTIONS', 'false')
        
        try:
            #if USE_PERFORM_ACTIONS == 'true':
            #    self.perform_actions()

            fill_field(self.driver, 'USERNAME', 'id', email, 'Preenchimento de Email')
            fill_field(self.driver, 'PASSWORD', 'id', password, 'Preenchimento de Password')
            click_element(self.driver,'btnEntrar', 'id', 'Click Login')
            time.sleep(2)
        
        except Exception as e:
                msg = f"Erro durante log in: {e}"
                logger.exception(msg, exc_info=False)
                self.errors.append(msg)

        finally:
            execution_time = time.time() - start_time
            print(f"Tempo de execução: {execution_time:.2f} segundos")

    def fechar_navegador(self):
        """
        Encerra a instância do WebDriver.
        """
        if self.driver:
            self.driver.quit()
            print("Navegador fechado.")