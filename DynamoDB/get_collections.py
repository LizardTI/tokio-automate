from connection import DynamoDBConnection

class DynamoDBCollections:
    def __init__(self, db_connection: DynamoDBConnection):
        self.db_connection = db_connection.get_client()

    def list_tables(self):
        if self.db_connection:
            try:
                tables = self.db_connection.tables.all()
                table_names = [table.name for table in tables]
                print("Collections (Tabelas) no DynamoDB:")
                for name in table_names:
                    print(f"- {name}")
                return table_names
            except Exception as e:
                print(f"Erro ao listar as tabelas do DynamoDB: {e}")
                return None
        else:
            print("Não há conexão com o DynamoDB.")
            return None

if __name__ == '__main__':
    # Exemplo de uso
    db_connect = DynamoDBConnection(region_name='sua-regiao') # Substitua pela sua região
    collections_handler = DynamoDBCollections(db_connect)
    collections_handler.list_tables()