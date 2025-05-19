# components/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.utils.db.db_utils_mysql import get_user_data_from_mysql

def render_dashboard(db_url: str):
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>📊 User Health Dashboard</h1>",
        unsafe_allow_html=True
    )

    if not st.session_state.user_id:
        st.warning("Please select a user to view the dashboard.")
        st.stop()

    uid   = st.session_state.user_id
    uname = st.session_state.username
    st.markdown(f"<h4 style='text-align:center;'>Welcome, <b>{uname}</b>!</h4>", unsafe_allow_html=True)
    st.markdown("---")

    # Load data
    data     = get_user_data_from_mysql(uid, db_url)
    df_food  = data['food_intake']
    df_sleep = data['sleep_hours']
    df_steps = data['step_count']
    df_water = data['water_intake']

    # Convert event_time/date to datetime.date
    for df_, col in zip([df_food, df_sleep, df_steps, df_water], ['event_time', 'date', 'date', 'event_time']):
        if not df_.empty:
            df_['date'] = pd.to_datetime(df_[col]).dt.date

    # Metric Summary
    st.markdown("### Summary Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Calories", int(df_food['calories'].sum()) if not df_food.empty else 0)
    c2.metric("Avg Sleep (hrs)", round(df_sleep['total_sleep_h'].mean(), 2) if not df_sleep.empty else 0)
    c3.metric("Water Intake (ml)", int(df_water['amount'].sum()) if not df_water.empty else 0)
    c4.metric("Avg Steps/Day", int(df_steps['total_steps'].mean()) if not df_steps.empty else 0)
    st.markdown("---")

    # Tabs
    tab_food, tab_sleep, tab_steps, tab_water = st.tabs(["Food Intake", "Sleep", "Steps", "Water"])

    with tab_food:
        if not df_food.empty:
            st.subheader("Food Intake Insights")
            cal_line = df_food.groupby('date')['calories'].sum().reset_index()
            top_foods = df_food.groupby('food_name')['calories'].sum().reset_index()
            top_foods = top_foods.sort_values('calories', ascending=False).head(5)

            col1, col2 = st.columns(2)
            with col1:
                fig = px.line(cal_line, x='date', y='calories', markers=True,
                              labels={'date': 'Date', 'calories': 'Calories'},
                              title="Daily Calorie Intake")
                fig.update_traces(line_color='firebrick')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig_donut = px.pie(top_foods, values='calories', names='food_name',
                                   hole=0.4, title="Top 5 Food Sources (by Calories)")
                fig_donut.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No food data available.")

    with tab_sleep:
        if not df_sleep.empty:
            st.subheader("Sleep Insights")
            col1, col2 = st.columns(2)
            with col1:
                fig_sleep = px.bar(df_sleep, x='date', y='total_sleep_h',
                                   title="Daily Sleep Duration",
                                   labels={'date': 'Date', 'total_sleep_h': 'Hours Slept'})
                fig_sleep.update_traces(marker_color='indigo')
                st.plotly_chart(fig_sleep, use_container_width=True)
            with col2:
                fig_hist = px.histogram(df_sleep, x='total_sleep_h', nbins=10,
                                        title="Distribution of Sleep Hours",
                                        labels={'total_sleep_h': 'Hours Slept'})
                fig_hist.update_traces(marker_color='indigo')
                st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No sleep data available.")

    with tab_steps:
        if not df_steps.empty:
            st.subheader("Step Activity")
            df_steps['week'] = pd.to_datetime(df_steps['date']).dt.to_period("W").astype(str)
            steps_weekly = df_steps.groupby('week')['total_steps'].mean().reset_index()

            col1, col2 = st.columns(2)
            with col1:
                fig_steps = px.area(df_steps, x='date', y='total_steps',
                                    title="Daily Step Count",
                                    labels={'date': 'Date', 'total_steps': 'Steps'})
                fig_steps.update_traces(line_color='seagreen')
                st.plotly_chart(fig_steps, use_container_width=True)
            with col2:
                fig_week = px.bar(steps_weekly, x='week', y='total_steps',
                                  title="Average Steps per Week",
                                  labels={'week': 'Week', 'total_steps': 'Steps'})
                fig_week.update_traces(marker_color='seagreen')
                st.plotly_chart(fig_week, use_container_width=True)
        else:
            st.info("No step data available.")

    with tab_water:
        if not df_water.empty:
            st.subheader("Water Consumption")
            df_water['week'] = pd.to_datetime(df_water['date']).dt.to_period("W").astype(str)
            water_weekly = df_water.groupby('week')['amount'].sum().reset_index()

            col1, col2 = st.columns(2)
            with col1:
                fig_water = px.bar(df_water, x='date', y='amount',
                                   title="Daily Water Intake",
                                   labels={'date': 'Date', 'amount': 'Water (ml)'})
                fig_water.update_traces(marker_color='royalblue')
                st.plotly_chart(fig_water, use_container_width=True)
            with col2:
                fig_water_week = px.line(water_weekly, x='week', y='amount', markers=True,
                                         title="Weekly Water Consumption",
                                         labels={'week': 'Week', 'amount': 'Water (ml)'})
                fig_water_week.update_traces(line_color='royalblue')
                st.plotly_chart(fig_water_week, use_container_width=True)
        else:
            st.info("No water data available.")
