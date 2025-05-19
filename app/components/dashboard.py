# components/dashboard.py
import streamlit as st
import pandas as pd
from modules.utils.db.db_utils_mysql import get_user_data_from_mysql
import plotly.express as px

def render_dashboard():
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