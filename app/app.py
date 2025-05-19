#!/usr/bin/env python3
# app.py

import streamlit as st
import toml
import time
from sqlalchemy.exc import SQLAlchemyError
from modules.utils.db.db_utils_mysql import (
    get_existing_users,
    get_user_data_from_mysql,
    push_user_data_mysql,
    delete_user_data_mysql
)
from modules.utils.db.db_utils_neo4j import (
    ingest_user_data_to_neo4j,
    delete_user_data_neo4j,
    driver as neo4j_driver
)
from modules.utils.db.db_chat_mysql import (
    get_sessions,
    create_session,
    rename_session,
    delete_session,
    get_chat_history,
    push_chat_message
)
from modules.utils.cleaner.cleaner import (
    load_csv_from_zip,
    clean_food_intake,
    clean_sleep_hours,
    clean_step_count,
    clean_water_intake
)
from modules.utils.retrieval.graphrag import get_graphrag_agent
from components.home import render_home
from components.input_data import render_input_data
from components.dashboard import render_dashboard
from components.ai_assistant import render_ai_assistant

from urllib.parse import quote_plus

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
cfg = toml.load('secrets.toml')
DB_MYSQL = cfg['mysql']
PASSWORD = quote_plus(DB_MYSQL['password'])
DB_URL = (
    f"mysql+pymysql://{DB_MYSQL['user']}:{PASSWORD}"
    f"@{DB_MYSQL['host']}:{DB_MYSQL['port']}/{DB_MYSQL['database']}"
)
st.set_page_config(page_title="Samsung Health GraphRAG", layout="wide")

# ─── SESSION STATE DEFAULTS ───────────────────────────────────────────────────

def init_session_state():
    defaults = {
        'main_page': 'home',
        'user_id': None,
        'username': None,
        'session_id': None,
        'agent_executor': None,
        'history_loaded_for': None,
        'chat_history': []
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# ─── NAVIGATION CALLBACKS ─────────────────────────────────────────────────────

def to_home():
    st.session_state.main_page = 'home'

def to_input_data():
    st.session_state.main_page = 'input_user_data'

def to_dashboard():
    st.session_state.main_page = 'user_dashboard'

def to_ai():
    st.session_state.main_page = 'ai_assistant'

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

def render_sidebar():
    # Inject CSS to make sidebar buttons full-width
    st.markdown(
        """
        <style>
        /* Full-width buttons in sidebar */
        [data-testid="stSidebar"] .stButton>button {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    # Header and Main Features
    st.sidebar.header("Main Menu")
    st.sidebar.button("Home", on_click=to_home)
    with st.sidebar.expander("Main Features", expanded=True):
        st.button("User Dashboard", on_click=to_dashboard)
        st.button("AI Assistant", on_click=to_ai)
        st.button("Input Data", on_click=to_input_data)

    # Divider
    st.sidebar.markdown("---")

    # Only show user selection when Dashboard or AI Assistant is chosen
    if st.session_state.main_page in ['user_dashboard', 'ai_assistant']:
        try:
            users = get_existing_users(DB_URL)
            user_map = {row['username']: row['user_id'] for _, row in users.iterrows()}
            user_options = ['-- Select --'] + list(user_map.keys())
            choice = st.sidebar.selectbox(
                "Select User", user_options, key="user_select"
            )
            if choice != '-- Select --':
                st.session_state.user_id = user_map[choice]
                st.session_state.username = choice
                # Delete user expander
                if st.session_state.user_id:
                    with st.sidebar.expander("Delete User?", expanded=False):
                        if st.button("Delete This User", key="delete_user_btn"):
                            delete_user_data_mysql(st.session_state.user_id, DB_URL)
                            delete_user_data_neo4j(st.session_state.user_id)
                            st.success(f"User '{st.session_state.username}' and related data have been deleted.")
                            st.session_state.user_id = None
                            st.session_state.username = None
                            st.session_state.session_id = None
                            st.session_state.chat_history = []
                            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error loading users: {e}")

    # Only show chat session controls when AI Assistant page is active and a user is selected
    if st.session_state.main_page == 'ai_assistant' and st.session_state.user_id:
        # st.sidebar.markdown("---")
        # New Chat expander
        # with st.sidebar.expander("New Chat", expanded=True):
        #     if st.button("Start New Session", key="new_chat_btn"):
        #         sid = create_session(st.session_state.user_id)
        #         st.session_state.session_id = sid
        # Manage existing sessions expander
        with st.sidebar.expander("⚙️ Manage Sessions", expanded=False):
            if st.button("➕ Start New Session", key="new_chat_btn"):
                sid = create_session(st.session_state.user_id)
                st.session_state.session_id = sid

            sessions = get_sessions(st.session_state.user_id)
            sess_map = {row['name']: row['session_id'] for _, row in sessions.iterrows()}
            names = list(sess_map.keys())
            if names:
                # default index to current session
                default_idx = 0
                if st.session_state.session_id in sess_map.values():
                    current_name = next(k for k, v in sess_map.items() if v == st.session_state.session_id)
                    default_idx = names.index(current_name)
                selected = st.selectbox(
                    "Select Session", names,
                    index=default_idx, key="sess_manage_select"
                )
                st.session_state.session_id = sess_map[selected]
                # Rename functionality
                new_name = st.text_input(
                    "Rename Session:", key="rename_session_input"
                )
                if st.button("Rename", key="rename_session_btn") and new_name:
                    rename_session(st.session_state.session_id, new_name)
                    st.rerun()
                # Delete functionality
                if st.button("Delete", key="delete_session_btn"):
                    delete_session(st.session_state.session_id)
                    st.session_state.session_id = None
                    st.session_state.history_loaded_for = None
                    st.session_state.chat_history = []
                    st.rerun()

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    init_session_state()
    render_sidebar()
    page = st.session_state.main_page

    if page == 'home':
        render_home()
    elif page == 'input_user_data':
        render_input_data(DB_URL)
    elif page == 'user_dashboard':
        if not st.session_state.user_id:
            st.warning("Select a user first.")
        else:
            render_dashboard(DB_URL)
    elif page == 'ai_assistant':
        if not st.session_state.user_id or not st.session_state.session_id:
            st.warning("User and session required.")
        else:
            if not st.session_state.agent_executor:
                st.session_state.agent_executor = get_graphrag_agent()
            render_ai_assistant()

if __name__ == '__main__':
    main()
