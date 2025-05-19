# components/input_data.py
import streamlit as st
import zipfile
import pandas as pd
from modules.utils.cleaner.cleaner import (
    load_csv_from_zip, clean_food_intake,
    clean_sleep_hours, clean_step_count, clean_water_intake
)
from modules.utils.db.db_utils_mysql import push_user_data_mysql
from modules.utils.db.db_utils_neo4j import ingest_user_data_to_neo4j

def render_input_data(DB_URL):
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>📂 Upload & Process Health Data</h1>"
        "<p style='text-align:center; color:gray;'>This will store your Samsung Health data into MySQL & Neo4j.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    uploaded_zip = st.file_uploader("Upload Samsung Health ZIP file", type="zip", help="Exported ZIP from Samsung Health App")
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

    st.markdown("### User Info")
    new_username = st.text_input(
        "👤 Username for this dataset:",
        value="",
        placeholder="e.g. Sundar Pichai",
        help="This will be used to identify your data in the database."
    )

    # Submit button with feedback
    if st.button("Push Data to Databases"):
        if not new_username.strip():
            st.error("❗ Username is required.")
        else:
            user_id = None
            try:
                with st.spinner("Pushing to MySQL..."):
                    user_id = push_user_data_mysql(
                        new_username,
                        df_food_clean,
                        df_water_clean,
                        df_sleep_clean,
                        df_steps_clean,
                        DB_URL
                    )
                    st.success(f"MySQL: Data successfully pushed (user_id={user_id})")

                with st.spinner("Ingesting to Neo4j..."):
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
                    except Exception as neo4j_err:
                        # Rollback MySQL if Neo4j fails
                        from modules.utils.db.db_utils_mysql import delete_user_data_mysql
                        delete_user_data_mysql(user_id)
                        st.error(f"Neo4j ingestion failed. MySQL rollback performed. Error: {neo4j_err}")
            except Exception as mysql_err:
                st.error(f"MySQL push failed: {mysql_err}")



    st.markdown("---")
    st.subheader("Cleaned Data Preview")

    # Show each dataframe in tab layout
    tabs = st.tabs(["Food", "Sleep", "Steps", "Water"])

    with tabs[0]:
        if not df_food_clean.empty:
            st.dataframe(df_food_clean)
        else:
            st.info("No food intake data found.")

    with tabs[1]:
        if not df_sleep_clean.empty:
            st.dataframe(df_sleep_clean)
        else:
            st.info("No sleep data found.")

    with tabs[2]:
        if not df_steps_clean.empty:
            st.dataframe(df_steps_clean)
        else:
            st.info("No step data found.")

    with tabs[3]:
        if not df_water_clean.empty:
            st.dataframe(df_water_clean)
        else:
            st.info("No water intake data found.")
