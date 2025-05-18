#!/usr/bin/env python3
# app.py
import streamlit as st
import time
import re
import pandas as pd
import zipfile
import toml
import plotly.express as px
from sqlalchemy.exc import SQLAlchemyError

from modules.utils.db.db_utils_mysql import (
    get_existing_users,
    get_user_data_from_mysql,
    push_user_data,
    delete_user_data
)
from modules.utils.db.db_utils_neo4j import (
    ingest_user_data_to_neo4j,
    delete_user_data_neo4j,
    driver as neo4j_driver
)
from modules.utils.cleaner.cleaner import (
    load_csv_from_zip,
    clean_food_intake,
    clean_sleep_hours,
    clean_step_count,
    clean_water_intake
)
from modules.utils.retrieval.graphrag import get_graphrag_agent

# Configuration
cfg_mysql = toml.load('secrets.toml')['mysql']
DB_URL = (
    f"mysql+pymysql://{cfg_mysql['user']}:{cfg_mysql['password']}"
    f"@{cfg_mysql['host']}:{cfg_mysql['port']}/{cfg_mysql['database']}"
)

# Streamlit setup
st.set_page_config(page_title="Samsung Health GraphRAG Explorer", layout="wide")
st.title("📱 Samsung Health GraphRAG Explorer")

# Initialize session state
if 'main_page' not in st.session_state:
    st.session_state.main_page = 'input_user_data'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None
if 'ai_history' not in st.session_state:
    st.session_state.ai_history = []

# Navigation callbacks
def to_input_user_data():
    st.session_state.main_page = 'input_user_data'

def to_user_dashboard():
    st.session_state.main_page = 'user_dashboard'

def to_ai_assistant():
    st.session_state.main_page = 'ai_assistant'

# Sidebar - Menu and User Selector
with st.sidebar:
    st.header("Main Menu")
    st.button("📝 Input Data", on_click=to_input_user_data)
    st.button("📊 User Dashboard", on_click=to_user_dashboard)
    st.button("🤖 AI Assistant", on_click=to_ai_assistant)

    st.markdown("---")
    st.subheader("Select User")
    try:
        users_df = get_existing_users()
        options = [f"{row['username']} ({row['user_id']})" for _, row in users_df.iterrows()]
    except Exception as e:
        st.error(f"Error loading users: {e}")
        options = []
    selection = st.selectbox("User:", ["-- Select --"] + options)
    if selection and selection != "-- Select --":
        uname, uid_str = selection.rsplit(" (", 1)
        uid = int(uid_str.rstrip(")"))
        # Validate existence in Neo4j
        with neo4j_driver.session() as session:
            res = session.run(
                "MATCH (u:User {user_id: $uid}) RETURN count(u) AS c",
                uid=uid
            ).single()
            count = res['c'] if res else 0
        if count == 0:
            st.error(f"User_id {uid} not found in Neo4j. Please ensure data ingestion.")
            st.session_state.user_id = None
            st.session_state.username = None
        else:
            st.session_state.user_id = uid
            st.session_state.username = uname

    # Delete User
    if st.session_state.user_id:
        st.markdown("---")
        st.subheader("Delete User")
        confirm = st.text_input("Type DELETE to confirm deletion:", key="del_confirm")
        if st.button("Delete", key="del_btn"):
            if confirm == "DELETE":
                try:
                    delete_user_data(st.session_state.user_id)
                    delete_user_data_neo4j(st.session_state.user_id)
                    st.success(f"Deleted user {st.session_state.username} (ID {st.session_state.user_id}) from both DBs.")
                    st.session_state.user_id = None
                    st.session_state.username = None
                    st.session_state.ai_history = []
                except Exception as e:
                    st.error(f"Failed to delete user: {e}")
            else:
                st.error("Type DELETE exactly to confirm.")

