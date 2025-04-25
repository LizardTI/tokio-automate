from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class RpaService:
    def __init__(self, service_name):
        self.service_name = service_name
        self.driver = webdriver.Chrome()  # Ou Firefox(), Edge(), etc.

    def start(self):
        print(f"Iniciando o serviço de RPA: {self.service_name}")
        self.login()

    def stop(self):
        print(f"Parando o serviço de RPA: {self.service_name}")
        self.driver.quit()  # Fecha o navegador

    def get_status(self):
        print(f"Obtendo o status do serviço de RPA: {self.service_name}")
        return "Em execução"  # Exemplo de status

    def login(self):
        try:
            print("Acessando a página de login...")
            self.driver.get("https://tms-prestador.tokiomarine.com.br/login?returnUrl=home")

            # Aguarda o carregamento da página (ajuste conforme necessário)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print("Página carregada com sucesso!")

            # Aqui você pode adicionar a lógica de login (preencher usuário/senha)
            # Exemplo:
            username_input = self.driver.find_element(By.XPATH, "//*[@id='usuario']")
            password_input = self.driver.find_element(By.XPATH, "//*[@id='Senha']")
            username_input.send_keys("ALINE BASE")
            password_input.send_keys("Ar91430863@")
            password_input.send_keys(Keys.RETURN)

            # Espera um pouco para visualização (remova em produção)
            time.sleep(3)

        except Exception as e:
            print(f"Erro durante o login: {e}")
            self.stop()

if __name__ == '__main__':
    # Exemplo de uso
    rpa_service = RpaService("Processo de Extração de Dados")
    rpa_service.start()
    print(f"Status: {rpa_service.get_status()}")
    rpa_service.stop()