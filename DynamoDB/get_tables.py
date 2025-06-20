# DynamoDB/get_tables.py
import boto3
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class DynamoDBConnection:
    def __init__(self, region_name, aws_access_key_id=None, aws_secret_access_key=None):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.dynamodb = None

    def connect(self):
        params = {'region_name': self.region_name}
        if self.aws_access_key_id and self.aws_secret_access_key:
            params.update(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        try:
            self.dynamodb = boto3.resource(
                "dynamodb",
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            return self.dynamodb
        except Exception as e:
            print(f"Erro ao conectar no DynamoDB: {e}")
            return None

    def buscar_dados_tabela(self, table_name) -> list:
        """Faz scan e retorna a lista de itens (não imprime)."""
        if not self.dynamodb:
            self.connect()

        table = self.dynamodb.Table(
            table_name
        )
        items = []
        try:
            response = table.scan()
            items.extend(response.get('Items', []))
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
                print(f"{items}")
        except Exception as e:
            print(f"Erro ao buscar dados da tabela '{table_name}': {e}")
        return items
