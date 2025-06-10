# components/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from modules.utils.db.db_utils_mysql import get_user_data_from_mysql
from components.export_report import render_export_section  # Import the optimized function

def calculate_health_score(df_food, df_sleep, df_steps, df_water):
    """Calculate an overall health score based on all metrics"""
    scores = {}

    # Sleep score (0-25 points)
    if not df_sleep.empty:
        avg_sleep = df_sleep['total_sleep_h'].mean()
        consistency = df_sleep['total_sleep_h'].std()

        if 7 <= avg_sleep <= 9:
            sleep_score = 20
        elif 6.5 <= avg_sleep < 7 or 9 < avg_sleep <= 9.5:
            sleep_score = 15
        else:
            sleep_score = 10

        if consistency < 1.5:
            sleep_score += 5
        elif consistency < 2.5:
            sleep_score += 3
        else:
            sleep_score += 1

        scores['sleep'] = min(sleep_score, 25)
    else:
        scores['sleep'] = 0

    # Activity score (0-25 points)
    if not df_steps.empty:
        avg_steps = df_steps['total_steps'].mean()

        if avg_steps >= 10000:
            scores['activity'] = 25
        elif avg_steps >= 8000:
            scores['activity'] = 20
        elif avg_steps >= 6000:
            scores['activity'] = 15
        elif avg_steps >= 4000:
            scores['activity'] = 10
        else:
            scores['activity'] = 5
    else:
        scores['activity'] = 0

    # Hydration score (0-25 points)
    if not df_water.empty:
        avg_water = df_water['amount'].mean()

        if avg_water >= 2000:
            scores['hydration'] = 25
        elif avg_water >= 1500:
            scores['hydration'] = 20
        elif avg_water >= 1000:
            scores['hydration'] = 15
        else:
            scores['hydration'] = 10
    else:
        scores['hydration'] = 0

    # Nutrition score (0-25 points) - simplified
    if not df_food.empty:
        daily_calories = df_food.groupby('date')['calories'].sum()
        avg_calories = daily_calories.mean()
        food_variety = len(df_food['food_name'].unique())

        calorie_score = 15 if 1500 <= avg_calories <= 2500 else 10
        variety_score = min(food_variety, 10)

        scores['nutrition'] = calorie_score + variety_score
    else:
        scores['nutrition'] = 0

    total_score = sum(scores.values())
    return total_score, scores

