# No seu main.py
from DynamoDB.connection import DynamoDBConnection
from RPA.rpa_get_services import RpaService


def main():
    # 1. Conexão com DynamoDB
    db_conn = DynamoDBConnection(region_name='us-east-1')

    # 2. Inicia RPA (já carrega configs automaticamente)
    rpa = RpaService("Automação Notro")

    # 3. Para recarregar configs durante execução:
    rpa._load_configurations()  # Atualiza listas do DynamoDB

if __name__ == "__main__":
    main()