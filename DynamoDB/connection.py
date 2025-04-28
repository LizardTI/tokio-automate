import boto3
import os

class DynamoDBConnection:
    def __init__(self, region_name='us-east-1', aws_access_key_id=None, aws_secret_access_key=None):
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
                print(f"Conexão estabelecida com o DynamoDB na região: {self.region_name} usando credenciais explícitas.")
            else:
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
                print(f"Conexão estabelecida com o DynamoDB na região: {self.region_name} usando credenciais padrão (variáveis de ambiente/arquivo de configuração).")
            return self.dynamodb
        except Exception as e:
            print(f"Erro ao conectar com o DynamoDB: {e}")
            return None

    def get_client(self):
        if not self.dynamodb:
            self.connect()
        return self.dynamodb