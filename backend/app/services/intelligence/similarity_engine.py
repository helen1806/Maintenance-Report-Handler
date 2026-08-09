from sentence_transformers import SentenceTransformer
from app.database.neo4jConnection import get_driver

class SimilarityEngine:
    def __init__(self):
        # Using a fast, small embedding model ideal for text matching
        self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        self.driver = get_driver()
        
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
        """Finds FailureModes without embeddings and generates them."""
        query = "MATCH (f:FailureMode) WHERE f.embedding IS NULL RETURN f.name AS name, elementId(f) AS id"
        with self.driver.session() as session:
            results = session.run(query).data()
            
            for row in results:
                # Generate a 384-dimensional vector embedding
                embedding = self.model.encode(row['name']).tolist()
                update_query = "MATCH (f:FailureMode) WHERE elementId(f) = $id SET f.embedding = $embedding"
                session.run(update_query, id=row['id'], embedding=embedding)

    def search_similar_failures(self, failure_text: str, top_k: int = 3):
        """Searches the Neo4j Graph for similar past failures."""
        self.setup_index()
        self.update_missing_embeddings()
        
        embedding = self.model.encode(failure_text).tolist()
        
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
