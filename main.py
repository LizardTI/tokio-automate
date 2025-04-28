# main.py
from DynamoDB.connection import DynamoDBConnection

def listar_tabelas(dynamodb_resource):
    """Lista e exibe os nomes das tabelas no DynamoDB."""
    try:
        tables = list(dynamodb_resource.tables.all())
        if tables:
            print("Tabelas encontradas:")
            for table in tables:
                print(f"- {table.name}")
        else:
            print("Nenhuma tabela encontrada.")
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")

def main():
    region = 'us-east-1'

    # Exemplo de uso com credenciais explícitas (APENAS PARA TESTES, NUNCA COMMITAR EM PRODUÇÃO)
    access_key = 'AKIAV5CUZH5XNKRORK5G'
    secret_key = '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'

    try:
        db_connection_explicit = DynamoDBConnection(
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        dynamodb_resource_explicit = db_connection_explicit.connect()
        if dynamodb_resource_explicit:
            print("\nConexão bem-sucedida usando credenciais explícitas!")
            listar_tabelas(dynamodb_resource_explicit)
    except Exception as e:
        print(f"Falha na conexão explícita: {e}")

    # Exemplo de uso com credenciais padrão (RECOMENDADO)
    try:
        db_connection_default = DynamoDBConnection(region_name=region)
        dynamodb_resource_default = db_connection_default.connect()
        if dynamodb_resource_default:
            print("\nConexão bem-sucedida usando credenciais padrão!")
            listar_tabelas(dynamodb_resource_default)
    except Exception as e:
        print(f"Falha na conexão padrão: {e}")

if __name__ == "__main__":
    main()
