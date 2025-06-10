# components/home.py
import streamlit as st

def render_home():
    # Define the base URL for your GitHub branch
    github_base_url = "https://github.com/yaffawijaya/samsung-health-graphrag/tree/claude-improvements"
    assets_base_url = "https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets"

    # Define navigation callbacks directly within render_home for clarity
    # These functions will be assigned to the on_click attribute of the buttons
    def to_input_data():
        st.session_state.main_page = 'input_user_data'
        st.rerun() # Rerun to switch page

    def to_dashboard():
        st.session_state.main_page = 'user_dashboard'
        st.rerun() # Rerun to switch page

    def to_ai():
        st.session_state.main_page = 'ai_assistant'
        st.rerun() # Rerun to switch page

    # Overall page styling and fonts
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            html, body, [class*="st-"] {{
                font-family: 'Inter', sans-serif;
                color: #2c3e50;
            }}
            .main-header {{
                text-align: center;
                margin-bottom: 0.5em;
                padding-top: 20px;
            }}
            .main-header h1 {{
                font-size: 3.5em;
                color: #4B79A1; /* Samsung Health blue */
                font-weight: 700;
                margin-bottom: 0.1em;
            }}
            .main-header h1 span:last-child {{
                color: #283E51; /* Darker blue/grey for GraphRAG */
            }}
            .main-header h4 {{
                color: #555;
                font-weight: 600;
                margin-bottom: 0.5em;
            }}
            .main-header p {{
                font-style: italic;
                color: #777;
                font-size: 1.1em;
            }}
            .section-header {{
                text-align: center;
                color: #4B79A1;
                font-size: 2em;
                margin-top: 3em;
                margin-bottom: 1.5em;
                font-weight: 600;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 10px;
            }}
            .content-block {{
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                text-align: center;
            }}
            .content-block h3 {{
                color: #283E51;
                font-size: 1.8em;
                margin-bottom: 15px;
            }}
            .content-block p {{
                font-size: 1.1em;
                line-height: 1.7;
                color: #444;
            }}

            /* GraphRAG Intro Specific Styling */
            .graphrag-intro {{
                background: linear-gradient(135deg, #eaf6ff, #dbe9f7);
                padding: 40px;
                border-radius: 15px;
                margin: 40px auto;
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
                border: 1px solid #cceeff;
                text-align: center;
            }}
            .graphrag-intro h2 {{
                color: #3498db;
                font-size: 2.2em;
                margin-bottom: 20px;
                border-bottom: none; /* Override general section-header border */
                padding-bottom: 0;
            }}
            .graphrag-intro p {{
                font-size: 1.2em;
                line-height: 1.8;
                max-width: 700px;
                margin: 0 auto 20px auto;
                color: #333;
            }}
            .graphrag-intro b {{
                color: #2980b9;
            }}
            .tech-highlights {{
                display: flex;
                justify-content: center;
                gap: 25px;
                margin-top: 30px;
                flex-wrap: wrap;
            }}
            .tech-item {{
                background: rgba(255,255,255,0.7);
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                font-weight: 600;
                color: #283E51;
                border: 1px solid #e0e0e0;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Added transition */
            }}
            .tech-item:hover {{ /* Added hover effect */
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            }}


            /* Features Grid */
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }}
            .feature-card {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                text-align: center;
                transition: transform 0.2s ease-in-out;
            }}
            .feature-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            .feature-card h3 {{
                color: #4B79A1;
                font-size: 1.5em;
                margin-bottom: 15px;
            }}
            .feature-card p {{
                font-size: 1em;
                color: #555;
            }}
            .feature-icon {{
                font-size: 3em;
                color: #283E51;
                margin-bottom: 15px;
            }}


            /* Team Section */
            .team-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
                justify-content: center;
                margin: 40px 0;
            }}
            .team-member {{
                text-align: center;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                transition: transform 0.2s ease-in-out;
            }}
            .team-member:hover {{
                transform: translateY(-5px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            }}
            .member-img {{
                border-radius: 50%;
                width: 120px;
                height: 120px;
                object-fit: cover;
                border: 4px solid #4B79A1;
                margin-bottom: 15px;
            }}
            .member-name {{
                font-weight: 700;
                font-size: 1.2em;
                color: #283E51;
                margin-bottom: 5px;
            }}
            .member-role {{
                font-size: 0.9em;
                color: #777;
                margin-bottom: 10px;
            }}
            .social-links a {{
                color: #4B79A1;
                margin: 0 8px;
                font-size: 1.2em;
                text-decoration: none;
            }}
            .social-links a:hover {{
                color: #283E51;
            }}

            /* Image sections (How it Works, Poster) */
            .image-display {{
                text-align: center;
                margin: 30px auto; /* Center the container */
                max-width: 700px; /* Adjusted max width for posters */
            }}
            .image-display img {{
                max-width: 100%; /* Make images responsive within their container */
                height: auto;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}

            /* Call to Action Buttons - New Styling */
            .start-buttons-container {{
                display: flex;
                flex-wrap: wrap; /* Allow buttons to wrap on smaller screens */
                justify-content: center; /* Center buttons horizontally */
                gap: 20px; /* Space between buttons */
                margin: 40px 0 50px 0; /* Margin top/bottom */
            }}
            .start-buttons-container .stButton>button {{
                background-color: #3498db; /* Lighter, more vibrant blue */
                color: white;
                border-radius: 8px;
                padding: 12px 28px; /* Slightly larger padding for better click area */
                font-size: 1.1em; /* Slightly smaller font to fit 3 buttons better */
                font-weight: 600;
                border: none;
                transition: background-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
                min-width: 200px; /* Ensure buttons have a minimum width */
            }}
            .start-buttons-container .stButton>button:hover {{
                background-color: #2980b9; /* Slightly darker on hover */
                transform: translateY(-3px); /* Lift effect on hover */
                box-shadow: 0 6px 15px rgba(0,0,0,0.1); /* Subtle shadow on hover */
            }}

            /* Adjust main container padding if needed for a wider look */
            .st-emotion-cache-1pxpxg4 {{
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }}

        </style>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
        """, unsafe_allow_html=True
    )

    # Main Header
    st.markdown(
        """
        <div class="main-header">
            <h1>Welcome to <span>Samsung Health</span> <span>GraphRAG</span></h1>
            <h4>Your AI-Powered Health Data Analyst</h4>
            <p>Unlock personalized insights from your Samsung Health records.</p>
        </div>
        <hr style="border-top: 1px solid #eee; margin: 3em auto; width: 80%;">
        """, unsafe_allow_html=True
    )

    # What is Samsung Health GraphRAG?
    st.markdown("<h2 class='section-header'>What is Samsung Health GraphRAG?</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="graphrag-intro">
            <p>
                <b>Samsung Health GraphRAG</b> is an innovative application designed to transform your personal health data
                into actionable insights. It leverages a <b>Neo4j Knowledge Graph</b> to build a rich, interconnected
                representation of your Samsung Health data (sleep, steps, food, water).
            </p>
            <p>
                Then, it uses <b>Retrieval-Augmented Generation (RAG)</b>, powered by advanced AI models, to provide
                intelligent, conversational answers and personalized insights directly from your unique health patterns
                stored in the graph. Think of it as a smart health companion that truly understands <b>your</b> data.
            </p>
            <div class="tech-highlights">
                <span class="tech-item">🔗 Neo4j Knowledge Graph</span>
                <span class="tech-item">💬 Retrieval-Augmented Generation (RAG)</span>
                <span class="tech-item">💡 Personalized Insights</span>
                <span class="tech-item">🗣️ Conversational AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Key Features
    st.markdown("<h2 class='section-header'>Key Features</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-upload"></i></div>
                <h3>Seamless Data Input</h3>
                <p>Easily upload your Samsung Health data (ZIP file) to get started with analysis.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                <h3>Intelligent Dashboard</h3>
                <p>Visualize trends, patterns, and correlations across your sleep, activity, nutrition, and hydration data.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-comments"></i></div>
                <h3>Conversational AI Assistant</h3>
                <p>Ask natural language questions about your health and receive personalized advice and explanations.</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # How it Works (Diagram)
    st.markdown("<h2 class='section-header'>How it Works</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="image-display">
            <img src="{assets_base_url}/how_it_work.png" alt="How It Works Diagram"/>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Meet the Team heading
    st.markdown("<h2 class='section-header'>Meet the Team</h2>", unsafe_allow_html=True)

    # Team members using a responsive grid layout
    st.markdown(
        f"""
        <div class="team-grid">
            <div class="team-member">
                <img src="{assets_base_url}/author_1_yaffa.png" class="member-img" alt="Yaffazka Afazillah Wijaya"/>
                <p class="member-name">Yaffazka Afazillah Wijaya</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/yaffazka-afazillah-wijaya-656b26227/" target="_blank"><i class="fab fa-linkedin"></i></a>
                    <a href="{github_base_url.replace('/tree/claude-improvements', '')}" target="_blank"><i class="fab fa-github"></i></a>
                </div>
            </div>
            <div class="team-member">
                <img src="{assets_base_url}/author_2_dapa.png" class="member-img" alt="Daffa Aqil Shadiq"/>
                <p class="member-name">Daffa Aqil Shadiq</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/daffaaqilshadiq/" target="_blank"><i class="fab fa-linkedin"></i></a>
                    <a href="{github_base_url.replace('/tree/claude-improvements', '')}" target="_blank"><i class="fab fa-github"></i></a>
                </div>
            </div>
            <div class="team-member">
                <img src="{assets_base_url}/author_4_hasna.png" class="member-img" alt="Hasna Aqila R."/>
                <p class="member-name">Hasna Aqila R.</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/hasnaaqilarahman/" target="_blank"><i class="fab fa-linkedin"></i></a>
                    <a href="{github_base_url.replace('/tree/claude-improvements', '')}" target="_blank"><i class="fab fa-github"></i></a>
                </div>
            </div>
            <div class="team-member">
                <img src="{assets_base_url}/author_3_hijrah.png" class="member-img" alt="Hijrah Wira Pratama"/>
                <p class="member-name">Hijrah Wira Pratama</p>
                <p class="member-role">Data Scientist</p>
                <div class="social-links">
                    <a href="https://www.linkedin.com/in/hijrahwira/" target="_blank"><i class="fab fa-linkedin"></i></a>
                    <a href="{github_base_url.replace('/tree/claude-improvements', '')}" target="_blank"><i class="fab fa-github"></i></a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Project Poster heading
    st.markdown("<h2 class='section-header'>Project Poster</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="image-display">
            <img src="{assets_base_url}/psd_poster.png" alt="Project Poster"/>
        </div>
        """, unsafe_allow_html=True
    )
    # GitHub link (remains at the bottom, perhaps with a smaller style)
    st.markdown(
        f"""
        <div style='text-align:center; margin-top: 50px; font-size: 0.9em; color: #777;'>
        <p>Learn more about the project on GitHub:</p>
        <a href='{github_base_url}' target='_blank'
        style='color:#4B79A1; text-decoration:none;'>
        <i class="fab fa-github" style="font-size:1.5em; vertical-align:middle; margin-right:5px;"></i> {github_base_url}
        </a>
        </div>
        """,
        unsafe_allow_html=True
    )
