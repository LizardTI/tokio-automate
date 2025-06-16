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

    def _handle_alert_ok(self):
        """Clica no botão de alerta, se visível."""
        try:
            alert_ok_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="alert-ok"]'))
            )
            alert_ok_btn.click()
            logger.info('✅ Botão "alert-ok" clicado com sucesso.')
        except TimeoutException:
            logger.debug('ℹ️ Botão "alert-ok" não encontrado. Seguindo...')

    def _process_service(self):
        """Processa o serviço disponível na tela."""
        try:
            # Constantes de XPath (boa prática pra manutenção futura)
            SERVICE_CELL_XPATH = "/html/body/div[1]/app-container/div[2]/app-acompanhamento-servico/div/div[2]/div/div/table/tbody/tr[1]/td[6]"
            BAIRRO_XPATH = "//*[@id='collapse_1']/div/div[2]/div[2]"
            CIDADE_XPATH = "//*[@id='collapse_1']/div/div[2]/div[3]"
            DATA_INICIO_XPATH = "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[1]/span"
            DATA_FIM_XPATH = "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[4]/div[2]/span"
            LOCALIZACAO_XPATH = "/html/body/modal-overlay/bs-modal-container/div/div/app-modal-aceite/div/div/div[2]/div[3]/div[3]/span"
            ACEITAR_BTN_XPATH = "//*[@id='aceitar']"

            # Abre o serviço
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, SERVICE_CELL_XPATH))
                )
                self.driver.find_element(By.XPATH, SERVICE_CELL_XPATH).click()
                logger.info("Serviço aberto com sucesso.")
            except TimeoutException:
                logger.warning("⚠️ Serviço não encontrado ou não carregado a tempo.")
                return

            # Captura os dados da UI
            tipo_servico = self.driver.find_element(By.XPATH, SERVICE_CELL_XPATH).text.strip()
            bairro = self.driver.find_element(By.XPATH, BAIRRO_XPATH).text.strip()
            cidade = self.driver.find_element(By.XPATH, CIDADE_XPATH).text.strip()
            data_inicio = self.driver.find_element(By.XPATH, DATA_INICIO_XPATH).text.strip()
            data_fim = self.driver.find_element(By.XPATH, DATA_FIM_XPATH).text.strip()
            localizacao = self.driver.find_element(By.XPATH, LOCALIZACAO_XPATH).text.strip()

            logger.info(
                f"📋 Capturado da UI => Serviço: {tipo_servico}, Cidade: {cidade}, Bairro: {bairro}, "
                f"Início: {data_inicio}, Fim: {data_fim}, Localização: {localizacao}"
            )

            # Validação com o esperado
            expected_service = next((s for s in self.expected.get('services', []) if s.get('active')), None)
            expected_city = self.expected.get('cities', [{}])[0]

            if not expected_service or not expected_city:
                logger.warning("⚠️ Dados esperados do DynamoDB não encontrados ou incompletos.")
                return

            bairro_match = bairro.lower() in [
                n['name'].strip().lower()
                for n in expected_city.get('neighborhoods', []) if n.get('active')
            ]

            match = (
                tipo_servico.lower() == expected_service['service'].strip().lower() and
                cidade.lower() == expected_city['city'].strip().lower() and
                bairro_match
            )

            if match:
                logger.info("✅ Dados validados com sucesso! Aceitando serviço...")
                self.driver.find_element(By.XPATH, ACEITAR_BTN_XPATH).click()
            else:
                logger.warning("❌ Dados não conferem com o esperado. Serviço NÃO aceito.")

        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar serviço: {e}", exc_info=True)


    def start(self):
        logger.info("=== Iniciando fluxo de RPA '%s' ===", self.service_name)
        self.login()
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

    def login(self):
        if self.logged_in:
            logger.debug("Login já realizado anteriormente")
            return

        logger.info("Acessando página de login...")
        try:
            url = "https://tms-prestador.tokiomarine.com.br/login?returnUrl=home"
            self.driver.get(url)

            while not self.logged_in:
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "usuario")))
                    logger.info("Preenchendo credenciais")
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
                        logger.debug("Nenhum alerta para confirmar")

                    # Adiciona chamada para tratar o modal após o login
                    logger.info("Verificando modal de aviso após login...")
                    self._handle_alert_ok()

                    logger.info("Login realizado com sucesso")
                    self.logged_in = True
                except TimeoutException:
                    if not self.logged_in:
                        time.sleep(3)
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
        try:
            self._process_service()
        except Exception as e:
            logger.error(f"❌ Erro inesperado no processo principal: {e}", exc_info=True)