# Page: Input User Data
if st.session_state.main_page == 'input_user_data':
    st.header("Input User Data")
    uploaded_zip = st.file_uploader("Upload Samsung Health ZIP file", type="zip")
    if not uploaded_zip:
        st.info("Please upload a Samsung Health ZIP file to proceed.")
        st.stop()

    with zipfile.ZipFile(uploaded_zip) as zip_file:
        df_food_raw = load_csv_from_zip(zip_file, 'com.samsung.health.food_intake')
        df_sleep_raw = load_csv_from_zip(zip_file, 'com.samsung.shealth.sleep')
        df_steps_raw = load_csv_from_zip(zip_file, 'com.samsung.shealth.step_daily_trend')
        df_water_raw = load_csv_from_zip(zip_file, 'com.samsung.health.water_intake')

    df_food_clean = clean_food_intake(df_food_raw) if not df_food_raw.empty else pd.DataFrame()
    df_sleep_clean = clean_sleep_hours(df_sleep_raw) if not df_sleep_raw.empty else pd.DataFrame()
    df_steps_clean = clean_step_count(df_steps_raw) if not df_steps_raw.empty else pd.DataFrame()
    df_water_clean = clean_water_intake(df_water_raw) if not df_water_raw.empty else pd.DataFrame()

    try:
        with zipfile.ZipFile(uploaded_zip) as zip_file:
            df_profile = load_csv_from_zip(zip_file, 'com.samsung.health.user_profile')
            default_username = df_profile.iloc[2, 0] if not df_profile.empty else ""
    except Exception:
        default_username = ""

    new_username = st.text_input("Username for this dataset:", value=default_username)

    if st.button("Push Data to Databases"):
        if not new_username:
            st.error("Username is required.")
        else:
            try:
                user_id = push_user_data(
                    new_username,
                    df_food_clean,
                    df_water_clean,
                    df_sleep_clean,
                    df_steps_clean
                )
                st.success(f"MySQL: Data successfully pushed (user_id={user_id})")
            except Exception as e:
                st.error(f"MySQL push failed: {e}")
                user_id = None

            if user_id:
                try:
                    ingest_user_data_to_neo4j(
                        user_id,
                        new_username,
                        df_food_clean,
                        df_water_clean,
                        df_steps_clean,
                        df_sleep_clean
                    )
                    st.success(f"Neo4j: Data ingested for user_id={user_id}")
                except Exception as e:
                    st.error(f"Neo4j ingestion failed: {e}")

    st.markdown("---")
    st.subheader("Cleaned Data Preview")
    with st.expander("Show Cleaned Data"):
        if not df_food_clean.empty:
            st.write("Cleaned Food Intake"); st.dataframe(df_food_clean)
        if not df_sleep_clean.empty:
            st.write("Cleaned Sleep Hours"); st.dataframe(df_sleep_clean)
        if not df_steps_clean.empty:
            st.write("Cleaned Step Count"); st.dataframe(df_steps_clean)
        if not df_water_clean.empty:
            st.write("Cleaned Water Intake"); st.dataframe(df_water_clean)

