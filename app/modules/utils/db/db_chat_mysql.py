# modules/utils/db/db_chat_mysql.py

import toml
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Load credentials
cfg = toml.load('secrets.toml')['mysql']
password_encoded = quote_plus(cfg['password'])
DB_URL = (
    f"mysql+pymysql://{cfg['user']}:{password_encoded}"
    f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
)

def _get_engine():
    return create_engine(DB_URL)

# 1) List sessions newest first
def get_sessions(user_id: int) -> pd.DataFrame:
    engine = _get_engine()
    query = text("""
        SELECT session_id, name, created_at, updated_at
        FROM chat_sessions
        WHERE user_id = :uid
        ORDER BY created_at DESC
    """
    )
    return pd.read_sql(query, engine, params={"uid": user_id})

# 2) Create a new session
# def create_session(user_id: int, name: str = None) -> int:
#     engine = _get_engine()
#     label = name or 'New chat'
#     with engine.begin() as conn:
#         conn.execute(
#             text("INSERT INTO chat_sessions (user_id, name) VALUES (:uid, :name)"),
#             {"uid": user_id, "name": label}
#         )
#         return conn.execute(text("SELECT LAST_INSERT_ID()"))
    
def create_session(user_id: int, name: str = "New chat") -> int:
    """
    Create a new chat session for the user and return its session_id as an integer.
    """
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO chat_sessions (user_id, name) VALUES (:uid, :name)"),
            {"uid": user_id, "name": name}
        )
        # Ambil ID terakhir sebagai scalar int
        session_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
    return session_id


# 3) Rename session (auto-updates updated_at)
def rename_session(session_id: int, new_name: str) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE chat_sessions SET name = :name WHERE session_id = :sid"),
            {"name": new_name, "sid": session_id}
        )

# 4) Delete session + its history
def delete_session(session_id: int) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM chat_sessions WHERE session_id = :sid"), {"sid": session_id})

# 5) Fetch chat history (chronological)
def get_chat_history(session_id: int) -> pd.DataFrame:
    engine = _get_engine()
    query = text("""
        SELECT role, message, created_at
        FROM chat_history
        WHERE session_id = :sid
        ORDER BY created_at ASC
    """
    )
    return pd.read_sql(query, engine, params={"sid": session_id})

# 6) Insert a chat message
def push_chat_message(session_id: int, role: str, message: str) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO chat_history (session_id, role, message)
                VALUES (:sid, :role, :msg)
            """),
            {"sid": session_id, "role": role, "msg": message}
        )


# # Load MySQL connection parameters
# cfg = toml.load('secrets.toml').get('mysql', {})
# DB_URL_TEMPLATE = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# def _get_engine():
#     """
#     Create a SQLAlchemy engine using the MySQL URL template and loaded credentials.
#     """
#     url = DB_URL_TEMPLATE.format(**cfg)
#     return create_engine(url)

# def get_sessions(user_id: int) -> pd.DataFrame:
#     """
#     Fetch all chat sessions for a given user_id.

#     Returns a DataFrame with columns: session_id, name, created_at.
#     """
#     engine = _get_engine()
#     query = text("""
#         SELECT session_id, name, created_at
#         FROM chat_sessions
#         WHERE user_id = :uid
#         ORDER BY created_at
#     """)
#     return pd.read_sql(query, engine, params={"uid": user_id})

# def create_session(user_id: int, name: str = "New chat") -> int:
#     """
#     Create a new chat session for the user and return its session_id.
#     """
#     engine = _get_engine()
#     with engine.begin() as conn:
#         conn.execute(
#             text("INSERT INTO chat_sessions (user_id, name) VALUES (:uid, :name)"),
#             {"uid": user_id, "name": name}
#         )
#         # Retrieve the auto-generated session_id
#         session_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
#     return session_id

# def rename_session(session_id: int, new_name: str) -> None:
#     """
#     Rename an existing chat session.
#     """
#     engine = _get_engine()
#     with engine.begin() as conn:
#         conn.execute(
#             text("UPDATE chat_sessions SET name = :name WHERE session_id = :sid"),
#             {"name": new_name, "sid": session_id}
#         )

# def delete_session(session_id: int) -> None:
#     """
#     Delete a chat session and all its messages.
#     """
#     engine = _get_engine()
#     with engine.begin() as conn:
#         # If chat_history has ON DELETE CASCADE, this is optional:
#         conn.execute(
#             text("DELETE FROM chat_history WHERE session_id = :sid"),
#             {"sid": session_id}
#         )
#         conn.execute(
#             text("DELETE FROM chat_sessions WHERE session_id = :sid"),
#             {"sid": session_id}
#         )

# def get_chat_history(session_id: int) -> pd.DataFrame:
#     """
#     Fetch all messages (user and assistant) for a given session_id.
    
#     Returns a DataFrame with columns: role, message, created_at.
#     """
#     engine = _get_engine()
#     query = text("""
#         SELECT role, message, created_at
#         FROM chat_history
#         WHERE session_id = :sid
#         ORDER BY created_at
#     """)
#     return pd.read_sql(query, engine, params={"sid": session_id})

# def push_chat_message(session_id: int, role: str, message: str) -> None:
#     """
#     Insert a single chat message into the history for a session.
    
#     role must be either 'user' or 'assistant'.
#     """
#     engine = _get_engine()
#     with engine.begin() as conn:
#         conn.execute(
#             text("""
#                 INSERT INTO chat_history (session_id, role, message)
#                 VALUES (:sid, :role, :msg)
#             """),
#             {"sid": session_id, "role": role, "msg": message}
#         )
