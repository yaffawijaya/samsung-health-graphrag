# db_utils_neo4j.py
import toml
from neo4j import GraphDatabase
import pandas as pd

# Load Neo4j credentials from secrets.toml
cfg = toml.load('secrets.toml').get('neo4j', {})
URI = cfg.get('uri') or cfg.get('NEO4J_URI')
USER = cfg.get('username') or cfg.get('NEO4J_USERNAME')
PASS = cfg.get('password') or cfg.get('NEO4J_PASSWORD')
if not all([URI, USER, PASS]):
    raise ValueError("Neo4j credentials missing under [neo4j] in secrets.toml")

# Initialize driver
driver = GraphDatabase.driver(URI, auth=(USER, PASS))

# Transaction functions

def create_user_node(tx, user_id: int, username: str):
    """
    Merge User node by user_id and set username.
    """
    tx.run(
        "MERGE (u:User {user_id: $uid}) SET u.username = $uname",
        uid=user_id, uname=username
    )


def ingest_food_tx(tx, user_id: int, date: str, food_name: str, amount, calories):
    tx.run(
        """
        MATCH (u:User {user_id: $uid})
        CREATE (f:Food:HealthData {
            name: $food_name,
            amount: toInteger($amount),
            calories: toFloat($calories),
            recordedOn: date($date)
        })
        CREATE (u)-[:HAS_ATE]->(f)
        """,
        uid=user_id,
        food_name=food_name,
        amount=amount,
        calories=calories,
        date=date
    )


def ingest_water_tx(tx, user_id: int, date: str, total_water_ml):
    tx.run(
        """
        MATCH (u:User {user_id: $uid})
        CREATE (w:Water:HealthData {
            name: toString($water),
            amount_ml: toInteger($water),
            recordedOn: date($date)
        })
        CREATE (u)-[:HAS_DRUNK]->(w)
        """,
        uid=user_id,
        water=total_water_ml,
        date=date
    )


def ingest_steps_tx(tx, user_id: int, date: str, total_steps):
    tx.run(
        """
        MATCH (u:User {user_id: $uid})
        CREATE (s:Step:HealthData {
            name: toString($steps),
            count: toInteger($steps),
            recordedOn: date($date)
        })
        CREATE (u)-[:HAS_WALKED]->(s)
        """,
        uid=user_id,
        steps=total_steps,
        date=date
    )


def ingest_sleep_tx(tx, user_id: int, date: str, total_sleep_h):
    tx.run(
        """
        MATCH (u:User {user_id: $uid})
        CREATE (sl:Sleep:HealthData {
            name: toString($sleep),
            duration_h: toFloat($sleep),
            recordedOn: date($date)
        })
        CREATE (u)-[:HAS_SLEPT]->(sl)
        """,
        uid=user_id,
        sleep=total_sleep_h,
        date=date
    )


def ingest_user_data_to_neo4j(
    user_id: int,
    username: str,
    df_food: pd.DataFrame,
    df_water: pd.DataFrame,
    df_steps: pd.DataFrame,
    df_sleep: pd.DataFrame
):
    """
    Ingest a user's data frames into Neo4j.
    User node is merged or created.
    """
    # Ensure date columns are strings in 'YYYY-MM-DD'
    dfs = {'food': df_food, 'water': df_water, 'steps': df_steps, 'sleep': df_sleep}
    for name, df in dfs.items():
        if 'date' not in df.columns:
            raise KeyError(f"DataFrame for {name} missing 'date' column")
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    with driver.session() as session:
        # Create/merge user node
        session.execute_write(create_user_node, user_id, username)

        # Ingest each category
        for row in df_food.to_dict('records'):
            session.execute_write(
                ingest_food_tx,
                user_id,
                row['date'],
                row.get('food_name'),
                row.get('amount'),
                row.get('calories')
            )
        for row in df_water.to_dict('records'):
            session.execute_write(
                ingest_water_tx,
                user_id,
                row['date'],
                row.get('total_water_ml')
            )
        for row in df_steps.to_dict('records'):
            session.execute_write(
                ingest_steps_tx,
                user_id,
                row['date'],
                row.get('total_steps')
            )
        for row in df_sleep.to_dict('records'):
            session.execute_write(
                ingest_sleep_tx,
                user_id,
                row['date'],
                row.get('total_sleep_h')
            )


def delete_user_data_neo4j(user_id: int):
    """
    Delete a user node and all its HealthData relationships in Neo4j.
    """
    with driver.session() as session:
        # Detach delete removes node and its relationships
        session.run(
            "MATCH (u:User {user_id: $uid}) DETACH DELETE u",
            uid=user_id
        )

    print(f"[Neo4j] Deleted user and related data for user_id={user_id}")
