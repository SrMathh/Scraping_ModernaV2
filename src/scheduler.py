import yaml
import time
from datetime import datetime
import logging
import main
from utils.render_email import render_summary_email
from utils.email_brevo import send_via_brevo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scraping_task():
    """
    Executa uma única tarefa de scraping e retorna um resumo.
    """
    start_time = time.time()
    start_dt = datetime.now()
    
    summary = main.execute_scraping() 
    
    end_time = time.time()
    duration_seconds = end_time - start_time

    hrs, rem = divmod(duration_seconds, 3600)
    mins, secs = divmod(rem, 60)
    duration_str = f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}"
    start_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")

    logging.info(f"Execução concluída em {duration_str}.")
    logging.info(f"Resumo: {summary}")

    try:
        logging.info("Renderizando e enviando e-mail de resumo...")
        html_content = render_summary_email(
            start_dt=start_dt_str,
            duration_seconds=duration_str,
            captured=summary.get("captured", []),
            errors=summary.get("errors", [])
        )
        send_via_brevo(html_content, "Relatório de Execução do Scraping")
        logging.info("E-mail de resumo enviado com sucesso.")
    except Exception as e:
        logging.error(f"Falha ao enviar e-mail de resumo: {e}")


if __name__ == "__main__":
    logging.info("Iniciando o Orquestrador de Scraping...")
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Arquivo 'config.yaml' não encontrado. Encerrando.")
        exit()

    mode = config.get("mode", "range")

    if mode == "scheduled":
        schedule_config = config.get("schedule", {})
        interval_str = schedule_config.get("every", "24h")
        
        unit = interval_str[-1].lower()
        value = int(interval_str[:-1])
        if unit == 'm':
            sleep_seconds = value * 60
        elif unit == 'h':
            sleep_seconds = value * 3600
        else:
            sleep_seconds = 24 * 3600 

        logging.info(f"Modo agendado ativado. Executando a cada {interval_str}.")
        while True:
            run_scraping_task()
            logging.info(f"Próxima execução em {interval_str}. Aguardando...")
            time.sleep(sleep_seconds)
            
    elif mode == "range":
        logging.info("Modo 'range' ativado. Executando a tarefa uma vez.")
        run_scraping_task()
        
    else: 
        logging.info("Modo 'all' ativado. Executando a tarefa uma vez.")
        run_scraping_task()

    logging.info("Orquestrador finalizado.")