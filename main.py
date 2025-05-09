# main.py
import logging
from RPA.rpa_get_services import RpaService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    rpa = RpaService(service_name="TOKIO - Validação de Serviços")
    try:
        rpa.run_interactive()
    except Exception as e:
        logging.error("Erro durante a execução do RPA: %s", str(e))
    finally:
        rpa.stop()

if __name__ == "__main__":
    main()
