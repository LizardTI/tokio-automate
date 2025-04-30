# RPA/rpa_get_services.py

import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from DynamoDB.get_tables import DynamoDBConnection

# --- Configuração global do logger ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class RpaService:
    def __init__(self, service_name: str, table_name: str = 'comercial-table'):
        self.service_name = service_name
        logger.info("Inicializando RpaService: %s", service_name)

        # 1) Conexão DynamoDB
        region     = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        aws_key    = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        conn_kwargs = {'region_name': region}
        if aws_key and aws_secret:
            conn_kwargs.update(
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret
            )

        self.db = DynamoDBConnection(**conn_kwargs)
        if not self.db.connect():
            logger.error("Não foi possível conectar ao DynamoDB")
            raise RuntimeError("Falha no DynamoDB")

        # 2) Carrega dados TOKIO
        logger.info("Buscando itens da tabela '%s' no DynamoDB...", table_name)
        all_items = self.db.buscar_dados_tabela(table_name)
        self.expected = next(
            (item for item in all_items if item.get('plataforma') == 'TOKIO'),
            None
        )
        if not self.expected:
            logger.error("Nenhum registro com plataforma='TOKIO' encontrado")
            raise ValueError("Registro TOKIO não encontrado")

        # 3) Inicia Selenium
        logger.info("Iniciando driver Selenium")
        self.driver = webdriver.Chrome()

    def start(self):
        logger.info("=== Iniciando fluxo de RPA '%s' ===", self.service_name)
        self.login()
        self.main_process()

    def stop(self):
        logger.info("=== Finalizando fluxo de RPA '%s' ===", self.service_name)
        self.driver.quit()

    def get_status(self) -> str:
        logger.info("Status solicitado para RPA '%s'", self.service_name)
        return "Em execução"

    def login(self):
        logger.info("Acessando página de login...")
        try:
            url = "https://tms-prestador.tokiomarine.com.br/login?returnUrl=home"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Página de login carregada")

            logger.info("Preenchendo credenciais")
            self.driver.find_element(By.ID, "usuario").send_keys("ALINE BASE")
            pwd = self.driver.find_element(By.ID, "Senha")
            pwd.send_keys("Ar91430863@")
            pwd.send_keys(Keys.RETURN)

            time.sleep(3)
            logger.info("Login realizado com sucesso")

        except Exception as e:
            logger.exception("Erro durante o login")
            self.stop()
            raise

    def main_process(self):
        logger.info("Iniciando extração de dados da UI")
        ui_cities   = self._extract_cities_from_ui()
        ui_services = self._extract_services_from_ui()

        # cidades
        expected_cities = { c['city'] for c in self.expected['cities'] }
        missing = expected_cities - set(ui_cities)
        extra   = set(ui_cities) - expected_cities

        logger.info("--- Validação de Cidades ---")
        logger.info("Esperadas: %s", expected_cities)
        logger.info("Encontradas na UI (%d): %s", len(ui_cities), ui_cities)
        logger.info("Faltando   : %s", missing or "nenhuma")
        logger.info("Extras     : %s", extra   or "nenhuma")

        # serviços
        expected_svcs = { s['service'] for s in self.expected['services'] if s.get('active') }
        ui_svcs_set   = set(ui_services)

        logger.info("--- Validação de Serviços ---")
        logger.info("Esperados (ativos): %s", expected_svcs)
        logger.info("Encontrados na UI (%d): %s", len(ui_services), ui_services)
        logger.info("Faltando   : %s", expected_svcs - ui_svcs_set or "nenhum")
        logger.info("Extras     : %s", ui_svcs_set - expected_svcs or "nenhum")

    def _extract_cities_from_ui(self) -> list[str]:
        logger.info("Extraindo cidades da UI...")
        elems = self.driver.find_elements(By.CSS_SELECTOR, ".city-name")
        cities = [e.text.strip() for e in elems if e.text.strip()]
        logger.info("Cidades extraídas: %d", len(cities))
        return cities

    def _extract_services_from_ui(self) -> list[str]:
        logger.info("Extraindo serviços da UI...")
        elems = self.driver.find_elements(By.CSS_SELECTOR, ".service-name")
        services = [e.text.strip() for e in elems if e.text.strip()]
        logger.info("Serviços extraídos: %d", len(services))
        return services

if __name__ == "__main__":
    rpa = RpaService("Validação TMS Tokio")
    try:
        rpa.start()
        logger.info("Status final: %s", rpa.get_status())
    finally:
        rpa.stop()
