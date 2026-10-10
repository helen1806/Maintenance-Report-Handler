from app.database.neo4jConnection import get_driver

class AnalyticsEngine:
    def __init__(self):
        self.driver = get_driver()
        
    def get_asset_failure_patterns(self, limit: int = 5):
        """Finds the most frequent failure modes for each asset type."""
        query = """
        MATCH (a:AssetType)-[:HAS]->(c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode)
        RETURN a.name AS asset_type, f.name AS failure_mode, count(f) AS frequency
        ORDER BY frequency DESC, asset_type ASC
        LIMIT $limit
        """
        with self.driver.session() as session:
            return session.run(query, limit=limit).data()

    def get_common_root_causes(self, limit: int = 5):
        """Aggregates the most common root causes across all failures."""
        query = """
        MATCH (f:FailureMode)-[:CAUSED_BY]->(rc:RootCause)
        RETURN rc.name AS root_cause, count(rc) AS frequency
        ORDER BY frequency DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            return session.run(query, limit=limit).data()

    def get_asset_reliability_scores(self):
        """
        Generates an automated reliability score based on historical failure counts.
        (Fewer failures = higher score).
        """
        query = """
        MATCH (a:AssetType)
        OPTIONAL MATCH (a)-[:HAS]->(c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode)
        WITH a.name AS asset, count(f) AS failure_count
        // Simple normalization: Assume 10+ failures is very low reliability
        WITH asset, failure_count, 
             CASE 
                WHEN failure_count = 0 THEN 100
                WHEN failure_count >= 10 THEN 10
                ELSE 100 - (failure_count * 9) 
             END AS reliability_score
        RETURN asset, failure_count, reliability_score
        ORDER BY reliability_score ASC
        """
        with self.driver.session() as session:
            return session.run(query).data()
