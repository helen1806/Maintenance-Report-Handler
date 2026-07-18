from neo4j.exceptions import Neo4jError

from app.database.neo4jConnection import get_driver
from app.services.graph_builder import Graph, Node, Relationship


class Neo4jService:
    def __init__(self):
        self.driver = get_driver()

    def close(self):
        
        self.driver.close()

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
      
        Assumes there is only one node of each label in the current context.
        """
        query = f"""
        MATCH (start:{relationship.start_label})
        MATCH (end:{relationship.end_label})
        MERGE (start)-[:{relationship.relationship_type}]->(end)
        """
        tx.run(query)
