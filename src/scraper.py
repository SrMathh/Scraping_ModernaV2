import time
import database
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv(override=True)

class Scraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.url_base = os.getenv('LINK_BASE')
        self.numero_base = int(os.getenv('ID_BASE'))

    def validate_patient(self, id_atual):
        """
        Função principal para validar os dados do paciente.
        """
        try:
            nome_paciente_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "txtMODERNA_PESSOAFISICA"))
            )
            idade_div = self.wait.until(
                EC.presence_of_element_located((By.ID, "PEP2200000_IDADE"))
            )
            nome_paciente = nome_paciente_input.get_attribute('value')
            idade_texto = idade_div.text
            if not nome_paciente and idade_texto.strip() == "0m 0d":
                print(f"ID {id_atual}: Paciente em branco (Nome vazio e Idade 0m 0d).")
                return False, None
            else:
                print(f"ID {id_atual}: Paciente válido encontrado - {nome_paciente}.")
                return True, nome_paciente
        except TimeoutException:
            print(f"ID {id_atual}: Página inválida ou erro de carregamento (Timeout).")
            return False, None
        except Exception as e:
            logger.error(f"Erro inesperado ao validar página para ID {id_atual}: {e}")
            database.registrar_paciente(id_atual, 'erro_geral')
            return False, None

    def _executar_fase(self, direcao, id_inicial):
        """
        Executa uma fase de scraping a partir de um ID inicial específico.
        """
        brancos_consecutivos = 0
        id_atual = id_inicial
        
        incremento = 1 if direcao == 'para_cima' else -1

        print(f"--- Iniciando Fase '{direcao.upper()}' a partir do ID: {id_atual} ---")

        while brancos_consecutivos < 100:
            if database.verificar_id_existente(id_atual):
                id_atual += incremento
                continue

            url_alvo = f"{self.url_base}{id_atual}"
            print(f"Navegando para: {url_alvo}")
            self.driver.get(url_alvo)
            
            eh_valido, nome_paciente = self.validate_patient(id_atual)

            if eh_valido:
                brancos_consecutivos = 0
                print(f">>> Sucesso! Paciente '{nome_paciente}'. Registrando e extraindo dados...")
                self.scraping_extensao()
                database.registrar_paciente(id_atual, 'sucesso', nome_paciente)
            else:
                brancos_consecutivos += 1
                database.registrar_paciente(id_atual, 'nao_encontrado')
                print(f"Brancos consecutivos: {brancos_consecutivos}/100")
            
            id_atual += incremento
        
        print(f"--- Fase '{direcao.upper()}' concluída: 100 IDs em branco consecutivos encontrados. ---")

    def iniciar_scraping(self):
        """
        Orquestra o scraping, determinando os pontos de partida corretos para
        cada fase com base nos dados já existentes no banco.
        """
        print(f"ID Base configurado: {self.numero_base}")

        maior_id = database.obter_maior_id_verificado()
        id_inicial_para_cima = self.numero_base
        if maior_id and maior_id >= self.numero_base:
            id_inicial_para_cima = maior_id + 1
            print(f"Retomando varredura 'para cima' do último ID salvo: {maior_id}")
        
        self._executar_fase('para_cima', id_inicial_para_cima)

        menor_id = database.obter_menor_id_verificado(self.numero_base)
        id_inicial_para_baixo = self.numero_base - 1
        if menor_id:
            id_inicial_para_baixo = menor_id - 1
            print(f"Retomando varredura 'para baixo' do último ID salvo: {menor_id}")
            
        self._executar_fase('para_baixo', id_inicial_para_baixo)

        print("Scraping concluído.")

    def scraping_extensao(self):
        print(f"   - Iniciando scraping de extensão.")

        try:
            time.sleep(1)
            # Lógica para scraping de extensão
            pass

        except Exception as e:
            print(f"   - ERRO GERAL ao tentar extrair dados de extensão: {e}")
