import time
import database
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

    def configurar_filtros_totais(self):
        try:
            # 1. Localiza todos os containers de filtros Chosen na página
            filtros = self.driver.find_elements(By.CLASS_NAME, "chosen-container")

            for filtro in filtros:
                # Verifica o texto atual do filtro
                texto_atual = filtro.find_element(By.CSS_SELECTOR, "a.chosen-single span").text

                if "(Todos)" not in texto_atual:
                    print(f"Configurando filtro para '(Todos)'...")
                    filtro.click()
                    time.sleep(0.5)
                    opcao_todos = filtro.find_element(By.XPATH, ".//li[contains(text(), '(Todos)')]")
                    opcao_todos.click()
                    time.sleep(0.5)
                else:
                    print("Filtro já está configurado como '(Todos)'.")

        except Exception as e:
            print(f"Erro ao configurar filtros: {e}")

    def _executar_fase(self, direcao, id_inicial, id_limite):
        """
        Executa uma fase de scraping a partir de um ID inicial específico.
        Continua até atingir o ID limite, pulando IDs em branco.
        """
        id_atual = id_inicial
        incremento = 1 if direcao == 'para_cima' else -1

        print(f"--- Iniciando Fase '{direcao.upper()}' a partir do ID: {id_atual} ---")

        while True:
            # Verifica se atingiu o limite
            if direcao == 'para_cima' and id_atual > id_limite:
                break
            if direcao == 'para_baixo' and id_atual < id_limite:
                break

            # Pula IDs já verificados
            if database.verificar_id_existente(id_atual):
                id_atual += incremento
                continue

            url_alvo = f"{self.url_base}{id_atual}"
            print(f"Navegando para: {url_alvo}")
            self.driver.get(url_alvo)
            
            eh_valido, nome_paciente = self.validate_patient(id_atual)

            if eh_valido:
                print(f">>> Sucesso! Paciente '{nome_paciente}'. Registrando e extraindo dados...")
                self.configurar_filtros_totais()
                self.scraping_extension(str(id_atual), nome_paciente, None, None)
                database.registrar_paciente(id_atual, 'sucesso', nome_paciente)
            else:
                database.registrar_paciente(id_atual, 'nao_encontrado')
                print(f"ID {id_atual}: Em branco, pulando...")
            
            id_atual += incremento
        
        print(f"--- Fase '{direcao.upper()}' concluída: ID limite {id_limite} atingido. ---")

    def iniciar_scraping(self):
        """
        Orquestra o scraping em duas fases:
        1ª Fase: Começa do ID base e desce (decrementa) até o ID mínimo
        2ª Fase: Volta ao ID base e sobe (incrementa) até o ID máximo
        """
        print(f"ID Base configurado: {self.numero_base}")
        
        # Define limites amplos para fazer varredura completa
        id_minimo = int(os.getenv('ID_MINIMO', '1'))  # ID mínimo a verificar
        id_maximo = int(os.getenv('ID_MAXIMO', '999999'))  # ID máximo a verificar

        # Fase 1: Descer a partir do ID base
        menor_id = database.obter_menor_id_verificado(self.numero_base)
        id_inicial_para_baixo = self.numero_base - 1
        if menor_id and menor_id < self.numero_base:
            id_inicial_para_baixo = menor_id - 1
            print(f"Retomando varredura 'para baixo' do último ID salvo: {menor_id}")
        else:
            print(f"Iniciando varredura 'para baixo' a partir do ID base: {self.numero_base}")
            
        self._executar_fase('para_baixo', id_inicial_para_baixo, id_minimo)

        # Fase 2: Subir a partir do ID base
        maior_id = database.obter_maior_id_verificado()
        id_inicial_para_cima = self.numero_base
        if maior_id and maior_id >= self.numero_base:
            id_inicial_para_cima = maior_id + 1
            print(f"Retomando varredura 'para cima' do último ID salvo: {maior_id}")
        else:
            print(f"Iniciando varredura 'para cima' a partir do ID base: {self.numero_base}")
        
        self._executar_fase('para_cima', id_inicial_para_cima, id_maximo)

        print("Scraping concluído.")

    def scraping_extension(self, patient_id: str, name: str, exam_date: date | None, patient_dob: date | None):
        """
        Função para realizar scraping completo utilizando a extensão.
        """
        try:
            # Voltar ao conteúdo principal
            self.driver.switch_to.default_content()
            shadow_host = self.driver.find_element(By.ID, "voiston-container-script")
            # Acessa o Shadow Root do Shadow Host
            shadow_root = shadow_host.shadow_root
            # Localiza o conteúdo dentro do Shadow Root
            shadow_content = shadow_root.find_element(By.ID, "voiston-content-base")
            
            try:
                exist_paciente = WebDriverWait(shadow_content, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.gWsYQM.Scrollable.MuiBox-root > div > div.sc-bczRLJ.fEJldt.MuiBox-root > span"))
                )
                text = exist_paciente.text.strip()

                if text == "Paciente não encontrado no Vöiston":
                    print(f"Paciente {patient_id} não encontrado na extensão.")
                    button = WebDriverWait(shadow_content, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button"))
                    )
                    print("Iniciando envio de paciente para a Vöiston")
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                    self.click_image("img/ok.png")  # Clica na imagem de confirmação
                    self.import_prontuaros_exames(patient_id, name, exam_date, patient_dob)  # Chama a função para importar exames
                    return
            except Exception:
                print(f"Paciente ja encontrado no Vöiston")

            try:
                name_paciente = WebDriverWait(shadow_content, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.gWsYQM.Scrollable.MuiBox-root > div > div:nth-child(1) > div > div > button"))
                )
                name_paciente.text.strip()
                print(f"Paciente {patient_id} já existe na extensão. Checando exames para importação.")
                self.import_prontuaros_exames(patient_id, name, exam_date, patient_dob)  # Chama a função para importar exames
            except Exception as e:
                logging.exception(f"Erro ao verificar se o paciente existe: {e}")

        except Exception as e:
            self.add_error(f"Erro ao realizar scraping da extensão: {e}", patient_id)

    def import_prontuaros_exames(self, patient_id: str, name: str, exam_date: date | None, patient_dob: date | None):
        try:
            shadow_host = self.driver.find_element(By.ID, "voiston-container-script")
            shadow_root = shadow_host.shadow_root
            shadow_content = shadow_root.find_element(By.ID, "voiston-content-base")

            try:
                time.sleep(2)
                timeout = 15
                interval = 2
                start_time = time.time()

                while time.time() - start_time < timeout:

                    try:
                        check_exames = WebDriverWait(shadow_content, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.gWsYQM.Scrollable.MuiBox-root > div > div.sc-bczRLJ.kaYPDH.MuiBox-root > div.sc-bczRLJ.cRjjBs.MuiBox-root > div > button > p"))
                        )
                        print("Elemento encontrado")
                        break
                    except Exception:
                        print("Elemento não encontrado, tentando novamente...")
                        time.sleep(interval)

                else:
                    check_exames_voiston = WebDriverWait(shadow_content, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.gWsYQM.Scrollable.MuiBox-root > div > div.sc-bczRLJ.kaYPDH.MuiBox-root > div.sc-bczRLJ.EZEsk.MuiBox-root > div:nth-child(2) > button > p"))
                    )
    
                    if check_exames_voiston:
                        text_voiston = check_exames_voiston.text.strip()
                        if int (text_voiston) > 0:
                            print(f"Ja ha para o paciente {patient_id}, {text_voiston} exames na voiston")
                            return
                time.sleep(2)
                timeout = 15
                interval = 2
                start_time = time.time()

                while time.time() - start_time < timeout:

                    try:
                        button = WebDriverWait(shadow_content, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button"))
                    )
                        print("Button I encontrado")
                        break
                    except Exception:
                        print("Button I não encontrado, tentando novamente...")
                        time.sleep(interval)

                else:
                    print("Tempo limite atingido. O Button I não foi encontrado.")
                text = check_exames.text.strip()

                if int(text) <= 0:
                    print(f"Paciente {patient_id} não possui novos exames.")
                    return
                
                elif int (text) > 0:
                    print(f"Paciente {patient_id} possui novos exames.")
                    button = WebDriverWait(shadow_content, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button"))
                    )
                    button.click()
                    time.sleep(2)
                    self.click_image("img/ok.png")
                time.sleep(2)
                timeout = 15
                interval = 2
                start_time = time.time()

                while time.time() - start_time < timeout:

                    try:
                        
                        button = WebDriverWait(shadow_content, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button"))
                    )
                        print("Exames carregados com sucesso !")
                        break
                    except Exception:
                        print("Carregando exames...")
                        time.sleep(interval)

                else:
                    print("Tempo limite atingido.")
                
            except:
                print(f"Nao a novos exames para o paciente {patient_id}")

            try:    
                check_exames_voiston = WebDriverWait(shadow_content, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.gWsYQM.Scrollable.MuiBox-root > div > div.sc-bczRLJ.kaYPDH.MuiBox-root > div.sc-bczRLJ.EZEsk.MuiBox-root > div:nth-child(2) > button > p"))
                )
                text_voiston = check_exames_voiston.text.strip()

                if int(text_voiston) <= 0:
                    print(f"Paciente {patient_id} não possui exames na voiston.")
                    button = WebDriverWait(shadow_content, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button"))
                    )
                    button.click()
                    time.sleep(2)
                    self.click_image("img/ok.png")
                    timeout = 15
                    interval = 2
                    start_time = time.time()

                    while time.time() - start_time < timeout:

                        try:
                            if time.time() - start_time > timeout:
                                print("Tempo limite atingido.")
                                break

                            try:
                                time.sleep(1)
                                progress_btn = shadow_content.find_element(By.CSS_SELECTOR, "#voiston-content-base > div > div > div:nth-child(2) > div > div > div.sc-bczRLJ.eXQUmS.MuiBox-root > div > button")
                                txt = progress_btn.text.strip().rstrip("%")

                                if txt.isdigit() and int(txt) >= 100:
                                    print("✅ Progresso atingiu 100%")
                                    break

                            except NoSuchElementException:
                                print("Botão de progresso desapareceu")
                                break

                        except Exception:
                            print("Button II não encontrado, tentando novamente...")
                            time.sleep(interval)

                    else:
                        print("Tempo limite atingido. O Button II não foi encontrado.")

                elif int (text_voiston) > 0:
                    print(f"Ja ha para o paciente {patient_id}, {text_voiston} exames na voiston")

            except Exception as e:
                self.add_not_found_patient(patient_id, name, patient_dob, exam_date,"Erro ao verificar exames na Vöiston")
            
        except Exception as e:
            msg = f"Erro ao realizar importação de exames para o paciente {patient_id}: {e}"
            logger.exception(msg, exc_info=False)
            self.add_error(msg)

    def click_image(self, image_path):
        import pyautogui
        location = pyautogui.locateCenterOnScreen(image_path,confidence=0.8)
        if location is not None:
            pyautogui.click(location)
        else:
            print(f'Elemento não encontrado: {image_path}')