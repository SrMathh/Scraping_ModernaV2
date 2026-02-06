from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from utils.helpers import fill_field, click_element, check_text_on_page, log_message, click_image, change_iframe
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

                # Caminho correto da extensão no Docker
                extension_path = "/app/extension"
                if os.path.exists(extension_path):
                    options.add_argument(f"--load-extension={extension_path}")  # Carrega a extensão
                    print(f"Carregando extensão de: {extension_path}")
                else:
                    print(f"AVISO: Extensão não encontrada em {extension_path}")

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
                self.driver.get("chrome://extensions/shortcuts")  
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
            print("Aguardando extensão carregar...")
            time.sleep(3)
            
            pyautogui.hotkey('alt', 'v')  
            print("Extensão ativada com Alt + V")
            time.sleep(3)

            if not click_image('img/config.png', timeout=15):
                print("AVISO: Não foi possível clicar em config.png")
            time.sleep(2)

            if not click_image('img/predef.png', timeout=15):
                print("AVISO: Não foi possível clicar em predef.png")
            time.sleep(2)  

            if not click_image('img/staging.png', timeout=15):
                print("AVISO: Não foi possível clicar em staging.png")
            time.sleep(2)

            if not click_image('img/close.png', timeout=15):
                print("AVISO: Não foi possível clicar em close.png")

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
            if USE_PERFORM_ACTIONS == 'true':
                self.perform_actions()

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

    def ready_for_scraping(self):
        """
        Prepara o ambiente para scraping.
        """
        print("Login na estenção")
        email = os.getenv('EMAIL2')  
        password = os.getenv('PASSWORD2')  
        start_time = time.time() 
        timeout = 60  

        try:

            shadow_host = self.driver.find_element(By.ID, "voiston-container-script")

            shadow_root = shadow_host.shadow_root

            shadow_content = shadow_root.find_element(By.ID, "voiston-content-base")

            entrar_link = WebDriverWait(shadow_content, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > a"))
            )

            entrar_link.click()

            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))

            main_window = self.driver.current_window_handle

            all_windows = self.driver.window_handles

            for window in all_windows:
                if window != main_window:
                    self.driver.switch_to.window(window)
                    break
            
            fill_field(self.driver, 'mat-input-0', 'id', email, 'Preenchimento de Email')
            fill_field(self.driver, 'mat-input-1', 'id', password, 'Preenchimento de Password')
            click_element(self.driver, "//button[contains(., 'Entrar')]", 'xpath', 'Click entrar')
            while time.time() - start_time < timeout:
                if not check_text_on_page(self.driver, 'Aguarde enquanto processamos sua requisição...', timeout=timeout):    
                    log_message("Log-in OK. Continuando ...")
                    break
                time.sleep(1)
                log_message("Aguarde enquanto processamos sua requisição...")
            else:
                msg = "Tempo limite excedido ao aguardar o login na extensão."
                logger.error(msg)
                self.errors.append(msg)
                sys.exit(1)
            print(" Login realizado com sucesso na extensão!")
            self.driver.switch_to.window(main_window)

        except Exception as e:
                msg = f"Erro durante log in na extensão: {e}"
                logger.exception(msg, exc_info=False)
                self.errors.append(msg)

        finally:
            execution_time = time.time() - start_time
            log_message(f"Ação Login concluída em {execution_time:.2f} segundos.")


    def fechar_navegador(self):
        """
        Encerra a instância do WebDriver.
        """
        if self.driver:
            self.driver.quit()
            print("Navegador fechado.")