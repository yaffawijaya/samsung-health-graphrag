#!/usr/bin/env python3
# app.py

import streamlit as st
import time
import pandas as pd
import zipfile
import toml
import plotly.express as px

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

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
cfg_mysql = toml.load('secrets.toml')['mysql']
DB_URL = (
    f"mysql+pymysql://{cfg_mysql['user']}:{cfg_mysql['password']}"
    f"@{cfg_mysql['host']}:{cfg_mysql['port']}/{cfg_mysql['database']}"
)
st.set_page_config(page_title="Samsung Health GraphRAG Explorer", layout="wide")
# st.title("Samsung Health GraphRAG Explorer")

# ─── SESSION STATE DEFAULTS ────────────────────────────────────────────────────
for key, default in [
    ('main_page','home'),
    ('user_id',None),
    ('username',None),
    ('session_id',None),
    ('agent_executor',None),
    ('history_loaded_for',None),
    ('chat_history',[])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── NAVIGATION CALLBACKS ─────────────────────────────────────────────────────

def to_home():          st.session_state.main_page = 'home'
def to_input_user_data(): st.session_state.main_page = 'input_user_data'
def to_user_dashboard():  st.session_state.main_page = 'user_dashboard'
def to_ai_assistant():    st.session_state.main_page = 'ai_assistant'

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Main Menu")
    # create expander for navigation
    st.button("🏠 Home", on_click=to_home)
    with st.expander("Main Features", expanded=True):
        st.button("🤖 AI Assistant", on_click=to_ai_assistant)
        st.button("📊 User Dashboard", on_click=to_user_dashboard)
        st.button("📝 Input Data", on_click=to_input_user_data)

    st.markdown("---")
    st.subheader("Select User")
    try:
        users_df = get_existing_users()
        user_map = {r['username']: r['user_id'] for _, r in users_df.iterrows()}
        user_opts = ['-- Select --'] + list(user_map.keys())
    except Exception as e:
        st.error(f"Error loading users: {e}")
        user_map, user_opts = {}, ['-- Select --']

    sel_user = st.selectbox("User:", user_opts, key="user_select")
    if sel_user != '-- Select --':
        uid = user_map[sel_user]
        with neo4j_driver.session() as session:
            exists = session.run(
                "MATCH (u:User {user_id:$uid}) RETURN count(u) AS c", {'uid': uid}
            ).single()['c']
        if not exists:
            st.error("User not found in Neo4j. Ingest first.")
        else:
            # reset on user switch
            for k in ['session_id','agent_executor','history_loaded_for','chat_history']:
                st.session_state[k] = None
            st.session_state.user_id = uid
            st.session_state.username = sel_user

    # Chat Sessions Section
    if st.session_state.user_id:
        st.markdown("---")
        with st.expander("💬 Chat Sessions", expanded=True):
            sid_df = get_sessions(st.session_state.user_id)
            sid_df = sid_df.sort_values('created_at', ascending=False)
            sess_map = {r['name']: r['session_id'] for _, r in sid_df.iterrows()}
            sess_opts = ['-- Select session --', '+ New Chat'] + list(sess_map.keys())

            # default
            default = '-- Select session --'
            for name, sid in sess_map.items():
                if sid == st.session_state.session_id:
                    default = name
                    break

            choice = st.selectbox(
                "Session:", sess_opts,
                index=sess_opts.index(default),
                key="sess_select"
            )
            if choice == '+ New Chat':
                new_id = create_session(st.session_state.user_id)
                st.session_state.session_id = new_id
                st.rerun()
            elif choice in sess_map:
                st.session_state.session_id = sess_map[choice]

            if st.session_state.session_id:
                new_name = st.text_input("Rename session:", key="rename_session")
                if st.button("Rename", key="rename_btn") and new_name:
                    rename_session(st.session_state.session_id, new_name)
                    st.rerun()
                if st.button("Delete Session", key="del_sess_btn"):
                    delete_session(st.session_state.session_id)
                    for k in ['session_id','chat_history','history_loaded_for']:
                        st.session_state[k] = None
                    st.rerun()

    # Delete User Section
    if st.session_state.user_id:
        st.markdown("---")
        with st.expander("⚠️ Danger Zone: Delete User", expanded=False):
            st.write("**Warning:** This will permanently delete user and all associated data from MySQL and Neo4j.")
            # User must type their username exactly to enable the delete button
            confirm = st.text_input(
                f"Type the exact username (`{st.session_state.username}`) to confirm deletion:",
                key="del_input"
            )
            if confirm == st.session_state.username:
                if st.button("🚨 Delete User Now", key="del_btn", help="This action cannot be undone"):
                    try:
                        # Delete from both MySQL and Neo4j
                        delete_user_data_mysql(st.session_state.user_id)
                        delete_user_data_neo4j(st.session_state.user_id)
                        st.success(f"User '{st.session_state.username}' and all data have been deleted.")
                        # Clear all related state
                        for k in ['user_id','username','session_id','agent_executor','history_loaded_for','chat_history']:
                            st.session_state[k] = None
                    except Exception as e:
                        st.error(f"Failed to delete user: {e}")
            else:
                st.info("Enter the correct username to unlock the delete button.")

    

# ─── PAGE: Home of Author & Project ────────────────────────────────────────────
if st.session_state.main_page == 'home':
    # Heading
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0.25em;'>"
        "Welcome to <span style='color:#4B79A1;'>Samsung Health</span> "
        "<span style='color:#283E51;'>GraphRAG</span>"
        "</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align:center; color:#555;'>"
        "<span style=font-weight:bold;>Capstone Project for Data Science </span>"
        "</h4>"
        "<p style='text-align:center; font-style:italic; color:#555;'>"
        "AI Powered Health Data Analysis"
        "</p>", unsafe_allow_html=True
    )
    st.markdown("---")

    # Meet the Team heading
    st.markdown(
        "<h2 style='text-align:center; color:#4B79A1;'>Meet the Team</h2>",
        unsafe_allow_html=True
    )
    # Display authors with Streamlit image and markdown for names
    authors = [
        ("Yaffazka Afazillah Wijaya", './assets/author_1_yaffa.jpeg'),
        ("Daffa Aqil Shadiq",        './assets/author_2_dapa.png'),
        ("Hasna Aqila R.",           './assets/author_4_hasna.png'),
        ("Hijrah Wira Pratama",      './assets/author_3_hijrah.png')
    ]
    cols = st.columns(len(authors), gap='large')
    for (name, img), col in zip(authors, cols):
        with col:
            st.image(img, width=100)
            st.markdown(
                f"<p style='text-align:center; font-weight:bold;'>{name}</p>",
                unsafe_allow_html=True
            )
    st.markdown("---")

    # Project Poster heading
    st.markdown(
        "<h2 style='text-align:center; color:#4B79A1;'>Project Poster</h2>",
        unsafe_allow_html=True
    )
    # Center poster using columns
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.image('./assets/psd_poster_ai_generated.png', width=300)
    st.markdown("---")

    # GitHub link
    st.markdown(
        "<div style='text-align:center;'>"
        "<a href='https://github.com/yaffawijaya/samsung-health-graphrag' "
        "style='font-size:1.1em; color:#4B79A1; text-decoration:none;'>"
        "🔗 View the project on GitHub</a>"
        "</div>",
        unsafe_allow_html=True
    )

