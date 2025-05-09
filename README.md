# Tokio Automate

Este projeto contém automações para a plataforma Tokio Marine.

## Estrutura do Projeto

- `RPA/`: Contém scripts de automação
  - `rpa_get_services.py`: Script para automatizar a obtenção de serviços

## Requisitos

- Python 3.x
- Selenium
- AWS SDK (boto3)
- Chrome WebDriver

## Configuração

1. Configure as variáveis de ambiente AWS:
   - AWS_DEFAULT_REGION
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Para executar a automação:

```bash
python RPA/rpa_get_services.py
```

## Funcionalidades

- Login automático na plataforma Tokio Marine
- Monitoramento de serviços disponíveis
- Aceitação/recusa automática de serviços baseado em regras configuradas no DynamoDB
- Logging detalhado das operações

## Notas

- O script requer credenciais válidas para acesso à plataforma
- As regras de aceitação de serviços são configuradas no DynamoDB
- O script executa em loop contínuo, verificando novos serviços a cada 10 segundos 