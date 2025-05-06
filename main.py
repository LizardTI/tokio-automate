# main.py
import os
from DynamoDB.get_tables import DynamoDBConnection
from RPA.rpa_get_services import RpaService

def main():
    # Configura conexão DynamoDB (ambiente ou credential chain)
    region   = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    aws_key  = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    conn_kwargs = {'region_name': region}
    if aws_key and aws_secret:
        conn_kwargs.update(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret
        )

    # Conecta DynamoDB
    db = DynamoDBConnection(**conn_kwargs)
    if not db.connect():
        print("Falha ao conectar no DynamoDB")
        return

    # Busca e exibe itens TOKIO
    all_items = db.buscar_dados_tabela('comercial-table')
    tokio_items = [item for item in all_items if item.get('plataforma') == 'TOKIO']
    if tokio_items:
        print(f"Encontradas {len(tokio_items)} entradas com plataforma 'TOKIO':")
        for entry in tokio_items:
            print(entry)
    else:
        print("Nenhum item com plataforma 'TOKIO' encontrado.")

    # Executa RPA de validação em modo interativo
    print("\nIniciando RPA de validação no navegador...")
    rpa = RpaService("Validação TMS Tokio")
    rpa.run_interactive()


if __name__ == "__main__":
    main()