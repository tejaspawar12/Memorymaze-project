from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class GraphMemoryManager:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print("✅ Connected to Neo4j")

    def close(self):
        self.driver.close()

    def create_user_node(self, user_id: str):
        query = "MERGE (u:User {id: $user_id}) RETURN u"
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            return result.single()[0]

    def create_plan(self, user_id: str, plan_text: str, day: str):
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (p:Plan {text: $plan_text, day: $day})
        MERGE (u)-[:HAS_PLAN]->(p)
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id, plan_text=plan_text, day=day)
            return result.single()[0]