# ─── PAGE: Input User Data ────────────────────────────────────────────────────
if st.session_state.main_page == 'input_user_data':
    st.header("Input User Data")
    uploaded_zip = st.file_uploader("Upload Samsung Health ZIP file", type="zip")
    if not uploaded_zip:
        st.info("Please upload a Samsung Health ZIP file to proceed.")
        st.stop()

    with zipfile.ZipFile(uploaded_zip) as zip_file:
        df_food_raw   = load_csv_from_zip(zip_file, 'com.samsung.health.food_intake')
        df_sleep_raw  = load_csv_from_zip(zip_file, 'com.samsung.shealth.sleep')
        df_steps_raw  = load_csv_from_zip(zip_file, 'com.samsung.shealth.step_daily_trend')
        df_water_raw  = load_csv_from_zip(zip_file, 'com.samsung.health.water_intake')

    df_food_clean   = clean_food_intake(df_food_raw)   if not df_food_raw.empty  else pd.DataFrame()
    df_sleep_clean  = clean_sleep_hours(df_sleep_raw)  if not df_sleep_raw.empty else pd.DataFrame()
    df_steps_clean  = clean_step_count(df_steps_raw)   if not df_steps_raw.empty else pd.DataFrame()
    df_water_clean  = clean_water_intake(df_water_raw) if not df_water_raw.empty else pd.DataFrame()

    # Always start with empty username; require user to type it
    new_username = st.text_input(
        "Username for this dataset:",
        value="",
        placeholder="e.g. Sundar Pichai",
        help="This will be used to identify your data in the database. User id will be auto-generated by increments."
    )

    if st.button("Push Data to Databases"):
        if not new_username.strip():
            st.error("Username is required.")
        else:
            try:
                user_id = push_user_data_mysql(
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
            st.write("Cleaned Food Intake");   st.dataframe(df_food_clean)
        if not df_sleep_clean.empty:
            st.write("Cleaned Sleep Hours");   st.dataframe(df_sleep_clean)
        if not df_steps_clean.empty:
            st.write("Cleaned Step Count");    st.dataframe(df_steps_clean)
        if not df_water_clean.empty:
            st.write("Cleaned Water Intake");  st.dataframe(df_water_clean)



# ─── PAGE: User Dashboard ─────────────────────────────────────────────────────

elif st.session_state.main_page == 'user_dashboard':
    st.header("User Health Dashboard")
    if not st.session_state.user_id:
        st.warning("Select a user first.")
        st.stop()

    uid   = st.session_state.user_id
    uname = st.session_state.username
    st.subheader(f"Dashboard for {uname} (ID {uid})")

    data     = get_user_data_from_mysql(uid)
    df_food  = data['food_intake'];   df_sleep = data['sleep_hours']
    df_steps = data['step_count'];    df_water = data['water_intake']

    for df_, col in zip(
        [df_food, df_sleep, df_steps, df_water],
        ['event_time','date','date','event_time']
    ):
        if not df_.empty:
            df_['date'] = pd.to_datetime(df_[col]).dt.date

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Calories", int(df_food['calories'].sum()) if not df_food.empty else 0)
    c2.metric("Avg Sleep (hrs)", round(df_sleep['total_sleep_h'].mean(),2) if not df_sleep.empty else 0)
    c3.metric("Total Water (ml)", int(df_water['amount'].sum()) if not df_water.empty else 0)
    c4.metric("Avg Steps/Day", int(df_steps['total_steps'].mean()) if not df_steps.empty else 0)

    tabs = st.tabs(["Food","Sleep","Steps","Water"])
    with tabs[0]:
        if not df_food.empty:
            d = df_food.groupby('date')['calories'].sum().reset_index()
            st.plotly_chart(px.line(d,'date','calories'), use_container_width=True)
            st.dataframe(df_food[['date','food_name','amount','calories']])
        else: st.info("No food data.")
    with tabs[1]:
        if not df_sleep.empty:
            st.plotly_chart(px.bar(df_sleep,'date','total_sleep_h'), use_container_width=True)
            st.dataframe(df_sleep)
        else: st.info("No sleep data.")
    with tabs[2]:
        if not df_steps.empty:
            st.plotly_chart(px.line(df_steps,'date','total_steps'), use_container_width=True)
            st.dataframe(df_steps)
        else: st.info("No step data.")
    with tabs[3]:
        if not df_water.empty:
            st.plotly_chart(px.bar(df_water,'date','amount'), use_container_width=True)
            st.dataframe(df_water[['date','amount']])
        else: st.info("No water data.")

# ─── PAGE: AI Assistant ───────────────────────────────────────────────────────

elif st.session_state.main_page == 'ai_assistant':
    st.header("AI Assistant")

    # 1) must have user
    if not st.session_state.user_id:
        st.warning("Select a user first.")
        st.stop()

    # 2) must have session
    if not st.session_state.session_id:
        st.warning("Select or create a Chat Session in the sidebar first.")
        st.stop()

    sid   = st.session_state.session_id
    uname = st.session_state.username

    # 3) init agent once
    if st.session_state.agent_executor is None:
        st.session_state.agent_executor = get_graphrag_agent()
    agent = st.session_state.agent_executor

    # 4) load chat history once per session
    if st.session_state.history_loaded_for != sid:
        hist = get_chat_history(sid)
        st.session_state.chat_history = [
            {"role": row.role, "content": row.message}
            for row in hist.itertuples()
        ]
        st.session_state.history_loaded_for = sid

    # 5) render all prior messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 6) new user input & response
    user_q = st.chat_input("Ask a question about your health data:")
    if user_q:
        with st.chat_message("user"):
            st.write(user_q)
        push_chat_message(sid, "user", user_q)
        st.session_state.chat_history.append({"role":"user","content":user_q})

        # generate full answer
        prompt = f"For user {uname}, {user_q}"
        try:
            res = agent.invoke({"input": prompt})
            ans = res.get("output","").strip() if res else ""
        except Exception:
            ans = "I’m sorry, I don’t have the information to answer that."

        # stream answer & accumulate
        reply_text = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for token in ans.split():
                reply_text += token + " "
                placeholder.write(reply_text)
                time.sleep(0.02)

        # save assistant reply
        push_chat_message(sid, "assistant", reply_text)
        st.session_state.chat_history.append({"role":"assistant","content":reply_text})
