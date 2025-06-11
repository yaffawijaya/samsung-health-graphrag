import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio # Import plotly.io for image export
from datetime import datetime
import base64 # For encoding images into base64
import json # Only needed if json.dumps is used, not directly used in the provided Claude snippets but good to keep if in original context

def _plotly_fig_to_base64_img(fig, key):
    """
    Converts a Plotly figure to a base64 encoded PNG image.
    Includes error handling for kaleido.
    """
    try:
        # Use kaleido to convert figure to PNG bytes
        # Increased scale for better resolution, you can adjust this if still too slow
        img_bytes = pio.to_image(fig, format="png", width=700, height=450, scale=1.5)
        # Encode bytes to base64 string
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        st.error(f"Error converting Plotly figure '{key}' to image: {e}")
        # Placeholder for broken image or a small transparent image if conversion fails
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# ===============================
# SOLUTION 1: TEXT-ONLY REPORT (FASTEST) - Integrated from Claude
# ===============================

def generate_text_only_report(df_food, df_sleep, df_steps, df_water, total_score, score_breakdown, insights, username):
    """
    Generate a text-only HTML report with NO charts - lightning fast!
    Uses CSS to create visual elements instead of charts.
    """

    # Calculate summary stats
    stats = {}

    if not df_sleep.empty:
        stats['sleep'] = {
            'avg': round(df_sleep['total_sleep_h'].mean(), 1),
            'min': round(df_sleep['total_sleep_h'].min(), 1),
            'max': round(df_sleep['total_sleep_h'].max(), 1),
            'consistency': round(df_sleep['total_sleep_h'].std(), 1),
            'nights': len(df_sleep)
        }

    if not df_steps.empty:
        stats['steps'] = {
            'avg': int(df_steps['total_steps'].mean()),
            'min': int(df_steps['total_steps'].min()),
            'max': int(df_steps['total_steps'].max()),
            'total': int(df_steps['total_steps'].sum()),
            'days': len(df_steps)
        }

    if not df_water.empty:
        if 'date' in df_water.columns:
            daily_water = df_water.groupby('date')['amount'].sum()
            stats['water'] = {
                'avg': int(daily_water.mean()),
                'total': int(df_water['amount'].sum()),
                'days': len(daily_water)
            }
        else:
            stats['water'] = {
                'avg': int(df_water['amount'].mean()),
                'total': int(df_water['amount'].sum()),
                'days': len(df_water)
            }

    if not df_food.empty:
        daily_calories = df_food.groupby('date')['calories'].sum()
        top_foods = df_food.groupby('food_name')['calories'].sum().head(5)
        stats['food'] = {
            'avg_daily': int(daily_calories.mean()),
            'total': int(df_food['calories'].sum()),
            'variety': len(df_food['food_name'].unique()),
            'days': len(daily_calories),
            'top_foods': list(top_foods.index)
        }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Health Report - {username}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                background: white;
                font-size: 14px;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}

            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 3px solid #3498db;
                padding-bottom: 20px;
            }}

            .header h1 {{
                color: #3498db;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}

            .score-display {{
                background: linear-gradient(135deg, #74b9ff, #0984e3);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin: 20px 0;
            }}

            .score-main {{
                font-size: 4em;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            .score-breakdown {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-top: 20px;
            }}

            .score-item {{
                background: rgba(255,255,255,0.2);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }}

            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}

            .metric-card {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 25px;
                text-align: center;
            }}

            .metric-card h3 {{
                color: #3498db;
                margin-bottom: 15px;
                font-size: 1.3em;
            }}

            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }}

            .metric-details {{
                color: #7f8c8d;
                font-size: 0.9em;
                line-height: 1.4;
            }}

            .progress-bar {{
                background: #ecf0f1;
                height: 20px;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }}

            .progress-fill {{
                height: 100%;
                border-radius: 10px;
                transition: width 0.3s ease;
            }}

            .progress-fill.excellent {{ background: #27ae60; }}
            .progress-fill.good {{ background: #f39c12; }}
            .progress-fill.fair {{ background: #e74c3c; }}

            .insights {{
                background: #f8fffe;
                border-left: 5px solid #00b894;
                padding: 25px;
                margin: 30px 0;
                border-radius: 0 10px 10px 0;
            }}

            .insights h2 {{
                color: #00b894;
                margin-bottom: 20px;
            }}

            .insights ul {{
                list-style: none;
            }}

            .insights li {{
                background: white;
                margin: 10px 0;
                padding: 15px;
                border-radius: 8px;
                border-left: 3px solid #00b894;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}

            .data-summary {{
                margin: 30px 0;
            }}

            .data-summary h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}

            .data-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #ecf0f1;
            }}

            .data-label {{
                font-weight: 600;
                color: #34495e;
            }}

            .data-value {{
                color: #3498db;
                font-weight: bold;
            }}

            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                text-align: center;
                color: #7f8c8d;
            }}

            @media print {{
                body {{ margin: 0; padding: 10px; }}
                .score-display {{
                    background: #3498db !important;
                    -webkit-print-color-adjust: exact;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Health Analytics Report</h1>
            <p style="font-size: 1.1em; color: #7f8c8d;">Generated for {username} on {datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class="score-display">
            <div class="score-main">{total_score}/100</div>
            <p style="font-size: 1.3em; margin-bottom: 20px;">Overall Health Score</p>

            <div class="score-breakdown">
                <div class="score-item">
                    <div style="font-size: 1.8em; font-weight: bold;">{score_breakdown.get('sleep', 0)}/25</div>
                    <div>Sleep Quality</div>
                </div>
                <div class="score-item">
                    <div style="font-size: 1.8em; font-weight: bold;">{score_breakdown.get('activity', 0)}/25</div>
                    <div>Activity Level</div>
                </div>
                <div class="score-item">
                    <div style="font-size: 1.8em; font-weight: bold;">{score_breakdown.get('hydration', 0)}/25</div>
                    <div>Hydration</div>
                </div>
                <div class="score-item">
                    <div style="font-size: 1.8em; font-weight: bold;">{score_breakdown.get('nutrition', 0)}/25</div>
                    <div>Nutrition</div>
                </div>
            </div>
        </div>

        <div class="metrics-grid">
    """

    # Add metric cards based on available data
    if 'sleep' in stats:
        sleep_progress = min((stats['sleep']['avg'] / 8) * 100, 100)
        progress_class = 'excellent' if sleep_progress >= 85 else 'good' if sleep_progress >= 70 else 'fair'

        html_content += f"""
            <div class="metric-card">
                <h3>😴 Sleep Analysis</h3>
                <div class="metric-value">{stats['sleep']['avg']}h</div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {sleep_progress}%"></div>
                </div>
                <div class="metric-details">
                    Average over {stats['sleep']['nights']} nights<br>
                    Range: {stats['sleep']['min']}h - {stats['sleep']['max']}h<br>
                    Consistency: ±{stats['sleep']['consistency']}h
                </div>
            </div>
        """

    if 'steps' in stats:
        steps_progress = min((stats['steps']['avg'] / 10000) * 100, 100)
        progress_class = 'excellent' if steps_progress >= 80 else 'good' if steps_progress >= 60 else 'fair'

        html_content += f"""
            <div class="metric-card">
                <h3>🚶 Activity Level</h3>
                <div class="metric-value">{stats['steps']['avg']:,}</div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {steps_progress}%"></div>
                </div>
                <div class="metric-details">
                    Average daily steps over {stats['steps']['days']} days<br>
                    Total steps: {stats['steps']['total']:,}<br>
                    Peak day: {stats['steps']['max']:,} steps
                </div>
            </div>
        """

    if 'water' in stats:
        water_progress = min((stats['water']['avg'] / 2000) * 100, 100)
        progress_class = 'excellent' if water_progress >= 90 else 'good' if water_progress >= 70 else 'fair'

        html_content += f"""
            <div class="metric-card">
                <h3>💧 Hydration</h3>
                <div class="metric-value">{stats['water']['avg']}ml</div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {water_progress}%"></div>
                </div>
                <div class="metric-details">
                    Average daily intake over {stats['water']['days']} days<br>
                    Total consumed: {stats['water']['total']:,}ml<br>
                    Target: 2,000ml per day
                </div>
            </div>
        """

    if 'food' in stats:
        cal_progress = 75 if 1500 <= stats['food']['avg_daily'] <= 2500 else 50
        progress_class = 'excellent' if cal_progress >= 70 else 'fair'

        html_content += f"""
            <div class="metric-card">
                <h3>🍎 Nutrition</h3>
                <div class="metric-value">{stats['food']['avg_daily']}</div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {cal_progress}%"></div>
                </div>
                <div class="metric-details">
                    Average daily calories over {stats['food']['days']} days<br>
                    Food variety: {stats['food']['variety']} different items<br>
                    Top foods: {', '.join(stats['food']['top_foods'][:3])}
                </div>
            </div>
        """

    html_content += "</div>"

    # Add insights
    if insights:
        html_content += """
        <div class="insights">
            <h2>💡 Personalized Health Insights</h2>
            <ul>
        """
        for insight in insights[:8]: # Limit insights
            html_content += f"<li>{insight}</li>"
        html_content += "</ul></div>"

    # Add data summary
    html_content += """
        <div class="data-summary">
            <h2>📊 Data Summary</h2>
    """

    if 'sleep' in stats:
        html_content += f"""
            <div class="data-row">
                <span class="data-label">Total Sleep Hours Tracked</span>
                <span class="data-value">{stats['sleep']['avg'] * stats['sleep']['nights']:.0f} hours</span>
            </div>
        """

    if 'steps' in stats:
        html_content += f"""
            <div class="data-row">
                <span class="data-label">Total Steps Recorded</span>
                <span class="data-value">{stats['steps']['total']:,} steps</span>
            </div>
        """

    if 'water' in stats:
        html_content += f"""
            <div class="data-row">
                <span class="data-label">Total Water Consumed</span>
                <span class="data-value">{stats['water']['total']:,} ml</span>
            </div>
        """

    if 'food' in stats:
        html_content += f"""
            <div class="data-row">
                <span class="data-label">Total Calories Tracked</span>
                <span class="data-value">{stats['food']['total']:,} calories</span>
            </div>
        """

    html_content += f"""
        </div>

        <div class="footer">
            <h3>Health Report Summary</h3>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This report provides a comprehensive overview of your health data trends and patterns.</p>
            <p>Use this information to make informed decisions about your health and wellness journey.</p>
        </div>
    </body>
    </html>
    """

    return html_content

# ===============================
# SOLUTION 2: SUMMARY TABLE REPORT (FAST)
# ===============================

def generate_table_based_report(df_food, df_sleep, df_steps, df_water, total_score, score_breakdown, insights, username):
    """
    Generate a report with data tables instead of charts - much faster!
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Health Data Report - {username}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .header {{ text-align: center; color: #3498db; margin-bottom: 30px; }}
            .score-box {{ background: #3498db; color: white; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0; }}
            .score-main {{ font-size: 3em; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .insights {{ background: #f0f8f0; padding: 20px; border-left: 5px solid #27ae60; margin: 20px 0; }}
            .metric-summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .metric-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
            .metric-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Health Analytics Report</h1>
            <h2>{username}</h2>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class="score-box">
            <div class="score-main">{total_score}/100</div>
            <p>Overall Health Score</p>
        </div>

        <div class="metric-summary">
            <div class="metric-box">
                <div class="metric-number">{score_breakdown.get('sleep', 0)}/25</div>
                <p>Sleep Score</p>
            </div>
            <div class="metric-box">
                <div class="metric-number">{score_breakdown.get('activity', 0)}/25</div>
                <p>Activity Score</p>
            </div>
            <div class="metric-box">
                <div class="metric-number">{score_breakdown.get('hydration', 0)}/25</div>
                <p>Hydration Score</p>
            </div>
            <div class="metric-box">
                <div class="metric-number">{score_breakdown.get('nutrition', 0)}/25</div>
                <p>Nutrition Score</p>
            </div>
        </div>
    """

    # Add data tables
    def add_data_table(df, title, columns_to_show):
        if df.empty:
            return f"<h3>{title}</h3><p>No data available</p>"

        # Get recent 10 entries
        recent_df = df.head(10)

        table_html = f"<h3>{title}</h3><table><thead><tr>"

        for col in columns_to_show:
            if col in recent_df.columns:
                table_html += f"<th>{col.replace('_', ' ').title()}</th>"

        table_html += "</tr></thead><tbody>"

        for _, row in recent_df.iterrows():
            table_html += "<tr>"
            for col in columns_to_show:
                if col in recent_df.columns:
                    value = row[col]
                    if pd.isna(value):
                        value = "N/A"
                    elif isinstance(value, float):
                        value = f"{value:.1f}"
                    table_html += f"<td>{value}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table>"
        return table_html

    html_content += add_data_table(df_sleep, "Recent Sleep Records", ['date', 'total_sleep_h'])
    html_content += add_data_table(df_steps, "Recent Activity Records", ['date', 'total_steps'])
    html_content += add_data_table(df_water, "Recent Hydration Records", ['date', 'amount'])
    html_content += add_data_table(df_food, "Recent Food Records", ['date', 'food_name', 'calories'])

    # Add insights
    if insights:
        html_content += '<div class="insights"><h3>Health Insights</h3><ul>'
        for insight in insights:
            html_content += f"<li>{insight}</li>"
        html_content += '</ul></div>'

    html_content += """
        <div style="margin-top: 40px; text-align: center; color: #7f8c8d;">
            <p>This report was generated using your personal health data.</p>
            <p>Consult healthcare professionals for medical advice.</p>
        </div>
    </body>
    </html>
    """

    return html_content

# ===============================
# SOLUTION 3: INSTANT MARKDOWN REPORT (SUPER FAST)
# ===============================

def generate_markdown_report(df_food, df_sleep, df_steps, df_water, total_score, score_breakdown, insights, username):
    """
    Generate a simple markdown report - instant generation!
    """

    report_content = f"""# Health Report for {username}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 Overall Health Score: {total_score}/100

| Category | Score | Status |
|----------|-------|--------|
| Sleep Quality | {score_breakdown.get('sleep', 0)}/25 | {'✅ Good' if score_breakdown.get('sleep', 0) >= 20 else '⚠️ Needs Attention'} |
| Activity Level | {score_breakdown.get('activity', 0)}/25 | {'✅ Good' if score_breakdown.get('activity', 0) >= 20 else '⚠️ Needs Attention'} |
| Hydration | {score_breakdown.get('hydration', 0)}/25 | {'✅ Good' if score_breakdown.get('hydration', 0) >= 20 else '⚠️ Needs Attention'} |
| Nutrition | {score_breakdown.get('nutrition', 0)}/25 | {'✅ Good' if score_breakdown.get('nutrition', 0) >= 20 else '⚠️ Needs Attention'} |

---

## 📊 Health Metrics Summary

"""

    # Add metrics based on available data
    if not df_sleep.empty:
        avg_sleep = round(df_sleep['total_sleep_h'].mean(), 1)
        consistency = round(df_sleep['total_sleep_h'].std(), 1)
        report_content += f"""### 😴 Sleep Analysis
- **Average Sleep:** {avg_sleep} hours per night
- **Sleep Consistency:** ±{consistency} hours
- **Total Nights Tracked:** {len(df_sleep)}
- **Sleep Range:** {df_sleep['total_sleep_h'].min():.1f}h - {df_sleep['total_sleep_h'].max():.1f}h

"""

    if not df_steps.empty:
        avg_steps = int(df_steps['total_steps'].mean())
        total_steps = int(df_steps['total_steps'].sum())
        report_content += f"""### 🚶 Activity Analysis
- **Average Daily Steps:** {avg_steps:,}
- **Total Steps Recorded:** {total_steps:,}
- **Most Active Day:** {df_steps['total_steps'].max():,} steps
- **Days Tracked:** {len(df_steps)}

"""

    if not df_water.empty:
        if 'date' in df_water.columns:
            daily_water = df_water.groupby('date')['amount'].sum()
            avg_water = int(daily_water.mean())
        else:
            avg_water = int(df_water['amount'].mean())
        total_water = int(df_water['amount'].sum())

        report_content += f"""### 💧 Hydration Analysis
- **Average Daily Water:** {avg_water}ml
- **Total Water Consumed:** {total_water:,}ml
- **Hydration Status:** {'✅ Meeting Goals' if avg_water >= 2000 else '⚠️ Below Recommended'}
- **Daily Target:** 2,000ml (2 liters)

"""

    if not df_food.empty:
        daily_calories = df_food.groupby('date')['calories'].sum()
        avg_calories = int(daily_calories.mean())
        food_variety = len(df_food['food_name'].unique())
        top_foods = df_food.groupby('food_name')['calories'].sum().head(3)

        report_content += f"""### 🍎 Nutrition Analysis
- **Average Daily Calories:** {avg_calories}
- **Food Variety:** {food_variety} different foods
- **Days Tracked:** {len(daily_calories)}
- **Top 3 Foods:** {', '.join(top_foods.index)}

"""

    # Add insights
    if insights:
        report_content += """---

## 💡 Personalized Health Insights

"""
        for i, insight in enumerate(insights, 1):
            report_content += f"{i}. {insight}\n"

    report_content += f"""

---

## 📋 Action Items

Based on your health data analysis:

1. **Focus Area:** {'Sleep' if score_breakdown.get('sleep', 0) < 20 else 'Activity' if score_breakdown.get('activity', 0) < 20 else 'Hydration' if score_breakdown.get('hydration', 0) < 20 else 'Nutrition' if score_breakdown.get('nutrition', 0) < 20 else 'Maintain current habits'}

2. **Quick Win:** {'Establish consistent bedtime' if score_breakdown.get('sleep', 0) < 20 else 'Add 1000 more daily steps' if score_breakdown.get('activity', 0) < 20 else 'Drink one extra glass of water with meals' if score_breakdown.get('hydration', 0) < 20 else 'Add more food variety' if score_breakdown.get('nutrition', 0) < 20 else 'Continue your excellent health habits!'}

3. **Track Progress:** Use this dashboard weekly to monitor improvements

---

*This report is based on your personal health data and is for informational purposes only. Consult healthcare professionals for medical advice.*

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return report_content

# ===============================
# MAIN EXPORT FUNCTION WITH OPTIONS (REMOVED TAB4)
# ===============================

def render_export_section(df_food, df_sleep, df_steps, df_water, total_score, score_breakdown, insights, username, plotly_figures):
    """
    Renders the data export section with options to download data and generate health reports.
    Tab4 (chart export) has been removed as requested.
    """
    st.markdown("---")
    st.markdown("### 📥 Export Your Data")

    with st.expander("ℹ️ Understanding Data Export Options"):
        st.markdown("""
        **Export Features:**

        **📊 CSV Downloads**:
        - **Raw data format** for further analysis in Excel, Google Sheets, or other tools
        - **Date-indexed** for easy time-series analysis
        - **Clean, structured format** ready for use

        **⚡ Fast Reports (No Charts)**:
        - **Instant HTML Report**: A visually appealing HTML report using CSS for elements, no chart images. Fastest for quick summaries.
        - **Table-Based HTML Report**: An HTML report focused on data tables and summaries. Fast and data-rich.
        - **Markdown Report**: A plain text markdown file, instantly generated and universally readable.

        **💡 Use Cases:**
        - **Share with healthcare providers** during appointments
        - **Personal tracking** in other apps or spreadsheets
        - **Long-term archiving** of your health journey
        - **Data analysis** for research or personal insights

        **Privacy Note**: Downloaded data remains private on your device. We don't store or share your exported data.
        """)

    # Export options in tabs (removed tab4)
    tab1, tab2, tab3 = st.tabs(["⚡ Instant Report", "📊 Table Report", "📝 Markdown"])

    with tab1:
        st.markdown("#### ⚡ Ultra-Fast Visual Report (No Charts)")
        st.markdown("Generates a beautiful, professional report in **under 1 second** using CSS styling instead of charts.")

        if st.button("🚀 Generate Instant Report", type="primary", key="generate_instant_report_btn"):
            with st.spinner("Generating instant report... ⚡"):
                report_html = generate_text_only_report(
                    df_food, df_sleep, df_steps, df_water,
                    total_score, score_breakdown, insights, username
                )

                st.download_button(
                    label="📥 Download Instant Report HTML",
                    data=report_html,
                    file_name=f"instant_health_report_{username.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="download_instant_report",
                    type="primary"
                )

                st.success("✅ Report generated instantly! Professional styling with progress bars and metrics. Open the downloaded HTML file in your browser to view.")

    with tab2:
        st.markdown("#### 📊 Table-Based Report")
        st.markdown("Data-focused report with tables and summaries - **lightning fast** generation.")

        if st.button("📊 Generate Table Report", key="generate_table_report_btn"):
            with st.spinner("Creating table report..."):
                table_report = generate_table_based_report(
                    df_food, df_sleep, df_steps, df_water,
                    total_score, score_breakdown, insights, username
                )

                st.download_button(
                    label="📥 Download Table Report HTML",
                    data=table_report,
                    file_name=f"table_health_report_{username.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="download_table_report"
                )

                st.success("✅ Table report ready! Perfect for detailed data review. Open the downloaded HTML file in your browser to view.")

    with tab3:
        st.markdown("#### 📝 Markdown Report")
        st.markdown("Simple, clean text report - **instant** generation, works everywhere.")

        if st.button("📝 Generate Markdown Report", key="generate_markdown_report_btn"):
            markdown_report = generate_markdown_report(
                df_food, df_sleep, df_steps, df_water,
                total_score, score_breakdown, insights, username
            )

            st.download_button(
                label="📥 Download Markdown Report",
                data=markdown_report,
                file_name=f"health_report_{username.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key="download_markdown_report"
            )

            st.success("✅ Markdown report generated instantly! Download the .md file to view in any text editor or markdown viewer.")

    st.markdown("---")
    st.markdown("#### 📥 Download Individual Data Sets")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if not df_sleep.empty:
            csv_sleep = df_sleep.to_csv(index=False)
            st.download_button(
                "💤 Download Sleep Data",
                csv_sleep,
                "sleep_data.csv",
                "text/csv",
                key="download_sleep_data",
                help="Download your sleep duration data including dates and total hours slept. Use for tracking sleep patterns over time."
            )
        else:
            st.button("💤 Sleep Data", disabled=True, key="download_sleep_data_disabled", help="No sleep data available to download")

    with col2:
        if not df_food.empty:
            csv_food = df_food.to_csv(index=False)
            st.download_button(
                "🍎 Download Food Data",
                csv_food,
                "food_data.csv",
                "text/csv",
                key="download_food_data",
                help="Download your food intake records including food names, calories, and consumption dates. Great for nutrition analysis."
            )
        else:
            st.button("🍎 Food Data", disabled=True, key="download_food_data_disabled", help="No food data available to download")

    with col3:
        if not df_water.empty:
            csv_water = df_water.to_csv(index=False)
            st.download_button(
                "💧 Download Water Data",
                csv_water,
                "water_data.csv",
                "text/csv",
                key="download_water_data",
                help="Download your water intake records showing daily hydration amounts. Track your hydration trends over time."
            )
        else:
            st.button("💧 Water Data", disabled=True, key="download_water_data_disabled", help="No water data available to download")

    with col4:
        if not df_steps.empty:
            csv_steps = df_steps.to_csv(index=False)
            st.download_button(
                "🚶 Download Steps Data",
                csv_steps,
                "steps_data.csv",
                "text/csv",
                key="download_steps_data",
                help="Download your daily step count data. Perfect for activity tracking and fitness goal monitoring."
            )
        else:
            st.button("🚶 Steps Data", disabled=True, key="download_steps_data_disabled", help="No step data available to download")

    # Data summary for export
    st.markdown("#### 📋 Data Summary")
    summary_data = []

    if not df_sleep.empty:
        summary_data.append(f"Sleep: {len(df_sleep)} nights tracked")
    if not df_food.empty:
        summary_data.append(f"Food: {len(df_food)} entries across {len(df_food['date'].unique()) if 'date' in df_food.columns else 'multiple'} days")
    if not df_water.empty:
        summary_data.append(f"Water: {len(df_water)} intake records")
    if not df_steps.empty:
        summary_data.append(f"Steps: {len(df_steps)} days of activity data")

    if summary_data:
        st.success(f"📊 **Your Data Portfolio**: {' • '.join(summary_data)}")
        st.caption("All downloads include your complete historical data for the selected metric. Data is formatted for easy analysis in spreadsheet applications.")
    else:
        st.info("📈 Upload health data to unlock export features and build your personal health data portfolio!")