# RPA/rpa_get_services.py
import os
import time
import logging

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
        self.expected = next(
            (item for item in all_items if item.get('plataforma') == 'TOKIO'),
            None
        )
        if not self.expected:
            logger.error("Nenhum registro com plataforma='TOKIO' encontrado")
            raise ValueError("Registro TOKIO não encontrado")

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
        except Exception as e:
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
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "usuario")))
            self.driver.find_element(By.ID, "usuario").clear()
            self.driver.find_element(By.ID, "usuario").send_keys("ALINE BASE")

            pwd = self.driver.find_element(By.ID, "Senha")
            pwd.clear()
            pwd.send_keys("Ar91430863@")
            pwd.send_keys(Keys.RETURN)

            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'OK')]"))
                )
                self.driver.execute_script("arguments[0].click();", element)
                logger.info("Alerta de múltiplos acessos confirmado")
            except TimeoutException:
                pass

            logger.info("Login realizado com sucesso")

        except Exception:
            logger.exception("Erro durante o login")
            raise

    def _sessao_valida(self) -> bool:
        try:
            self.driver.find_element(By.ID, "main-content")
            return True
        except NoSuchElementException:
            return False

    def _safe_get_text(self, xpath: str) -> str:
        try:
            return self.driver.find_element(By.XPATH, xpath).text
        except Exception as e:
            logger.debug(f"[DOM] Elemento não encontrado: {xpath} | {e}")
            return ""

    def monitor_servicos(self):
        logger.info("Monitorando serviços...")
        td_xpath = "/html/body/div[1]/app-container/div[2]/app-acompanhamento-servico/div/div[2]/div/div/table/tbody/tr[1]/td[6]"

        try:
            td_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, td_xpath))
            )

            if td_element.is_displayed():
                logger.info("Serviço detectado. Expandindo...")
                td_element.click()

                tipo_servico = td_element.text
                bairro = self._safe_get_text("//*[@id='collapse_1']/div/div[2]/div[2]")
                cidade = self._safe_get_text("//*[@id='collapse_1']/div/div[2]/div[3]")
                data_inicio = self._safe_get_text("/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[1]/span")
                data_fim = self._safe_get_text("/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[2]/span")
                localizacao = self._safe_get_text("/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[3]/div[3]/span")

                logger.info(
                    f"UI => Serviço: {tipo_servico}, Cidade: {cidade}, Bairro: {bairro}, Início: {data_inicio}, Fim: {data_fim}, Local: {localizacao}"
                )

                expected_service = next((s for s in self.expected['services'] if s.get('active')), None)
                expected_city = self.expected['cities'][0] if self.expected['cities'] else {}

                match = (
                    tipo_servico.strip().lower() == expected_service['service'].strip().lower() and
                    cidade.strip().lower() == expected_city['city'].strip().lower() and
                    bairro.strip().lower() in [
                        n['name'].strip().lower() for n in expected_city.get('neighborhoods', []) if n['active']
                    ]
                )

                if match:
                    logger.info("Serviço compatível. Aceitando...")
                    self.driver.find_element(By.XPATH, "//*[@id='aceitar']").click()
                else:
                    logger.warning("Serviço não compatível. Ignorando.")

        except TimeoutException:
            logger.debug("Nenhum serviço visível no momento.")
        except Exception as e:
            logger.error(f"Erro inesperado ao monitorar serviço: {e}")
