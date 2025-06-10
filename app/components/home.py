# components/home.py
import streamlit as st

def render_home():
    # Overall page styling and fonts
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            html, body, [class*="st-"] {
                font-family: 'Inter', sans-serif;
                color: #2c3e50;
            }
            .main-header {
                text-align: center;
                margin-bottom: 0.5em;
                padding-top: 20px;
            }
            .main-header h1 {
                font-size: 3.5em;
                color: #4B79A1; /* Samsung Health blue */
                font-weight: 700;
                margin-bottom: 0.1em;
            }
            .main-header h1 span:last-child {
                color: #283E51; /* Darker blue/grey for GraphRAG */
            }
            .main-header h4 {
                color: #555;
                font-weight: 600;
                margin-bottom: 0.5em;
            }
            .main-header p {
                font-style: italic;
                color: #777;
                font-size: 1.1em;
            }
            .section-header {
                text-align: center;
                color: #4B79A1;
                font-size: 2em;
                margin-top: 3em;
                margin-bottom: 1.5em;
                font-weight: 600;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 10px;
            }
            .content-block {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                text-align: center;
            }
            .content-block h3 {
                color: #283E51;
                font-size: 1.8em;
                margin-bottom: 15px;
            }
            .content-block p {
                font-size: 1.1em;
                line-height: 1.7;
                color: #444;
            }

            /* Team Section */
            .team-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
                justify-content: center;
                margin: 40px 0;
            }
            .team-member {
                text-align: center;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                transition: transform 0.2s ease-in-out;
            }
            .team-member:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            }
            .member-img {
                border-radius: 50%;
                width: 120px;
                height: 120px;
                object-fit: cover;
                border: 4px solid #4B79A1;
                margin-bottom: 15px;
            }
            .member-name {
                font-weight: 700;
                font-size: 1.2em;
                color: #283E51;
                margin-bottom: 5px;
            }
            .member-role {
                font-size: 0.9em;
                color: #777;
                margin-bottom: 10px;
            }
            .social-links a {
                color: #4B79A1;
                margin: 0 8px;
                font-size: 1.2em;
                text-decoration: none;
            }
            .social-links a:hover {
                color: #283E51;
            }

            /* Image sections (How it Works, Poster) */
            .image-display {
                text-align: center;
                margin: 30px 0;
            }
            .image-display img {
                max-width: 100%; /* Make images responsive */
                height: auto;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }

            /* Call to Action Button */
            .stButton>button {
                background-color: #4B79A1;
                color: white;
                border-radius: 8px;
                padding: 10px 25px;
                font-size: 1.2em;
                font-weight: 600;
                border: none;
                transition: background-color 0.2s ease, transform 0.2s ease;
            }
            .stButton>button:hover {
                background-color: #283E51;
                transform: translateY(-2px);
            }

            .st-emotion-cache-1pxpxg4 { /* Targeted CSS for the main container padding */
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }

        </style>
        """, unsafe_allow_html=True
    )

    # Main Header
    st.markdown(
        """
        <div class="main-header">
            <h1>Welcome to <span>Samsung Health</span> <span>GraphRAG</span></h1>
            <h4>Capstone Project for Data Science</h4>
            <p>AI-Powered Health Data Analysis for Personalized Insights</p>
        </div>
        <hr style="border-top: 1px solid #eee; margin: 3em auto; width: 80%;">
        """, unsafe_allow_html=True
    )


    # What is Samsung Health GraphRAG?
    st.markdown("<h2 class='section-header'>What is Samsung Health GraphRAG?</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="content-block">
            <p>
                <b>Samsung Health GraphRAG</b> is an innovative application designed to transform your personal health data
                into actionable insights. By leveraging the power of **Graph Neural Networks (GNNs)** and **Retrieval-Augmented Generation (RAG)**
                techniques, we create a sophisticated health knowledge graph from your Samsung Health data.
            </p>
            <p>
                This allows for advanced analysis, including trend identification, correlation discovery, and personalized
                recommendations, helping you make informed decisions about your well-being.
            </p>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # How it Works
    st.markdown("<h2 class='section-header'>How it Works</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="image-display">
            <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/how_it_work.png" alt="How It Works Diagram"/>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Meet the Team heading
    st.markdown("<h2 class='section-header'>Meet the Team</h2>", unsafe_allow_html=True)

    # Team members using a responsive grid layout
    st.markdown(
        """
        <div class="team-grid">
            <div class="team-member">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/author_1_yaffa.png" class="member-img" alt="Yaffazka Afazillah Wijaya"/>
                <p class="member-name">Yaffazka Afazillah Wijaya</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/yaffazka-afazillah-wijaya-656b26227/" target="_blank">LinkedIn</a>
                    <a href="https://github.com/yaffawijaya" target="_blank">GitHub</a>
                </div>
            </div>
            <div class="team-member">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/author_2_dapa.png" class="member-img" alt="Daffa Aqil Shadiq"/>
                <p class="member-name">Daffa Aqil Shadiq</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/daffaaqilshadiq/" target="_blank">LinkedIn</a>
                    <a href="https://github.com/DaffaAqilS" target="_blank">GitHub</a>
                </div>
            </div>
            <div class="team-member">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/author_4_hasna.png" class="member-img" alt="Hasna Aqila R."/>
                <p class="member-name">Hasna Aqila R.</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/hasnaaqilarahman/" target="_blank">LinkedIn</a>
                    <a href="https://github.com/hasnaaqr" target="_blank">GitHub</a>
                </div>
            </div>
            <div class="team-member">
                <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/author_3_hijrah.png" class="member-img" alt="Hijrah Wira Pratama"/>
                <p class="member-name">Hijrah Wira Pratama</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/hijrahwira/" target="_blank">LinkedIn</a>
                    <a href="https://github.com/hijrahwira" target="_blank">GitHub</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Project Poster heading
    st.markdown("<h2 class='section-header'>Project Poster</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="image-display">
            <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets/psd_poster.png" alt="Project Poster"/>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Call to Action
    st.markdown(
        """
        <div style="text-align: center; margin: 40px 0;">
            <p style="font-size: 1.3em; margin-bottom: 20px; color: #444;">Ready to explore your health data?</p>
        </div>
        """, unsafe_allow_html=True
    )
    # Using st.columns to center the button more reliably
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🚀 Get Started with Your Health Data", key="get_started_button"):
            st.session_state.current_page = "Data Input" # Assuming you use session state for page navigation
            st.rerun()

    # GitHub link (remains at the bottom, perhaps with a smaller style)
    st.markdown(
        """
        <div style='text-align:center; margin-top: 50px; font-size: 0.9em; color: #777;'>
        <p>Learn more about the project on GitHub:</p>
        <a href='https://github.com/yaffawijaya/samsung-health-graphrag' target='_blank'
        style='color:#4B79A1; text-decoration:underline;'>
        https://github.com/yaffawijaya/samsung-health-graphrag
        </a>
        </div>
        """,
        unsafe_allow_html=True
    )
