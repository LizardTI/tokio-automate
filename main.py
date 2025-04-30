# main.py
import os
from DynamoDB.get_tables import DynamoDBConnection

def main():
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    aws_key    = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Monta args de conexão (ambiente ou credential chain)
    conn_kwargs = {'region_name': region}
    if aws_key and aws_secret:
        conn_kwargs.update(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret
        )

    db = DynamoDBConnection(**conn_kwargs)
    if not db.connect():
        print("Falha ao conectar no DynamoDB")
        return

    # Busca TODOS os itens
    all_items = db.buscar_dados_tabela('comercial-table')

    # Filtra apenas plataforma == "TOKIO"
    tokio_items = [item for item in all_items if item.get('plataforma') == 'TOKIO']

    # Exibe resultado
    if tokio_items:
        print(f"Foram encontradas {len(tokio_items)} entradas com plataforma 'TOKIO':")
        for entry in tokio_items:
            print(entry)
    else:
        print("Nenhum item com plataforma 'TOKIO' encontrado.")

if __name__ == "__main__":
    main()
