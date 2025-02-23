import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve connection details from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def test_connection():
    # Initialize the driver
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # Run a simple query to test the connection
            result = session.run("RETURN 1 AS result")
            record = result.single()
            if record and record["result"] == 1:
                print("Successfully connected to Neo4j!")
            else:
                print("Unexpected result:", record)
    except Exception as e:
        print("Failed to connect to Neo4j:", e)
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()



# def get_food_list():
#     """Connects to the Neo4j database and returns a list of food names that Yaffa has eaten."""
#     driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
#     try:
#         with driver.session() as session:
#             # Run a query to fetch the food names from the Food nodes that Yaffa is connected to via HAS_ATE
#             query = """
#             MATCH (u:User {name: 'Yaffa'})-[:HAS_ATE]->(food:Food)
#             RETURN food.name AS food
#             """
#             result = session.run(query)
#             # Extract the food names from the result
#             food_list = [record["food"] for record in result]
#             return food_list
#     except Exception as e:
#         print("Failed to retrieve food list:", e)
#         return []
#     finally:
#         driver.close()

# if __name__ == "__main__":
#     foods = get_food_list()
#     print("Foods eaten by Yaffa:", foods)
