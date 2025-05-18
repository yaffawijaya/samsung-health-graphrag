# db_utils.py
import toml
import pandas as pd
from sqlalchemy import create_engine, text

# Load MySQL connection URL from secrets.toml
cfg = toml.load('secrets.toml').get('mysql', {})
DB_URL_TEMPLATE = (
    "mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)


def _get_engine(url: str):
    return create_engine(url)


def get_existing_users() -> pd.DataFrame:
    """
    Return DataFrame of all users with their user_id and username.
    """
    url = DB_URL_TEMPLATE.format(**cfg)
    engine = _get_engine(url)
    query = "SELECT user_id, username FROM users ORDER BY username"
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame(columns=['user_id', 'username'])


def get_user_data_from_mysql(user_id: int) -> dict:
    """
    Fetch all health data tables for a given user_id.
    Returns a dict keyed by table name.
    """
    url = DB_URL_TEMPLATE.format(**cfg)
    engine = _get_engine(url)
    data = {}
    tables = ['food_intake', 'water_intake', 'sleep_hours', 'step_count']
    for tbl in tables:
        stmt = text(f"SELECT * FROM {tbl} WHERE user_id = :uid")
        try:
            df = pd.read_sql(stmt, engine, params={'uid': user_id})
        except Exception:
            df = pd.DataFrame()
        data[tbl] = df
    return data


def push_user_data(
    username: str,
    df_food: pd.DataFrame,
    df_water: pd.DataFrame,
    df_sleep: pd.DataFrame,
    df_steps: pd.DataFrame
) -> int:
    """
    Insert user and associated health data into MySQL.
    Returns the assigned user_id.
    """
    url = DB_URL_TEMPLATE.format(**cfg)
    engine = _get_engine(url)
    with engine.begin() as conn:
        # 1) Upsert user
        conn.execute(
            text("INSERT IGNORE INTO users (username) VALUES (:u)"),
            {"u": username}
        )
        # 2) Retrieve user_id
        result = conn.execute(
            text("SELECT user_id FROM users WHERE username = :u"),
            {"u": username}
        )
        user_id = result.scalar_one()

        # 3) Insert food_intake
        for _, row in df_food.iterrows():
            conn.execute(
                text(
                    "INSERT INTO food_intake (user_id, event_time, food_name, amount, calories)"
                    " VALUES (:uid, :t, :f, :a, :c)"
                ), {
                    "uid": user_id,
                    "t": row['date'],
                    "f": row['food_name'],
                    "a": row['amount'],
                    "c": row['calories']
                }
            )
        # 4) Insert water_intake
        for _, row in df_water.iterrows():
            conn.execute(
                text(
                    "INSERT INTO water_intake (user_id, event_time, amount)"
                    " VALUES (:uid, :t, :a)"
                ), {
                    "uid": user_id,
                    "t": row['date'],
                    "a": row['total_water_ml']
                }
            )
        # 5) Insert sleep_hours
        for _, row in df_sleep.iterrows():
            conn.execute(
                text(
                    "INSERT INTO sleep_hours (user_id, date, total_sleep_h)"
                    " VALUES (:uid, :d, :h)"
                ), {
                    "uid": user_id,
                    "d": row['date'],
                    "h": row['total_sleep_h']
                }
            )
        # 6) Insert step_count
        for _, row in df_steps.iterrows():
            conn.execute(
                text(
                    "INSERT INTO step_count (user_id, date, total_steps)"
                    " VALUES (:uid, :d, :s)"
                ), {
                    "uid": user_id,
                    "d": row['date'],
                    "s": int(row['total_steps'])
                }
            )
    return user_id


def delete_user_data(user_id: int):
    """
    Delete a user and all associated records by user_id.
    """
    url = DB_URL_TEMPLATE.format(**cfg)
    engine = _get_engine(url)
    tables = ['food_intake', 'water_intake', 'sleep_hours', 'step_count']
    with engine.begin() as conn:
        # Delete from each health table
        for tbl in tables:
            conn.execute(
                text(f"DELETE FROM {tbl} WHERE user_id = :uid"),
                {"uid": user_id}
            )
        # Delete user
        conn.execute(
            text("DELETE FROM users WHERE user_id = :uid"),
            {"uid": user_id}
        )
