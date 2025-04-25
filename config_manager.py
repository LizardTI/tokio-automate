from typing import Dict, Any
from DynamoDB.connection import DynamoDBConnection

class ConfigManager:
    def __init__(self, db_connection: DynamoDBConnection):
        self.db = db_connection
        self._config_table = "rpa_configurations"  # Nome da sua tabela no DynamoDB

    def refresh_configs(self) -> Dict[str, Any]:
        """Busca todas as configurações no DynamoDB."""
        return {
            "CITYS_LIST": self._get_config("cities"),
            "SERVICES_LIST": self._get_config("services"),
            "WORKING_HOURS": self._get_config("working_hours"),
            "HOLIDAYS": self._get_config("holidays")
        }

    def _get_config(self, key: str) -> Any:
        """Método privado para buscar uma configuração específica."""
        return self.db.get_table_data(self._config_table, key)