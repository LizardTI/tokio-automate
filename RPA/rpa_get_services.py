# RPA/rpa_get_services.py
import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
        self.alert_checked = False
        self.logged_in = False  # Adicionando flag para controlar estado do login
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
        self.login()  # Login ocorre apenas uma vez no início
        while True:
            self.main_process()
            logger.info("Aguardando próximo ciclo...")
            time.sleep(10)

    def stop(self):
        logger.info("=== Finalizando fluxo de RPA '%s' ===", self.service_name)
        self.driver.quit()

    def get_status(self) -> str:
        logger.info("Status solicitado para RPA '%s'", self.service_name)
        return "Em execução"

    def confirmar_alerta(self):
        if self.alert_checked:
            return
        try:
            logger.info("Verificando alerta de múltiplos acessos...")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "alert-ok"))
            )

            ok_btn = self.driver.find_element(By.ID, "alert-ok")
            ok_btn.click()

            logger.info("Verificando alerta de múltiplos acessos...")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "logar"))
            )

            entrar_btn = self.driver.find_element(By.ID, "logar")
            entrar_btn.click()

            logger.info("Botões de alerta confirmados")
        except TimeoutException:
            logger.debug("Nenhum alerta de múltiplos acessos encontrado")
        finally:
            self.alert_checked = True

    def login(self):
        if self.logged_in:  # Se já estiver logado, não faz nada
            logger.debug("Login já realizado anteriormente")
            return

        logger.info("Acessando página de login...")
        try:
            url = "https://tms-prestador.tokiomarine.com.br/login?returnUrl=home"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "usuario"))
            )

            logger.info("Preenchendo credenciais")
            self.driver.find_element(By.ID, "usuario").send_keys("ALINE BASE")
            pwd = self.driver.find_element(By.ID, "Senha")
            pwd.send_keys("Ar91430863@")
            pwd.send_keys(Keys.RETURN)

            time.sleep(3)
            self.confirmar_alerta()
            self.logged_in = True  # Marca como logado após sucesso

        except Exception:
            logger.exception("Erro durante o login")
            self.stop()
            raise

    def run_interactive(self):
        try:
            self.start()
        except KeyboardInterrupt:
            logger.info("Interrompido manualmente.")
        finally:
            self.stop()

    def main_process(self):
        logger.info("Iniciando processo principal...")
        self.confirmar_alerta()  # Apenas verifica alertas, não faz login novamente
        try:
            tipo_servico = self.driver.find_element(By.XPATH,
                                                    "/html/body/div[1]/app-container/div[2]/app-acompanhamento-servico/div/div[2]/div/div/table/tbody/tr[1]/td[6]").text
            logger.info(f"Tipo de serviço: {tipo_servico}")

            self.driver.find_element(By.XPATH, "//*[@id='aceitar']")
            self.driver.find_element(By.XPATH, "//*[@id='recusar']")
            self.driver.find_element(By.XPATH, "//*[@id='heading']/div/a").click()

            bairro = self.driver.find_element(By.XPATH, "//*[@id='collapse_1']/div/div[2]/div[2]").text
            cidade = self.driver.find_element(By.XPATH, "//*[@id='collapse_1']/div/div[2]/div[3]").text

            logger.info(f"Cidade: {cidade}, Bairro: {bairro}")

            data_inicio = self.driver.find_element(By.XPATH,
                                                   "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[1]/span").text
            data_fim = self.driver.find_element(By.XPATH,
                                                "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[2]/span").text
            localizacao = self.driver.find_element(By.XPATH,
                                                   "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[3]/div[3]/span").text

            logger.info(f"Início: {data_inicio}, Fim: {data_fim}, Localização: {localizacao}")

        except Exception:
            logger.warning("Algum dos elementos esperados não foi encontrado no DOM atual.")