def create_trend_analysis(df, date_col, value_col, title):
    """Create trend analysis with moving averages"""
    if df.empty:
        return None

    df_sorted = df.sort_values(date_col)

    # Calculate 7-day moving average
    df_sorted['7_day_avg'] = df_sorted[value_col].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    # Add actual data
    fig.add_trace(go.Scatter(
        x=df_sorted[date_col],
        y=df_sorted[value_col],
        mode='markers+lines',
        name='Daily Values',
        line=dict(color='lightblue', width=1),
        marker=dict(size=4)
    ))

    # Add trend line
    fig.add_trace(go.Scatter(
        x=df_sorted[date_col],
        y=df_sorted['7_day_avg'],
        mode='lines',
        name='7-Day Average',
        line=dict(color='darkblue', width=3)
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=value_col.replace('_', ' ').title(),
        hovermode='x unified',
        showlegend=True,
        height=400  # Standardized height for export
    )

    return fig

def create_correlation_heatmap(df_food, df_sleep, df_steps, df_water):
    """Create correlation heatmap between different health metrics"""

    # Prepare data for correlation
    correlation_data = pd.DataFrame()

    if not df_sleep.empty:
        sleep_daily = df_sleep.groupby('date')['total_sleep_h'].mean().reset_index()
        sleep_daily.columns = ['date', 'sleep_hours']
        correlation_data = sleep_daily

    if not df_steps.empty:
        steps_daily = df_steps.groupby('date')['total_steps'].mean().reset_index()
        steps_daily.columns = ['date', 'daily_steps']
        if correlation_data.empty:
            correlation_data = steps_daily
        else:
            correlation_data = pd.merge(correlation_data, steps_daily, on='date', how='outer')

    if not df_water.empty:
        water_daily = df_water.groupby('date')['amount'].sum().reset_index()
        water_daily.columns = ['date', 'water_intake']
        if correlation_data.empty:
            correlation_data = water_daily
        else:
            correlation_data = pd.merge(correlation_data, water_daily, on='date', how='outer')

    if not df_food.empty:
        food_daily = df_food.groupby('date')['calories'].sum().reset_index()
        food_daily.columns = ['date', 'daily_calories']
        if correlation_data.empty:
            correlation_data = food_daily
        else:
            correlation_data = pd.merge(correlation_data, food_daily, on='date', how='outer')

    if len(correlation_data.columns) > 2:  # At least 2 metrics + date
        corr_matrix = correlation_data.drop('date', axis=1).corr()

        fig = px.imshow(
            corr_matrix,
            title="Health Metrics Correlation",
            color_continuous_scale='RdBu',
            aspect='auto',
            height=400  # Standardized height
        )
        return fig

    return None

def create_weekly_pattern_analysis(df, date_col, value_col, title):
    """Analyze weekly patterns"""
    if df.empty:
        return None

    df_copy = df.copy()
    df_copy['weekday'] = pd.to_datetime(df_copy[date_col]).dt.day_name()
    df_copy['week_num'] = pd.to_datetime(df_copy[date_col]).dt.isocalendar().week

    weekday_avg = df_copy.groupby('weekday')[value_col].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])

    fig = px.bar(
        x=weekday_avg.index,
        y=weekday_avg.values,
        title=f"{title} - Weekly Pattern",
        labels={'x': 'Day of Week', 'y': value_col.replace('_', ' ').title()},
        height=400  # Standardized height
    )

    return fig

