from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

URI = os.getenv("NEO4J_URI")
# Aceita NEO4J_USER ou NEO4J_USERNAME como fallback
USER = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (USER, PASSWORD)
DEFAULT_DB = os.getenv("NEO4J_DATABASE") or None

class Database:
    def __init__(self):
        self._driver = None

    def connect(self):
        if not self._driver:
            try:
                # Conexão segura para nuvem
                self._driver = GraphDatabase.driver(URI, auth=AUTH)
                self._driver.verify_connectivity()
                print(f"✅ Conectado ao AuraDB Cloud: {URI}")
            except Exception as e:
                print(f"❌ Falha na conexão Cloud: {e}")

    def close(self):
        if self._driver:
            self._driver.close()

    def get_session(self, database: str = None):
        """Retorna uma `Session` apontando para `database` (ou `NEO4J_DATABASE` se setado)."""
        if not self._driver:
            self.connect()
        db_name = database or DEFAULT_DB
        if db_name:
            return self._driver.session(database=db_name)
        return self._driver.session()

db = Database()