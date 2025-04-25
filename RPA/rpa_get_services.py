class RpaService:
    def __init__(self, service_name):
        self.service_name = service_name

    def start(self):
        print(f"Iniciando o serviço de RPA: {self.service_name}")
        # Aqui você colocaria a lógica real para iniciar o seu serviço de RPA
        # Isso pode envolver interagir com outras bibliotecas ou sistemas.

    def stop(self):
        print(f"Parando o serviço de RPA: {self.service_name}")
        # Aqui você colocaria a lógica para parar o seu serviço de RPA

    def get_status(self):
        print(f"Obtendo o status do serviço de RPA: {self.service_name}")
        return "Em execução" # Exemplo de status

if __name__ == '__main__':
    # Exemplo de uso
    rpa_service = RpaService("Processo de Extração de Dados")
    rpa_service.start()
    print(f"Status: {rpa_service.get_status()}")
    rpa_service.stop()