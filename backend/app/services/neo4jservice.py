from neo4j.exceptions import Neo4jError

from app.database.neo4jConnection import get_driver
from app.services.graph_builder import Graph, Node, Relationship


class Neo4jService:
    def __init__(self):
        self.driver = get_driver()

    def close(self):
        
        self.driver.close()

    def report_exists(self, file_hash: str) -> bool:
        """Checks if a MaintenanceReport with the given SHA-256 hash already exists."""
        query = "MATCH (r:MaintenanceReport {file_hash: $file_hash}) RETURN count(r) > 0 AS exists"
        with self.driver.session() as session:
            result = session.run(query, file_hash=file_hash)
            return result.single()["exists"]

    def save_graph(self, graph: Graph):
        """
        transaction based
        """
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    for node in graph.nodes:
                        self._create_node(tx, node)
                    
                    for relationship in graph.relationships:
                        self._create_relationship(tx, relationship)
                    # The context manager implicitly commits the transaction 
                    # if no exception is raised.
        except Neo4jError as e:
            raise RuntimeError(f"Failed to persist graph to Neo4j: {str(e)}") from e

    def _create_node(self, tx, node: Node):
       
        if not node.properties:
          
            query = f"MERGE (n:{node.label})"
            tx.run(query)
            return

        props_str = ", ".join([f"{k}: ${k}" for k in node.properties.keys()])
        query = f"MERGE (n:{node.label} {{{props_str}}})"
        tx.run(query, **node.properties)

    def _create_relationship(self, tx, relationship: Relationship):
        """
        Creates a relationship between two exact nodes by matching on their specific properties.
        """
        start_node = relationship.start_node
        end_node = relationship.end_node

        start_props_str = ", ".join([f"{k}: ${k}_start" for k in start_node.properties.keys()])
        end_props_str = ", ".join([f"{k}: ${k}_end" for k in end_node.properties.keys()])
        
        query = f"""
        MATCH (start:{start_node.label} {{{start_props_str}}})
        MATCH (end:{end_node.label} {{{end_props_str}}})
        MERGE (start)-[:{relationship.relationship_type}]->(end)
        """
        
        params = {}
        for k, v in start_node.properties.items():
            params[f"{k}_start"] = v
        for k, v in end_node.properties.items():
            params[f"{k}_end"] = v
            
        tx.run(query, **params)
