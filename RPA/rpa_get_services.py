# RPA/rpa_get_services.py
import os
import time
import logging

import json
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
        self.logged_in = False
        logger.info("Inicializando RpaService: %s", service_name)

        # Configurações de conexão DynamoDB
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
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

        logger.info("Buscando itens da tabela '%s' no DynamoDB...", table_name)
        all_items = self.db.buscar_dados_tabela(table_name)

        # Filtra configuração da plataforma TOKIO
        tokio_items = [item for item in all_items if item.get('plataforma') == 'TOKIO']
        self.config = tokio_items[0]

        # Debug: imprime configuração
        pprint(self.config)

        logger.info("Iniciando driver Selenium (modo visível)")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)

    def start(self):
        logger.info("=== Iniciando fluxo de RPA '%s' ===", self.service_name)
        try:
            self.login()
            while True:
                self.monitor_servicos()
                time.sleep(2)
        except Exception:
            logger.exception("Erro crítico. Reiniciando fluxo após 10 segundos...")
            time.sleep(10)
            self.start()

    def stop(self):
        logger.info("=== Finalizando fluxo de RPA '%s' ===", self.service_name)
        self.driver.quit()

    def get_status(self) -> str:
        return "Em execução"

    def login(self):
        logger.info("Realizando login...")
        try:
            self.driver.get("https://tms-prestador.tokiomarine.com.br/login?returnUrl=home")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "usuario"))
            )
            elem = self.driver.find_element(By.ID, "usuario")
            elem.clear()
            elem.send_keys("ALINE BASE")

            pwd = self.driver.find_element(By.ID, "Senha")
            pwd.clear()
            pwd.send_keys("Ar91430863@")
            pwd.send_keys(Keys.RETURN)

            # Trata alerta de múltiplos acessos
            try:
                btn_ok = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'OK')]"))
                )
                btn_ok.click()
                logger.info("Alerta de múltiplos acessos confirmado")
            except TimeoutException:
                pass

            logger.info("Login realizado com sucesso")
        except Exception:
            logger.exception("Erro durante o login")
            raise

    def is_valid_service(self, service_name: str) -> bool:
        return any(
            svc['service'] == service_name and svc['active']
            for svc in self.config['services']
        )

    def get_city_config(self, city_name: str) -> dict | None:
        return next(
            (c for c in self.config['cities'] if c['city'] == city_name and c['active']),
            None
        )

    def is_valid_neighborhood(self, city_cfg: dict, neighborhood: str) -> bool:
        return any(
            neigh['name'] == neighborhood and neigh['active']
            for neigh in city_cfg['neighborhoods']
        )

    def monitor_servicos(self):
        logger.info("Monitorando serviços...")
        td_xpath = "/html/body/div[1]/app-container/div[2]/app-acompanhamento-servico/div/div[2]/div/div/table/tbody/tr[1]/td[6]"
        try:
            td = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, td_xpath))
            )

            if td.is_displayed():
                svc = td.text

                agora = time.strftime("%H:%M")

                city_xpath = ""
                nbhd_xpath = ""
                start_xpath = "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[1]/span"
                end_xpath = "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[2]/span"

                city = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, city_xpath)))
                nbhd = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, nbhd_xpath)))
                start_scr = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, start_xpath)))
                end_scr = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, end_xpath)))

                city_text = city.text
                nbhd_text = nbhd.text
                start_text = start_scr.text
                end_text = end_scr.text

                logger.info(f"Serviço detectado: {svc}. INICIO: {start_scr}. FIM: {end_scr}")
                td.click()

                # Validações
                if self.is_valid_service(svc):
                    cfg = self.get_city_config(city_text)
                    if cfg and self.is_valid_neighborhood(cfg, nbhd_text):
                        # escolhe janela correta
                        if cfg['is_emergency']:
                            start_cfg, end_cfg = cfg['emergencyStartTime'], cfg['emergencyEndTime']
                        else:
                            start_cfg, end_cfg = cfg['startTimeW'], cfg['endTimeW']
                        # valida correspondência exata
                        if start_scr == start_cfg and end_scr == end_cfg:
                            logger.info(f"Aceitando {svc} em {city_text}/{nbhd_text} — {start_text}-{end_text}")
                            elm.click()
                            return
        except TimeoutException:
            pass
        except Exception as e:
            logger.error(f"Erro na lógica dinâmica: {e}")
