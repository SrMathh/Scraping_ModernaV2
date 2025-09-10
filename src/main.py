from browser import Browser
from scraper import Scraper
import database

def execute_scraping():
    """
    Função principal que encapsula todo o processo de scraping.
    Retorna um dicionário com o resumo da execução.
    """
    database.inicializar_banco()
    browser = Browser()
    
    summary = {
        "captured": [],
        "errors": []
    }

    try:
        browser.open_browser()
        if browser.errors:
            summary["errors"].extend(browser.errors)
            raise Exception("Erro na inicialização do navegador.")

        browser.login()
        if browser.errors:
            summary["errors"].extend(browser.errors)
            raise Exception("Erro durante o login.")

        scraper = Scraper(browser.driver)
        scraper.iniciar_scraping()
        
    except Exception as e:
        error_msg = f"Ocorreu um erro crítico no fluxo principal: {e}"
        print(error_msg)
        summary["errors"].append(error_msg)
        if browser.errors:
            summary["errors"].extend(browser.errors)
            
    finally:
        print("Processo finalizado. Fechando o navegador.")
        browser.fechar_navegador()

    return summary

if __name__ == "__main__":
    execute_scraping()