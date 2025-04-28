# DynamoDB/connection.py
import boto3

class DynamoDBConnection:
    def __init__(self, region_name, aws_access_key_id=None, aws_secret_access_key=None):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.dynamodb = None

    def connect(self):
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=self.region_name,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key
                )
            else:
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=self.region_name
                )
            return self.dynamodb
        except Exception as e:
            print(f"Erro ao conectar no DynamoDB: {e}")
            return None

    def listar_tabelas(self):
        """Lista e exibe os nomes das tabelas no DynamoDB."""
        if not self.dynamodb:
            self.connect()

        try:
            tables = list(self.dynamodb.tables.all())
            if tables:
                print("Tabelas encontradas:")
                for table in tables:
                    print(f"- {table.name}")
            else:
                print("Nenhuma tabela encontrada.")
        except Exception as e:
            print(f"Erro ao listar tabelas: {e}")

    def buscar_dados_tabela(self, table_name):
        """Busca e exibe todos os dados da tabela especificada."""
        if not self.dynamodb:
            self.connect()

        try:
            table = self.dynamodb.Table(table_name)
            response = table.scan()

            items = response.get('Items', [])
            if items:
                print(f"\nDados encontrados na tabela '{table_name}':")
                for item in items:
                    print(item)
            else:
                print(f"\nNenhum dado encontrado na tabela '{table_name}'.")

            # Paginação se tiver muitos registros
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items = response.get('Items', [])
                for item in items:
                    print(item)

        except Exception as e:
            print(f"Erro ao buscar dados da tabela '{table_name}': {e}")
