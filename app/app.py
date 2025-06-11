#!/usr/bin/env python3
# app.py - Deployment Ready Version

import streamlit as st
import toml
import time
import os
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
# Load database configuration (no OpenAI key needed here)
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
        'chat_history': [],
        'openai_api_key': None,
        'api_key_valid': False,
        'show_api_key': False
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

# ─── API KEY VALIDATION ───────────────────────────────────────────────────────

def validate_openai_api_key(api_key):
    """Validate OpenAI API key format"""
    if not api_key:
        return False
    # Basic validation - OpenAI keys start with "sk-" and are typically 51 characters
    if api_key.startswith('sk-') and len(api_key) >= 40:
        return True
    return False

def test_openai_connection(api_key):
    """Test if the OpenAI API key works"""
    try:
        os.environ["OPENAI_API_KEY"] = api_key
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        # Test with a minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        return False

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
        .api-key-container {
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
            margin-bottom: 20px;
        }
        .download-guide {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
            margin-bottom: 20px;
        }
        .warning-box {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    # ─── STEP 1: OpenAI API KEY SETUP ─────────────────────────────────────────
    st.sidebar.markdown(
        """
        <div class="api-key-container">
            <h4>🔑 Step 1: OpenAI API Key</h4>
            <p style='font-size: 12px; color: #666;'>Required for AI analysis</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # API Key input
    api_key_placeholder = st.sidebar.empty()
    
    with api_key_placeholder.container():
        if not st.session_state.api_key_valid:
            # Show API key input
            api_key_input = st.text_input(
                "Enter OpenAI API Key",
                type="password" if not st.session_state.show_api_key else "default",
                placeholder="sk-...",
                help="Your API key is not stored and only used during this session",
                key="api_key_input"
            )
            
            # Toggle show/hide API key
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👁️ Show/Hide", key="toggle_api_key"):
                    st.session_state.show_api_key = not st.session_state.show_api_key
                    st.rerun()
            
            with col2:
                if st.button("✅ Validate", key="validate_api_key"):
                    if validate_openai_api_key(api_key_input):
                        with st.spinner("Testing API key..."):
                            if test_openai_connection(api_key_input):
                                st.session_state.openai_api_key = api_key_input
                                st.session_state.api_key_valid = True
                                # Set environment variable for the session
                                os.environ["OPENAI_API_KEY"] = api_key_input
                                st.success("✅ API key validated!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Invalid API key or connection failed")
                    else:
                        st.error("❌ Invalid API key format")
            
            # Privacy notice
            st.markdown(
                """
                <div style='font-size: 11px; color: #888; margin-top: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 5px;'>
                🔒 <strong>Privacy:</strong> Your API key is only stored in memory during this session and is never saved to our servers.
                </div>
                """, unsafe_allow_html=True
            )
            
            # Get API key link
            st.markdown(
                """
                <div style='text-align: center; margin-top: 10px;'>
                <a href='https://platform.openai.com/api-keys' target='_blank' style='color: #4CAF50; text-decoration: none;'>
                🔗 Get your OpenAI API Key
                </a>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            # Show API key is validated
            masked_key = st.session_state.openai_api_key[:8] + "..." + st.session_state.openai_api_key[-4:]
            st.success(f"✅ API Key: {masked_key}")
            
            if st.button("🔄 Change API Key", key="change_api_key"):
                st.session_state.api_key_valid = False
                st.session_state.openai_api_key = None
                if "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
                st.rerun()

    # ─── STEP 2: DATA DOWNLOAD GUIDE ─────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div class="download-guide">
            <h4>📱 Step 2: Get Your Samsung Health Data</h4>
            <p style='font-size: 12px; color: #666;'>Download your health data export</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    with st.sidebar.expander("📥 Download Sample Data", expanded=False):
        st.markdown(
            """
            **Option 1: Use Sample Data (Recommended for Testing)**
            
            Download our sample Samsung Health data to try the app:
            
            🔗 [**Download Sample Data**](https://drive.google.com/file/d/11ScNs1k6Kac1ylLaCMxlGU6f6dru2bn6/view?usp=sharing)
            
            ---
            
            **Option 2: Export Your Own Data**
            
            To export your own Samsung Health data:
            
            1. Open **Samsung Health** app
            2. Go to **Settings** (⚙️)
            3. Tap **Data Export**
            4. Select **Export Data**
            5. Choose time range (e.g., "Last 6 months")
            6. Tap **Export** 
            7. Save the ZIP file
            8. Transfer to your computer
            
            **Supported Data Types:**
            - 🛌 Sleep records
            - 🍎 Food intake
            - 💧 Water intake  
            - 🚶 Step count
            
            **File Format:** ZIP file containing CSV files
            """
        )
        
        st.info("💡 **Tip:** Sample data contains realistic health patterns for demonstration purposes.")

    # ─── STEP 3: MAIN NAVIGATION (only show if API key is valid) ─────────────────
    if st.session_state.api_key_valid:
        st.sidebar.markdown("---")
        st.sidebar.header("📊 Main Menu")
        st.sidebar.button("🏠 Home", on_click=to_home)
        
        with st.sidebar.expander("🚀 Main Features", expanded=True):
            st.button("📊 Dashboard", on_click=to_dashboard, help="View health analytics and insights")
            st.button("🤖 AI Assistant", on_click=to_ai, help="Chat with AI about your health data")
            st.button("📁 Input Data", on_click=to_input_data, help="Upload your Samsung Health data")

        # ─── USER SELECTION & MANAGEMENT ─────────────────────────────────────────
        if st.session_state.main_page in ['user_dashboard', 'ai_assistant']:
            st.sidebar.markdown("---")
            st.sidebar.markdown("**👤 Select User**")
            
            try:
                users = get_existing_users(DB_URL)
                user_map = {row['username']: row['user_id'] for _, row in users.iterrows()}
                user_options = ['-- Select User --'] + list(user_map.keys())
                choice = st.sidebar.selectbox(
                    "Choose user data", user_options, key="user_select",
                    help="Select which user's health data to analyze"
                )
                
                if choice != '-- Select User --':
                    st.session_state.user_id = user_map[choice]
                    st.session_state.username = choice
                    
                    # Delete user section with warning
                    if st.session_state.user_id:
                        with st.sidebar.expander("⚠️ Danger Zone", expanded=False):
                            st.markdown(
                                """
                                <div class="warning-box">
                                <strong>⚠️ WARNING:</strong><br>
                                This will permanently delete:<br>
                                • All health data for this user<br>
                                • All chat history<br>
                                • All dashboard analytics<br>
                                <br>
                                <strong>This action cannot be undone!</strong>
                                </div>
                                """, unsafe_allow_html=True
                            )
                            
                            # Confirmation checkbox
                            confirm_delete = st.checkbox(
                                f"I understand that deleting '{st.session_state.username}' is permanent",
                                key="confirm_delete_checkbox"
                            )
                            
                            # Delete button (only enabled if confirmed)
                            if st.button(
                                f"🗑️ DELETE {st.session_state.username}",
                                key="delete_user_btn",
                                disabled=not confirm_delete,
                                help="This will permanently delete all data for this user"
                            ):
                                try:
                                    with st.spinner(f"Deleting {st.session_state.username}..."):
                                        delete_user_data_mysql(st.session_state.user_id, DB_URL)
                                        delete_user_data_neo4j(st.session_state.user_id)
                                    
                                    st.success(f"✅ User '{st.session_state.username}' and all related data have been permanently deleted.")
                                    
                                    # Reset session state
                                    st.session_state.user_id = None
                                    st.session_state.username = None
                                    st.session_state.session_id = None
                                    st.session_state.chat_history = []
                                    st.session_state.agent_executor = None
                                    
                                    time.sleep(2)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting user: {str(e)}")
            except Exception as e:
                st.sidebar.error(f"Error loading users: {e}")

        # ─── CHAT SESSION MANAGEMENT ─────────────────────────────────────────────
        if st.session_state.main_page == 'ai_assistant' and st.session_state.user_id:
            st.sidebar.markdown("---")
            
            with st.sidebar.expander("💬 Chat Sessions", expanded=False):
                # New session button
                if st.button("➕ New Chat Session", key="new_chat_btn"):
                    try:
                        sid = create_session(st.session_state.user_id)
                        st.session_state.session_id = sid
                        st.session_state.chat_history = []
                        st.session_state.history_loaded_for = None
                        st.success("✅ New chat session created!")
                        time.sleep(1)  # Brief pause to show success message
                        st.rerun()  # Force immediate rerun to refresh the UI
                    except Exception as e:
                        st.error(f"❌ Error creating session: {str(e)}")

                # Session management
                try:
                    sessions = get_sessions(st.session_state.user_id)
                    if not sessions.empty:
                        sess_map = {row['name']: row['session_id'] for _, row in sessions.iterrows()}
                        names = list(sess_map.keys())
                        
                        # Session selection with proper default handling
                        default_idx = 0
                        current_session_name = "New chat"  # Default fallback
                        
                        # Find current session name if session_id exists
                        if st.session_state.session_id and st.session_state.session_id in sess_map.values():
                            current_session_name = next(
                                (k for k, v in sess_map.items() if v == st.session_state.session_id), 
                                names[0] if names else "New chat"
                            )
                            if current_session_name in names:
                                default_idx = names.index(current_session_name)
                        elif names:
                            # If no session selected, default to the most recent (first in list)
                            current_session_name = names[0]
                            st.session_state.session_id = sess_map[current_session_name]
                        
                        selected = st.selectbox(
                            "Select Chat Session", 
                            names,
                            index=default_idx, 
                            key="sess_manage_select",
                            help="Choose which chat session to continue"
                        )
                        
                        # Update session_id when selection changes
                        if selected and selected in sess_map:
                            new_session_id = sess_map[selected]
                            if new_session_id != st.session_state.session_id:
                                st.session_state.session_id = new_session_id
                                st.session_state.history_loaded_for = None
                                st.session_state.chat_history = []
                                st.rerun()  # Refresh to load new session
                        
                        # Rename session
                        new_name = st.text_input(
                            "Rename Session:", 
                            placeholder="Enter new name",
                            key="rename_session_input"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✏️ Rename", key="rename_session_btn") and new_name.strip():
                                try:
                                    rename_session(st.session_state.session_id, new_name.strip())
                                    st.success("✅ Session renamed!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error renaming: {str(e)}")
                        
                        with col2:
                            if st.button("🗑️ Delete", key="delete_session_btn"):
                                try:
                                    delete_session(st.session_state.session_id)
                                    # Reset session state after deletion
                                    st.session_state.session_id = None
                                    st.session_state.history_loaded_for = None
                                    st.session_state.chat_history = []
                                    st.success("✅ Session deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting: {str(e)}")
                    else:
                        st.info("No chat sessions yet. Create your first one!")
                        # Auto-create first session if none exist
                        if not st.session_state.session_id:
                            try:
                                sid = create_session(st.session_state.user_id)
                                st.session_state.session_id = sid
                                st.session_state.chat_history = []
                                st.session_state.history_loaded_for = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error auto-creating session: {str(e)}")
                                
                except Exception as e:
                    st.error(f"Error managing sessions: {e}")
                    # Fallback: try to create a session if none exists
                    if not st.session_state.session_id:
                        try:
                            sid = create_session(st.session_state.user_id)
                            st.session_state.session_id = sid
                            st.rerun()
                        except Exception as fallback_e:
                            st.error(f"Fallback session creation failed: {fallback_e}")
    else:
        # Show message when API key is not provided
        st.sidebar.markdown("---")
        st.sidebar.info("🔑 Please provide your OpenAI API key to access the application features.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    init_session_state()
    render_sidebar()
    page = st.session_state.main_page

    # Check if API key is required for certain pages
    api_required_pages = ['user_dashboard', 'ai_assistant', 'input_user_data']
    
    if page == 'home':
        render_home()
    elif page in api_required_pages and not st.session_state.api_key_valid:
        st.warning("🔑 Please provide your OpenAI API key in the sidebar to access this feature.")
        st.info("👈 Look for 'Step 1: OpenAI API Key' in the sidebar to get started.")
    elif page == 'input_user_data':
        render_input_data(DB_URL)
    elif page == 'user_dashboard':
        if not st.session_state.user_id:
            st.warning("👤 Please select a user in the sidebar first.")
        else:
            render_dashboard(DB_URL)
    elif page == 'ai_assistant':
        if not st.session_state.user_id or not st.session_state.session_id:
            st.warning("👤 Please select a user and create/select a chat session in the sidebar.")
        else:
            if not st.session_state.agent_executor:
                st.session_state.agent_executor = get_graphrag_agent()
            render_ai_assistant()

if __name__ == '__main__':
    main()