def render_dashboard(db_url: str):
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>📊 Advanced Health Dashboard</h1>",
        unsafe_allow_html=True
    )

    if not st.session_state.user_id:
        st.warning("Please select a user to view the dashboard.")
        st.stop()

    uid = st.session_state.user_id
    uname = st.session_state.username
    st.markdown(f"<h3 style='text-align:center;'>Health Analytics for <b>{uname}</b></h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Load data
    data = get_user_data_from_mysql(uid, db_url)
    df_food = data['food_intake']
    df_sleep = data['sleep_hours']
    df_steps = data['step_count']
    df_water = data['water_intake']

    # Convert date columns
    for df_, col in zip([df_food, df_sleep, df_steps, df_water], ['event_time', 'date', 'date', 'event_time']):
        if not df_.empty and col in df_.columns:
            df_['date'] = pd.to_datetime(df_[col]).dt.date

    # Calculate health score
    total_score, score_breakdown = calculate_health_score(df_food, df_sleep, df_steps, df_water)

    # Optimized: Only store essential figures for export
    essential_figures = {}

    # Health Score Section
    st.markdown("### 🎯 Overall Health Score")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Overall Score",
            f"{total_score}/100",
            delta=f"{total_score-75}" if total_score > 75 else f"{total_score-75}",
            help="Combined health score based on all metrics. 75+ is good, 90+ is excellent. Calculated from sleep quality (25pts), activity level (25pts), hydration (25pts), and nutrition variety (25pts)."
        )

    with col2:
        st.metric(
            "Sleep Score",
            f"{score_breakdown.get('sleep', 0)}/25",
            help="Sleep quality score based on: Average hours (7-9h ideal = 20pts) + Consistency (low variation = 5pts). Good sleep is crucial for recovery, immune function, and mental health."
        )

    with col3:
        st.metric(
            "Activity Score",
            f"{score_breakdown.get('activity', 0)}/25",
            help="Activity level based on daily steps: 10,000+ steps = 25pts, 8,000+ = 20pts, 6,000+ = 15pts. Regular activity reduces disease risk and improves cardiovascular health."
        )

    with col4:
        st.metric(
            "Hydration Score",
            f"{score_breakdown.get('hydration', 0)}/25",
            help="Hydration level based on daily water intake: 2L+ = 25pts, 1.5L+ = 20pts. Proper hydration supports kidney function, temperature regulation, and nutrient transport."
        )

    with col5:
        st.metric(
            "Nutrition Score",
            f"{score_breakdown.get('nutrition', 0)}/25",
            help="Nutrition score based on calorie balance (1500-2500 daily = 15pts) + food variety (more types = up to 10pts). Balanced nutrition provides essential nutrients for optimal body function."
        )

    # Health score gauge (Essential for export)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Health Score"},
        delta = {'reference': 75},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig_gauge.update_layout(height=300)
    essential_figures["health_score_gauge"] = fig_gauge

    # Add expander with gauge explanation
    with st.expander("ℹ️ Understanding Your Health Score"):
        st.markdown("""
        **Health Score Ranges:**
        - 🔴 **0-50**: Needs Improvement - Focus on basic health habits
        - 🟡 **50-75**: Fair - Good foundation, room for optimization
        - 🟢 **75-90**: Good - Maintaining healthy lifestyle well
        - 🏆 **90-100**: Excellent - Optimal health habits across all areas

        **Calculation Method:**
        - Sleep Quality: 25 points (7-9 hours + consistency)
        - Activity Level: 25 points (based on daily steps)
        - Hydration: 25 points (daily water intake)
        - Nutrition: 25 points (calorie balance + food variety)

        The red threshold line at 90 represents the 'excellent' benchmark.
        """)

    st.plotly_chart(fig_gauge, use_container_width=True, key="health_score_gauge_display")

    # Summary metrics with improvements
    st.markdown("### 📈 Key Metrics Summary")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if not df_food.empty:
            total_cal = int(df_food['calories'].sum())
            avg_cal = int(df_food.groupby('date')['calories'].sum().mean())
            st.metric(
                "Daily Avg Calories",
                avg_cal,
                delta=f"Total: {total_cal}",
                help="Average daily calorie intake. Healthy range: 1,500-2,500 calories/day depending on age, gender, and activity level. Total calories show your overall tracking period."
            )
        else:
            st.metric("Daily Avg Calories", "No data", help="Upload food intake data to see calorie analysis")

    with c2:
        if not df_sleep.empty:
            avg_sleep = round(df_sleep['total_sleep_h'].mean(), 1)
            consistency = round(df_sleep['total_sleep_h'].std(), 1)
            st.metric(
                "Avg Sleep (hrs)",
                avg_sleep,
                delta=f"Consistency: ±{consistency}h",
                help="Average nightly sleep duration. Optimal: 7-9 hours for adults. Consistency shows sleep schedule regularity - lower values indicate more consistent bedtimes."
            )
        else:
            st.metric("Avg Sleep (hrs)", "No data", help="Upload sleep data to see sleep pattern analysis")

    with c3:
        if not df_water.empty:
            total_water = int(df_water['amount'].sum())
            avg_water = int(df_water.groupby('date')['amount'].sum().mean()) if 'date' in df_water.columns else int(df_water['amount'].mean())
            st.metric(
                "Daily Avg Water (ml)",
                avg_water,
                delta=f"Total: {total_water}ml",
                help="Average daily water intake. Recommended: 2,000ml (2 liters) per day for optimal hydration. Adjust for exercise, climate, and individual needs."
            )
        else:
            st.metric("Daily Avg Water (ml)", "No data", help="Upload water intake data to see hydration analysis")

    with c4:
        if not df_steps.empty:
            avg_steps = int(df_steps['total_steps'].mean())
            max_steps = int(df_steps['total_steps'].max())
            st.metric(
                "Avg Steps/Day",
                f"{avg_steps:,}",
                delta=f"Peak: {max_steps:,}",
                help="Average daily step count. Health targets: 8,000+ steps for health benefits, 10,000+ for fitness. Peak day shows your maximum recorded activity."
            )
        else:
            st.metric("Avg Steps/Day", "No data", help="Upload step count data to see activity analysis")

    st.markdown("---")

    # Advanced Analytics Tabs
    tab_trends, tab_patterns, tab_correlations, tab_detailed = st.tabs([
        "📈 Trends", "📅 Weekly Patterns", "🔗 Correlations", "📋 Detailed Analysis"
    ])

    with tab_trends:
        st.markdown("### Trend Analysis with Moving Averages")

        with st.expander("ℹ️ Understanding Trend Analysis"):
            st.markdown("""
            **What This Shows:**
            - **Light blue dots/lines**: Your actual daily values
            - **Dark blue line**: 7-day moving average (smoothed trend)
            - **Trend direction**: Shows if you're improving, declining, or stable over time

            **How to Use It:**
            - Look for **upward trends** in positive metrics (steps, water, good sleep)
            - Watch for **downward trends** that might need attention
            - **Flat trends** indicate consistency (good for sleep, may need improvement for activity)
            - Use trends to set goals and track progress over weeks/months
            """)

        col1, col2 = st.columns(2)

        with col1:
            if not df_sleep.empty:
                sleep_trend = create_trend_analysis(df_sleep, 'date', 'total_sleep_h', 'Sleep Duration Trend')
                if sleep_trend:
                    st.plotly_chart(sleep_trend, use_container_width=True, key="sleep_trend_chart_display")
                    st.caption("💤 Track sleep consistency and identify patterns in your sleep duration over time.")
                    essential_figures["sleep_trend_chart"] = sleep_trend  # Essential for export

            if not df_water.empty:
                water_daily = df_water.groupby('date')['amount'].sum().reset_index()
                water_trend = create_trend_analysis(water_daily, 'date', 'amount', 'Daily Water Intake Trend')
                if water_trend:
                    st.plotly_chart(water_trend, use_container_width=True, key="water_trend_chart_display")
                    st.caption("💧 Monitor hydration habits and see if you're maintaining consistent water intake.")

        with col2:
            if not df_steps.empty:
                steps_trend = create_trend_analysis(df_steps, 'date', 'total_steps', 'Daily Steps Trend')
                if steps_trend:
                    st.plotly_chart(steps_trend, use_container_width=True, key="steps_trend_chart_display")
                    st.caption("🚶 Visualize activity levels and identify periods of increased or decreased movement.")
                    essential_figures["steps_trend_chart"] = steps_trend  # Essential for export

            if not df_food.empty:
                food_daily = df_food.groupby('date')['calories'].sum().reset_index()
                food_trend = create_trend_analysis(food_daily, 'date', 'calories', 'Daily Calories Trend')
                if food_trend:
                    st.plotly_chart(food_trend, use_container_width=True, key="food_trend_chart_display")
                    st.caption("🍽️ Track eating patterns and caloric intake trends to maintain balanced nutrition.")

    with tab_patterns:
        st.markdown("### Weekly Pattern Analysis")

        with st.expander("ℹ️ Understanding Weekly Patterns"):
            st.markdown("""
            **What This Shows:**
            - Average values for each day of the week across your entire tracking period
            - Helps identify behavioral patterns (weekday vs weekend differences)

            **Common Patterns to Look For:**
            - **Sleep**: Often more on weekends, less consistent Friday/Saturday nights
            - **Activity**: May drop on weekends or specific days (rest days)
            - **Water**: Often lower on busy workdays or weekends
            - **Calories**: May spike on weekends or social days

            **How to Use It:**
            - Identify your "weak days" that need attention
            - Plan strategies for days with consistently poor metrics
            - Recognize patterns to build better habits
            """)

        col1, col2 = st.columns(2)

        with col1:
            if not df_sleep.empty:
                sleep_pattern = create_weekly_pattern_analysis(df_sleep, 'date', 'total_sleep_h', 'Sleep')
                if sleep_pattern:
                    st.plotly_chart(sleep_pattern, use_container_width=True, key="sleep_pattern_chart_display")
                    st.caption("😴 See which days you sleep best/worst. Plan consistent bedtimes for low-sleep days.")

            if not df_steps.empty:
                steps_pattern = create_weekly_pattern_analysis(df_steps, 'date', 'total_steps', 'Steps')
                if steps_pattern:
                    st.plotly_chart(steps_pattern, use_container_width=True, key="steps_pattern_chart_display")
                    st.caption("🏃 Identify low-activity days. Schedule workouts or walks on these days.")

        with col2:
            if not df_water.empty:
                water_daily = df_water.groupby('date')['amount'].sum().reset_index()
                water_pattern = create_weekly_pattern_analysis(water_daily, 'date', 'amount', 'Water Intake')
                if water_pattern:
                    st.plotly_chart(water_pattern, use_container_width=True, key="water_pattern_chart_display")
                    st.caption("💦 Track hydration patterns. Set reminders for low-water days.")

            if not df_food.empty:
                food_daily = df_food.groupby('date')['calories'].sum().reset_index()
                food_pattern = create_weekly_pattern_analysis(food_daily, 'date', 'calories', 'Calorie Intake')
                if food_pattern:
                    st.plotly_chart(food_pattern, use_container_width=True, key="food_pattern_chart_display")
                    st.caption("🍕 Monitor eating patterns. Plan healthier options for high-calorie days.")

    with tab_correlations:
        st.markdown("### Health Metrics Correlations")

        with st.expander("ℹ️ Understanding Correlations"):
            st.markdown("""
            **What Correlations Tell You:**
            - **Positive correlation (blue, +0.3 to +1.0)**: When one goes up, the other tends to go up
            - **Negative correlation (red, -0.3 to -1.0)**: When one goes up, the other tends to go down
            - **No correlation (white, -0.3 to +0.3)**: No clear relationship between the metrics

            **Interesting Correlations to Look For:**
            - **Sleep ↔ Activity**: Good sleep often leads to more activity next day
            - **Water ↔ Activity**: Higher activity days may correlate with better hydration
            - **Sleep ↔ Calories**: Poor sleep might lead to higher calorie intake
            - **Activity ↔ Sleep**: More active days might improve sleep quality

            **Strength Levels:**
            - **0.7-1.0**: Very strong relationship
            - **0.5-0.7**: Moderate relationship
            - **0.3-0.5**: Weak relationship
            - **0.0-0.3**: Little to no relationship
            """)

        correlation_fig = create_correlation_heatmap(df_food, df_sleep, df_steps, df_water)
        if correlation_fig:
            st.plotly_chart(correlation_fig, use_container_width=True, key="correlation_heatmap_display")
            st.caption("🔗 Discover how your health metrics influence each other. Strong correlations can help you optimize one area to improve another.")
            essential_figures["correlation_heatmap"] = correlation_fig  # Essential for export

            st.markdown("""
            **💡 How to Use Correlation Insights:**
            - If sleep and activity are positively correlated: prioritize good sleep to boost next-day energy
            - If water and steps are correlated: increase hydration on active days
            - If sleep and calories are negatively correlated: focus on sleep quality to avoid overeating
            - Strong correlations suggest you can improve multiple areas by focusing on one key habit
            """)
        else:
            st.info("Need at least 2 health metrics with data to show correlations.")
            st.markdown("""
            **🔍 What You'll See Here:**
            Once you have data for multiple metrics, this heatmap will show:
            - Color-coded relationships between your health behaviors
            - Numerical correlation values (-1 to +1)
            - Interactive tooltips with detailed explanations
            """)

    with tab_detailed:
        st.markdown("### Detailed Data Analysis")

        with st.expander("ℹ️ Understanding Detailed Analysis Charts"):
            st.markdown("""
            **Chart Types Explained:**

            **📊 Histograms/Distributions**: Show how often different values occur
            - **Peaks**: Most common values in your data
            - **Spread**: How varied your habits are
            - **Skew**: If you tend toward higher or lower values

            **📦 Box Plots**: Show data distribution and outliers
            - **Box**: Contains 50% of your data (middle range)
            - **Line in box**: Your median (middle value)
            - **Whiskers**: Normal range of variation
            - **Dots outside**: Unusual days (outliers)

            **🥧 Pie Charts**: Show proportional breakdown of categories
            - **Larger slices**: More common behaviors/patterns
            - **Smaller slices**: Less frequent occurrences
            - **Colors**: Different categories for easy comparison
            """)

        # Detailed analysis for each metric (displayed but not stored for export to save memory)
        if not df_food.empty:
            st.subheader("🍎 Food Intake Analysis")

            col1, col2 = st.columns(2)

            with col1:
                daily_calories = df_food.groupby('date')['calories'].sum()
                fig_cal_dist = px.histogram(
                    daily_calories,
                    title="Daily Calorie Distribution",
                    labels={'value': 'Calories', 'count': 'Number of Days'}
                )
                st.plotly_chart(fig_cal_dist, use_container_width=True, key="food_cal_dist_display")
                st.caption("📈 Shows how often you hit different calorie levels. Look for consistency around healthy ranges (1,500-2,500).")

            with col2:
                top_foods = df_food.groupby('food_name')['calories'].sum().head(8)
                fig_foods = px.pie(
                    values=top_foods.values,
                    names=top_foods.index,
                    title="Top Food Sources (by Calories)"
                )
                st.plotly_chart(fig_foods, use_container_width=True, key="top_foods_pie_display")
                st.caption("🥘 Identifies your main calorie sources. Large slices might need attention if they're less healthy foods.")

        if not df_sleep.empty:
            st.subheader("😴 Sleep Analysis")

            col1, col2 = st.columns(2)

            with col1:
                fig_sleep_box = px.box(
                    df_sleep,
                    y='total_sleep_h',
                    title="Sleep Duration Distribution"
                )
                st.plotly_chart(fig_sleep_box, use_container_width=True, key="sleep_duration_box_display")
                st.caption("📦 Box plot shows sleep consistency. Tight box = consistent sleep, dots outside = unusual nights needing attention.")

            with col2:
                df_sleep_copy = df_sleep.copy()
                df_sleep_copy['sleep_quality'] = pd.cut(
                    df_sleep_copy['total_sleep_h'],
                    bins=[0, 6, 7, 9, 24],
                    labels=['Poor (<6h)', 'Fair (6-7h)', 'Good (7-9h)', 'Excessive (>9h)']
                )
                quality_counts = df_sleep_copy['sleep_quality'].value_counts()

                fig_quality = px.bar(
                    x=quality_counts.index,
                    y=quality_counts.values,
                    title="Sleep Quality Distribution"
                )
                st.plotly_chart(fig_quality, use_container_width=True, key="sleep_quality_bar_display")
                st.caption("💤 Categorizes your sleep into quality levels. Aim for more nights in the 'Good' category.")

        if not df_steps.empty:
            st.subheader("🚶 Activity Analysis")

            col1, col2 = st.columns(2)

            with col1:
                fig_steps_hist = px.histogram(
                    df_steps,
                    x='total_steps',
                    title="Daily Steps Distribution",
                    labels={'total_steps': 'Steps', 'count': 'Number of Days'}
                )
                st.plotly_chart(fig_steps_hist, use_container_width=True, key="steps_dist_hist_display")
                st.caption("👟 Shows your typical activity levels. Look for peaks around 8,000-10,000+ steps for optimal health.")

            with col2:
                df_steps_copy = df_steps.copy()
                df_steps_copy['activity_level'] = pd.cut(
                    df_steps_copy['total_steps'],
                    bins=[0, 5000, 8000, 12000, float('inf')],
                    labels=['Sedentary', 'Lightly Active', 'Active', 'Very Active']
                )
                activity_counts = df_steps_copy['activity_level'].value_counts()

                fig_activity = px.pie(
                    values=activity_counts.values,
                    names=activity_counts.index,
                    title="Activity Level Distribution"
                )
                st.plotly_chart(fig_activity, use_container_width=True, key="activity_level_pie_display")
                st.caption("🏃 Breaks down your activity patterns. Aim for larger 'Active' and 'Very Active' slices.")

        if not df_water.empty:
            st.subheader("💧 Hydration Analysis")

            col1, col2 = st.columns(2)

            with col1:
                daily_water = df_water.groupby('date')['amount'].sum()
                fig_water_dist = px.histogram(
                    daily_water,
                    title="Daily Water Intake Distribution",
                    labels={'value': 'Water Intake (ml)', 'count': 'Number of Days'}
                )
                st.plotly_chart(fig_water_dist, use_container_width=True, key="water_intake_dist_display")
                st.caption("📊 Shows how consistently you hit your water intake goals. Aim for a peak around 2000ml.")

            with col2:
                fig_water_line = px.line(
                    df_water.groupby('date')['amount'].sum().reset_index(),
                    x='date',
                    y='amount',
                    title="Daily Water Intake Over Time"
                )
                st.plotly_chart(fig_water_line, use_container_width=True, key="water_intake_line_display")
                st.caption("🗓️ Track your daily water consumption trends to ensure consistent hydration.")

    # Health Insights Section
    st.markdown("---")
    st.markdown("### 💡 Health Insights & Recommendations")

    with st.expander("ℹ️ Understanding Your Health Insights"):
        st.markdown("""
        **How Insights Are Generated:**
        - **Evidence-based recommendations** using established health guidelines
        - **Personalized analysis** based on your specific data patterns
        - **Actionable advice** you can implement immediately

        **Health Guidelines Used:**
        - **Sleep**: 7-9 hours for adults, consistent schedule important
        - **Activity**: 8,000+ steps daily, 10,000+ for fitness goals
        - **Hydration**: 2L (2000ml) daily minimum, more if active
        - **Nutrition**: Balanced calories (1,500-2,500), food variety important

        **Types of Insights:**
        - 🎯 **Goal-oriented**: Specific targets to aim for
        - ⚠️ **Risk alerts**: Patterns that may need attention
        - 🌟 **Positive reinforcement**: Celebrating your successes
        - 📊 **Pattern recognition**: Behavioral trends identified
        """)

    insights = []

    # Sleep insights
    if not df_sleep.empty:
        avg_sleep = df_sleep['total_sleep_h'].mean()
        consistency = df_sleep['total_sleep_h'].std()

        if avg_sleep < 7:
            insights.append("🛌 **Sleep Duration**: Try to get more sleep - aim for 7-9 hours per night. Consider setting a consistent bedtime routine.")
        elif avg_sleep > 9:
            insights.append("🛌 **Sleep Duration**: You might be oversleeping - consider if there are underlying factors like stress or health issues to address.")
        else:
            insights.append("🛌 **Sleep Duration**: Great job maintaining good sleep duration! You're in the optimal 7-9 hour range.")

        if consistency > 2:
            insights.append("⏰ **Sleep Consistency**: Try to maintain a more regular sleep schedule. Consistent bedtimes help regulate your circadian rhythm.")
        elif consistency < 1:
            insights.append("⏰ **Sleep Consistency**: Excellent sleep consistency! Your regular schedule is supporting quality rest.")

    # Activity insights
    if not df_steps.empty:
        avg_steps = df_steps['total_steps'].mean()
        max_steps = df_steps['total_steps'].max()
        min_steps = df_steps['total_steps'].min()

        if avg_steps < 5000:
            insights.append("🚶 **Activity Level**: Consider increasing daily movement. Start with a goal of 6,000 steps and gradually work up to 8,000+.")
        elif avg_steps < 8000:
            insights.append("🚶 **Activity Level**: You're moderately active! Aim for 8,000+ steps daily for significant health benefits.")
        elif avg_steps < 10000:
            insights.append("🚶 **Activity Level**: Great activity level! You're meeting health guidelines. Consider 10,000+ steps for fitness goals.")
        else:
            insights.append("🚶 **Activity Level**: Outstanding! You're exceeding fitness recommendations and maintaining an active lifestyle.")

        if max_steps > avg_steps * 2:
            insights.append("📊 **Activity Variation**: You have some very active days! Try to maintain more consistent activity levels throughout the week.")

    # Hydration insights
    if not df_water.empty:
        if 'date' in df_water.columns:
            avg_water = df_water.groupby('date')['amount'].sum().mean()
        else:
            avg_water = df_water['amount'].mean()

        if avg_water < 1500:
            insights.append("💧 **Hydration**: Significantly increase water intake. Aim for at least 2L daily. Set hourly reminders to build the habit.")
        elif avg_water < 2000:
            insights.append("💧 **Hydration**: You're close to optimal hydration! Try to reach 2L daily - add one more glass with meals.")
        else:
            insights.append("💧 **Hydration**: Excellent hydration habits! You're meeting or exceeding the 2L daily recommendation.")

    # Nutrition insights
    if not df_food.empty:
        food_variety = len(df_food['food_name'].unique())
        daily_avg_cal = df_food.groupby('date')['calories'].sum().mean()

        if food_variety < 5:
            insights.append("🍎 **Food Variety**: Try to add more variety to your diet. Aim for different food groups: fruits, vegetables, proteins, grains.")
        elif food_variety < 10:
            insights.append("🍎 **Food Variety**: Good food variety! Consider adding more colorful fruits and vegetables for additional nutrients.")
        else:
            insights.append("🍎 **Food Variety**: Excellent dietary diversity! You're eating a wide range of foods, which supports balanced nutrition.")

        if daily_avg_cal < 1200:
            insights.append("🍽️ **Calorie Intake**: Your calorie intake seems very low. Consider consulting a healthcare provider to ensure you're meeting your energy needs.")
        elif daily_avg_cal < 1500:
            insights.append("🍽️ **Calorie Intake**: Consider if you're eating enough to meet your energy needs, especially if you're active.")
        elif daily_avg_cal > 2800:
            insights.append("🍽️ **Calorie Intake**: Your calorie intake is quite high. Consider portion control and choosing more nutrient-dense foods.")

    # Display insights
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")

        st.markdown("""
        ---
        **💪 Action Steps:**
        1. **Pick one insight** to focus on this week
        2. **Set a specific goal** (e.g., "drink 2L water daily")
        3. **Track your progress** using the dashboard
        4. **Celebrate small wins** - every improvement matters!

        Remember: Sustainable health changes happen gradually. Focus on building one habit at a time! 🌟
        """)
    else:
        st.info("Upload more health data to get personalized insights and recommendations!")
        st.markdown("""
        **🔍 Coming Soon:**
        Once you upload your health data, you'll see:
        - Personalized recommendations based on your patterns
        - Specific, actionable goals tailored to your needs
        - Celebration of your health achievements
        - Evidence-based advice for improvement areas
        """)

    # Call the optimized export section with only essential figures
    render_export_section(df_food, df_sleep, df_steps, df_water, total_score, score_breakdown, insights, uname, essential_figures)