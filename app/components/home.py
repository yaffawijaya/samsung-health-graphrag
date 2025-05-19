# components/home.py
import streamlit as st

def render_home():
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

    # CSS and author HTML layout
    st.markdown(
        """
        <style>
            .author-container {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 50px;
                flex-wrap: wrap;
                margin: 30px 0;
            }
            .author-item {
                text-align: center;
            }
            .author-img {
                border-radius: 50%;
                width: 100px;
                height: 100px;
                object-fit: cover;
            }
        </style>

        <div class="author-container">
            <div class="author-item">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/master/app/assets/author_1_yaffa.jpeg" class="author-img"/>
                <p style="font-weight: bold; margin-top: 8px;">Yaffazka Afazillah Wijaya</p>
            </div>
            <div class="author-item">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/master/app/assets/author_2_dapa.png" class="author-img"/>
                <p style="font-weight: bold; margin-top: 8px;">Daffa Aqil Shadiq</p>
            </div>
            <div class="author-item">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/master/app/assets/author_4_hasna.png" class="author-img"/>
                <p style="font-weight: bold; margin-top: 8px;">Hasna Aqila R.</p>
            </div>
            <div class="author-item">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/master/app/assets/author_3_hijrah.png" class="author-img"/>
                <p style="font-weight: bold; margin-top: 8px;">Hijrah Wira Pratama</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("---")

    # Project Poster heading
    st.markdown(
        "<h2 style='text-align:center; color:#4B79A1;'>Project Poster</h2>",
        unsafe_allow_html=True
    )

    # Center the poster image from GitHub
    st.markdown(
        """
        <div style='text-align: center; margin-top: 20px;'>
            <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/master/app/assets/psd_poster.png" width="400"/>
        </div>
        """,
        unsafe_allow_html=True
    )

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
