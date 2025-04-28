# main.py
from DynamoDB.connection import DynamoDBConnection

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
        if db_connection_explicit.connect():
            print("\nConexão bem-sucedida usando credenciais explícitas!")
            db_connection_explicit.listar_tabelas()
            db_connection_explicit.buscar_dados_tabela('comercial-table')
    except Exception as e:
        print(f"Falha na conexão explícita: {e}")

    # Exemplo de uso com credenciais padrão (RECOMENDADO)
    try:
        db_connection_default = DynamoDBConnection(region_name=region)
        if db_connection_default.connect():
            print("\nConexão bem-sucedida usando credenciais padrão!")
            db_connection_default.listar_tabelas()
            db_connection_default.buscar_dados_tabela('comercial-table')
    except Exception as e:
        print(f"Falha na conexão padrão: {e}")

if __name__ == "__main__":
    main()
