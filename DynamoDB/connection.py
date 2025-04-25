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

if __name__ == '__main__':
    # Exemplo de uso com credenciais explícitas (NÃO RECOMENDADO PARA PRODUÇÃO)
    # Certifique-se de não commitar suas credenciais diretamente no código!
    access_key = 'SUA_CHAVE_DE_ACESSO'
    secret_key = 'SUA_CHAVE_SECRETA'
    region = 'sua-regiao'

    db_connection_explicit = DynamoDBConnection(
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    dynamodb_resource_explicit = db_connection_explicit.connect()
    if dynamodb_resource_explicit:
        print("Conexão bem-sucedida usando credenciais explícitas!")

    # Exemplo de uso com credenciais padrão (RECOMENDADO)
    db_connection_default = DynamoDBConnection(region_name=region)
    dynamodb_resource_default = db_connection_default.connect()
    if dynamodb_resource_default:
        print("Conexão bem-sucedida usando credenciais padrão!")

    def get_table_data(self, table_name: str, key: str) -> list:
        """Busca dados específicos de uma tabela DynamoDB."""
        try:
            if not self.dynamodb:
                self.connect()

            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key={'config_key': key})
            return response.get('Item', {}).get('config_value', [])

        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return []  # Retorna lista vazia como fallback