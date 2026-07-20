from neo4j import GraphDatabase

from app.config import (
    DATABASE_URI,
    DATABASE_USERNAME,
    DATABASE_PASSWORD,
)


driver = GraphDatabase.driver(
    DATABASE_URI,
    auth=(DATABASE_USERNAME, DATABASE_PASSWORD)
)


def get_driver():
    return driver


def close_driver():
    driver.close()


if __name__ == "__main__":
    try:
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        close_driver()