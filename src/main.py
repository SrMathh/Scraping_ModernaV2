import database
from browser import Browser
from scraper import Scraper

database.inicializar_banco()
browser = Browser()

try:
    browser.open_browser()
    browser.login()
    scraper = Scraper(browser.driver)
    scraper.iniciar_scraping()
except Exception as e:
    print(f"Ocorreu um erro crítico no fluxo principal: {e}")
finally:
    print("Processo finalizado. Fechando o navegador.")
    browser.fechar_navegador()