# Page: User Health Dashboard
elif st.session_state.main_page == 'user_dashboard':
    st.header("User Health Dashboard")
    user_id = st.session_state.user_id
    username = st.session_state.username
    if not user_id:
        st.warning("Please select a user in the sidebar.")
        st.stop()

    st.subheader(f"Dashboard for {username} (ID: {user_id})")
    data = get_user_data_from_mysql(user_id)
    df_food = data.get('food_intake', pd.DataFrame())
    df_sleep = data.get('sleep_hours', pd.DataFrame())
    df_steps = data.get('step_count', pd.DataFrame())
    df_water = data.get('water_intake', pd.DataFrame())

    for df, col in zip([df_food, df_sleep, df_steps, df_water], ['event_time','date','date','event_time']):
        if not df.empty:
            df['date'] = pd.to_datetime(df[col]).dt.date

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Calories", int(df_food['calories'].sum()) if not df_food.empty else 0)
    c2.metric("Avg Sleep (hrs)", round(df_sleep['total_sleep_h'].mean(), 2) if not df_sleep.empty else 0)
    c3.metric("Total Water (ml)", int(df_water['amount'].sum()) if not df_water.empty else 0)
    c4.metric("Avg Steps/Day", int(df_steps['total_steps'].mean()) if not df_steps.empty else 0)

    st.markdown("---")
    tabs = st.tabs(["Food","Sleep","Steps","Water"])
    with tabs[0]:
        st.subheader("Food Intake Over Time")
        if not df_food.empty:
            df_daily = df_food.groupby('date')['calories'].sum().reset_index()
            st.plotly_chart(px.line(df_daily, x='date', y='calories'), use_container_width=True)
            st.dataframe(df_food[['date','food_name','amount','calories']])
        else:
            st.info("No food data.")
    with tabs[1]:
        st.subheader("Sleep Duration")
        if not df_sleep.empty:
            st.plotly_chart(px.bar(df_sleep, x='date', y='total_sleep_h'), use_container_width=True)
            st.dataframe(df_sleep)
        else:
            st.info("No sleep data.")
    with tabs[2]:
        st.subheader("Step Count Trend")
        if not df_steps.empty:
            st.plotly_chart(px.line(df_steps, x='date', y='total_steps'), use_container_width=True)
            st.dataframe(df_steps)
        else:
            st.info("No step data.")
    with tabs[3]:
        st.subheader("Water Intake")
        if not df_water.empty:
            st.plotly_chart(px.bar(df_water, x='date', y='amount'), use_container_width=True)
            st.dataframe(df_water[['date','amount']])
        else:
            st.info("No water data.")


elif st.session_state.main_page == 'ai_assistant':
    st.header("AI Assistant")

    # 1) Ensure a user is selected
    if not st.session_state.user_id:
        st.warning("Please select a user in the sidebar to use the AI Assistant.")
        st.stop()

    username = st.session_state.username  # e.g. "Yaffa"
    user_id = st.session_state.user_id

    # 2) Lazy‐init agent
    if st.session_state.agent_executor is None:
        st.session_state.agent_executor = get_graphrag_agent()

    # 3) Initialize history & welcome flags
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_user_for_welcome' not in st.session_state:
        st.session_state.last_user_for_welcome = None
    if 'last_page_for_welcome' not in st.session_state:
        st.session_state.last_page_for_welcome = None

    # 4) Show welcome once per user or page load
    should_welcome = (
        st.session_state.last_page_for_welcome != 'ai_assistant'
        or st.session_state.last_user_for_welcome != user_id
    )
    if should_welcome:
        welcome_text = f"👋 Hello, {username}! Ask me anything about your health data."
        with st.chat_message("assistant"):
            def _welcome_gen():
                for word in welcome_text.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            st.write_stream(_welcome_gen())
        st.session_state.last_page_for_welcome = 'ai_assistant'
        st.session_state.last_user_for_welcome = user_id

    # 5) Render previous conversation
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

    # 6) Collect new user input
    user_input = st.chat_input("Ask a question about your health data:")
    if user_input:
        # 6a) Display the user's question immediately
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        # 6b) Stream the assistant’s response
        def _response_gen():
            # Send the username, not the numeric ID
            prompt = f"For user {username}, {user_input}"
            try:
                result = st.session_state.agent_executor.invoke({"input": prompt})
                answer = result.get("output", "").strip()
            except Exception:
                answer = ""

            # Sanitize any leftover "user with id 'X'" mentions
            pattern = re.compile(r"user with id\s*'?"+re.escape(str(user_id))+"'?")
            answer = pattern.sub(username, answer)

            # Fallback for empty or error-like output
            if not answer or answer.lower().startswith("error") or "syntaxerror" in answer.lower():
                answer = "I’m sorry, I don’t have the information to answer that."

            # Stream word by word
            for token in answer.split(" "):
                yield token + " "
                time.sleep(0.02)

        with st.chat_message("assistant"):
            reply = st.write_stream(_response_gen())

        # 6c) Save the assistant reply
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': reply
        })