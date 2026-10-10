import os
import requests
from app.database.neo4jConnection import get_driver

class SimilarityEngine:
    def __init__(self):
        self.driver = get_driver()
        # We now use the lightweight free Cloud API instead of a heavy local PyTorch model!
        self.hf_token = os.getenv("HF_TOKEN")
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en-v1.5"
        
    def _get_embedding(self, text: str):
        if not self.hf_token:
            print("WARNING: HF_TOKEN environment variable is not set!")
            return [0.0] * 384
            
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        response = requests.post(self.api_url, headers=headers, json={"inputs": text})
        
        # The API returns a list of floats (the embedding vector)
        return response.json()
        
    def setup_index(self):
        """Creates the Vector Index in Neo4j if it doesn't exist."""
        query = """
        CREATE VECTOR INDEX failure_mode_idx IF NOT EXISTS
        FOR (f:FailureMode) ON (f.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 384,
         `vector.similarity_function`: 'cosine'
        }}
        """
        with self.driver.session() as session:
            session.run(query)
            
    def update_missing_embeddings(self):
        """Finds FailureModes without embeddings and fetches them via the Cloud API."""
        query = "MATCH (f:FailureMode) WHERE f.embedding IS NULL RETURN f.name AS name, elementId(f) AS id"
        with self.driver.session() as session:
            results = session.run(query).data()
            
            for row in results:
                embedding = self._get_embedding(row['name'])
                update_query = "MATCH (f:FailureMode) WHERE elementId(f) = $id SET f.embedding = $embedding"
                session.run(update_query, id=row['id'], embedding=embedding)

    def search_similar_failures(self, failure_text: str, top_k: int = 3):
        """Searches the Neo4j Graph for similar past failures."""
        self.setup_index()
        self.update_missing_embeddings()
        
        embedding = self._get_embedding(failure_text)
        
        query = """
        CALL db.index.vector.queryNodes('failure_mode_idx', $top_k, $embedding)
        YIELD node, score
        MATCH (node)<-[:CAN_EXPERIENCE]-(c:Component)<-[:HAS]-(a:AssetType)
        OPTIONAL MATCH (node)-[:CAUSED_BY]->(rc:RootCause)
        OPTIONAL MATCH (node)-[:RESOLVED_BY]->(ma:MaintenanceAction)
        RETURN node.name AS failure_mode, 
               a.name AS asset, 
               rc.name AS root_cause, 
               ma.name AS maintenance_action, 
               score
        ORDER BY score DESC
        """
        with self.driver.session() as session:
            return session.run(query, embedding=embedding, top_k=top_k).data()
