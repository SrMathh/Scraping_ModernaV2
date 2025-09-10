from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
from datetime import datetime, date
from typing import Optional, Union
import datetime

# Gera o nome do arquivo de log
log_filename = "testeAutomatico.log"



def log_message(message):
    """
    Registra uma mensagem no log e imprime no console sem erros de codificação.
    """

    # Força a saída no console para UTF-8
    try:
        print(message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    except UnicodeEncodeError:
        print(message.encode("utf-8", "ignore").decode("utf-8"))  # Se der erro, ignora caracteres inválidos

    # Salvar no arquivo de log com UTF-8 para evitar erros ao ler depois
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def fill_field(driver, identifier, identifier_type, value, action_name="", timeout=30):
    """
    Localiza um campo de input e preenche com um valor.

    Parâmetros:
    - driver (WebDriver): Instância do Selenium WebDriver.
    - identifier (str): Identificador do campo (exemplo: ID ou XPath).
    - identifier_type (str): Tipo do identificador ('id', 'xpath', 'class_name', etc.).
    - value (str): Texto a ser inserido no campo.
    - action_name (str, opcional): Nome da ação para fins de log.
    - timeout (int, opcional): Tempo máximo de espera pelo elemento (padrão: 20 segundos).

    Retorno:
    - Nenhum. Apenas preenche o campo de input.
    """

    start_time = time.time()  # Marca o tempo de início da execução

    try:

        # Verifica se o valor passado é uma string
        if not isinstance(value, str):
            raise ValueError(f" Esperado um valor de texto (string), mas recebeu {type(value).__name__}")

        # Dicionário para mapear os tipos de identificadores do Selenium
        by_type = {
            'id': By.ID,
            'xpath': By.XPATH,
            'class_name': By.CLASS_NAME,
            'css_selector': By.CSS_SELECTOR,
            'link_text': By.LINK_TEXT,
        }

        # Verifica se o tipo de identificador fornecido é válido
        if identifier_type not in by_type:
            raise ValueError(f" Tipo de identificador '{identifier_type}' não é suportado.")

        wait = WebDriverWait(driver, timeout)  # Define o tempo máximo de espera

        # Aguarda até que o campo esteja presente na página
        element = wait.until(EC.presence_of_element_located((by_type[identifier_type], identifier)))

        # Aguarda até que o campo esteja clicável
        wait.until(EC.element_to_be_clickable((by_type[identifier_type], identifier)))

        # Limpa o campo antes de inserir um novo valor
        element.clear()
        time.sleep(1)  # Pequeno atraso para garantir que o campo esteja pronto

        # Insere o texto no campo de input
        element.send_keys(value)

    except TimeoutException:
        # Se o tempo limite for atingido e o campo não for encontrado
        print(f" Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado após {timeout} segundos.")

    except NoSuchElementException:
        # Se o campo não existir na página
        print(f" Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado.")

    except ValueError as ve:
        # Se o valor passado não for uma string ou o identificador for inválido
        print(f" Erro de valor: {ve}")

    except Exception as e:
        # Captura qualquer erro inesperado
        print(f" Ocorreu um erro inesperado: {e}")

    finally:
        # Calcula e exibe o tempo total da execução
        execution_time = time.time() - start_time
        time.sleep(1)
        print(f" Ação '{action_name}' concluída em {execution_time:.2f} segundos.")


def click_element(driver, identifier, identifier_type, action_name="", timeout=20):
    """
    Localiza um elemento na página e realiza um clique, baseado no tipo de identificador.

    Parâmetros:
    - driver (WebDriver): Instância do Selenium WebDriver.
    - identifier (str): O valor do identificador do elemento (ex: ID ou XPath).
    - identifier_type (str): O tipo do identificador ('id', 'xpath', 'class_name', etc.).
    - action_name (str, opcional): Nome da ação para log.
    - timeout (int, opcional): Tempo máximo de espera pelo elemento (padrão: 20 segundos).

    Retorno:
    - Nenhum. Apenas realiza o clique no elemento.
    """

    start_time = time.time()  # Marca o início da execução

    try:
        wait = WebDriverWait(driver, timeout)  # Configura tempo máximo de espera para encontrar o elemento

        # Dicionário para mapear os tipos de identificadores do Selenium
        by_type = {
            'id': By.ID,
            'xpath': By.XPATH,
            'class_name': By.CLASS_NAME,
            'css_selector': By.CSS_SELECTOR,
            'link_text': By.LINK_TEXT,
            'name': By.NAME,
        }

        # Verifica se o tipo de identificador fornecido é válido
        if identifier_type not in by_type:
            raise ValueError(f"Tipo de identificador '{identifier_type}' não é suportado.")

        # Aguarda até que o elemento esteja clicável na página
        element = wait.until(EC.element_to_be_clickable((by_type[identifier_type], identifier)))

        time.sleep(1)  # Pequeno delay para garantir que o elemento esteja pronto para interação
        element.click()  # Realiza o clique no elemento

    except TimeoutException:
        # Se o tempo limite for atingido e o elemento não for encontrado
        print(f" Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado após {timeout} segundos.")

    except NoSuchElementException:
        # Se o elemento não existir na página
        print(f" Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado.")

    except Exception as e:
        # Captura qualquer erro inesperado
        print(f" Erro inesperado: {e}")

    finally:
        # Calcula e exibe o tempo total da execução
        execution_time = time.time() - start_time
        time.sleep(1)
        print(f" Ação '{action_name}' concluída em {execution_time:.2f} segundos.")

def check_text_on_page(driver, text, timeout, check_interval=5):
    """
    Verifica continuamente se um texto específico ainda está presente na página.

    Parâmetros:
    - driver (WebDriver): Instância do Selenium WebDriver.
    - text (str): Texto a ser verificado na página.
    - timeout (int): Tempo máximo para aguardar a remoção do texto (em segundos).
    - check_interval (int, opcional): Intervalo entre verificações (padrão: 5 segundos).

    Retorno:
    - True: Se o texto desaparecer antes do tempo limite.
    - False: Se o texto ainda estiver presente após o tempo limite.
    """

    start_time = time.time()  # Marca o tempo de início da verificação
    print(f" Iniciando verificação do texto: '{text}'")

    while True:
        try:
            # Busca elementos que contêm o texto desejado
            element_present = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")

            # Se o texto não estiver mais na página, retorna True
            if not element_present:
                print(f" O texto '{text}' desapareceu da página.")
                return False

        except Exception as e:
            print(f" Erro ao verificar '{text}': {e}")
            return False

        # Se o tempo limite for atingido, retorna False
        if time.time() - start_time > timeout:
            print(f" Tempo limite atingido! O texto '{text}' ainda está na página.")
            return True

        # Aguarda o intervalo definido antes de verificar novamente
        time.sleep(check_interval)

by_type = {
                'id': By.ID,
                'xpath': By.XPATH,
                'class_name': By.CLASS_NAME,
                'css_selector': By.CSS_SELECTOR,
                'link_text': By.LINK_TEXT,
                'name': By.NAME,
            }
def action_in_frame(driver, action, identifier, identifier_type, value=None, action_name="", timeout=30, iframe=None):
    start_time = time.time()  # Marca o tempo de início da execução

    try:

        # Validar se o tipo de identificador é válido
        if identifier_type not in by_type:
            raise ValueError(f"Tipo de identificador '{identifier_type}' não é suportado.")
        
        # Criando o WebDriverWait apenas uma vez
        wait = WebDriverWait(driver, timeout)

        # Ação: Preencher campo (fill_field)
        if action == "fill_field":
            # Espera até que o elemento esteja presente no iframe
            element = wait.until(EC.presence_of_element_located((by_type[identifier_type], identifier)))
            element.clear()
            time.sleep(1)
            element.send_keys(value)

        # Ação: Clicar no elemento (click_element)
        elif action == "click_element":
            # Espera até que o elemento esteja clicável dentro do iframe
            element = wait.until(EC.element_to_be_clickable((by_type[identifier_type], identifier)))
            element.click()

        # Ação: Verificar texto na página (check_text_on_page)
        elif action == "check_text_on_page":
            # Espera até que o texto esteja presente no iframe
            element_present = wait.until(EC.presence_of_element_located((by_type[identifier_type], identifier)))
            if value not in element_present.text:
                print(f"O texto '{value}' não foi encontrado no iframe.")
                return False

        # Ação: Esperar elemento (wait)
        elif action == "wait":
            wait.until(EC.presence_of_element_located((by_type[identifier_type], identifier)))
            time.sleep(1)

        else:
            raise ValueError(f"Ação '{action}' não suportada.")

    except TimeoutException:
        print(f"Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado após {timeout} segundos.")
    except NoSuchElementException:
        print(f"Erro: O elemento com {identifier_type} '{identifier}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        execution_time = time.time() - start_time
        print(f"Ação '{action_name}' concluída em {execution_time:.2f} segundos.")

def change_iframe(driver):
    """
    Altera o contexto do driver para um iframe específico.

    Parâmetros:
    - driver (WebDriver): Instância do Selenium WebDriver.
    - iframe (str): O identificador do iframe (ID ou XPath).

    Retorno:
    - Nenhum. Apenas altera o contexto do driver.
    """
    try:
        driver.switch_to.default_content()                   
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frmSuperMain"))
        )
        driver.switch_to.frame(iframe)
        print("Iframe encontrado e mudado com sucesso.")
    except Exception as e:
        print(f"Erro na mudança de iframe: {e}")
        return
    

def parse_date_safe(value: Optional[Union[str, datetime.datetime, datetime.date]]) -> Optional[datetime.date]:
    """
    Converte valor para datetime.date com segurança e vários formatos.

    Args:
        value: string no formato dd/mm/yyyy ou yyyy-mm-dd ou datetime ou date ou None

    Returns:
        datetime.date ou None se não conseguir interpretar
    """
    if value is None:
        return None

    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return value

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, str):
        value = value.strip()
        formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formatos:
            try:
                return datetime.datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    # Se chegou aqui, não conseguiu converter
    return None
