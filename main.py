from DynamoDB.connection import DynamoDBConnection
from DynamoDB.get_collections import DynamoDBCollections
from RPA.rpa_get_services import RpaService

def main():
    # 1. Estabelecer conexão com o DynamoDB
    db_connection = DynamoDBConnection(region_name='sua-regiao') # Substitua pela sua região
    dynamodb = db_connection.connect()

    if dynamodb:
        # 2. Listar as collections (tabelas) do DynamoDB
        collections_handler = DynamoDBCollections(db_connection)
        collections = collections_handler.list_tables()
        if collections:
            print("\nCollections encontradas:", collections)

        # 3. Iniciar o serviço de RPA
        rpa_process = RpaService("Processo Principal de Automação")
        rpa_process.start()

        # Aqui você pode adicionar mais lógica para interagir com o RPA,
        # talvez passando informações das collections do DynamoDB para ele.

        # Exemplo de como parar o RPA (em algum momento)
        # rpa_process.stop()

if __name__ == "__main__":
    main()