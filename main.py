# main.py
import logging
from RPA.rpa_get_services import RpaService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    try:
        rpa = RpaService(service_name="TOKIO - Validação de Serviços")
        rpa.start()
    except ValueError as e:
        logging.error("Erro de inicialização: %s", str(e))
    except Exception as e:
        logging.error("Erro durante a execução do RPA: %s", str(e))
    finally:
        try:
            rpa.stop()
        except:
            pass  # evita erro se o rpa nunca foi inicializado

if __name__ == "__main__":
    main()
