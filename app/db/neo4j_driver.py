from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jDriver:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def execute_write(self, query: str, parameters: dict = {}):
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(query, parameters))

    def execute_read(self, query: str, parameters: dict = {}):
        with self.driver.session() as session:
            result = session.read_transaction(lambda tx: tx.run(query, parameters))
            return [record.data() for record in result]

neo4j_driver = Neo4jDriver()
