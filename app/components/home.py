# components/home.py - Fixed UI Issues & Added Tech Logos
import streamlit as st

def render_home():
    # Define the base URL for your GitHub branch
    github_base_url = "https://github.com/yaffawijaya/samsung-health-graphrag/tree/claude-improvements"
    assets_base_url = "https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/claude-improvements/app/assets"

    # Overall page styling (removed font import since it's now global)
    st.markdown(
        f"""
        <style>
            /* Removed font import - now handled globally */
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
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .tech-item:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            }}

            /* Deployment Ready Notice */
            .deployment-notice {{
                background: linear-gradient(135deg, #e8f5e8, #d4edda);
                padding: 25px;
                border-radius: 10px;
                margin: 30px auto;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border-left: 5px solid #28a745;
                text-align: center;
            }}
            .deployment-notice h3 {{
                color: #155724;
                margin-bottom: 15px;
                font-size: 1.5em;
            }}
            .deployment-notice p {{
                color: #155724;
                margin-bottom: 10px;
            }}

            /* Getting Started Guide - Removed old styles */

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

            /* Tech Stack Section - Removed old styles */

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

            /* Image sections */
            .image-display {{
                text-align: center;
                margin: 30px auto;
                max-width: 700px;
            }}
            .image-display img {{
                max-width: 100%;
                height: auto;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}

            /* Center align buttons properly */
            .stButton>button {{
                margin: 0 auto;
                display: block;
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
            <p>Unlock personalized insights from your Samsung Health records using your own OpenAI API.</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Deployment Ready Notice
    st.markdown(
        """
        <div class="deployment-notice">
            <h3>🚀 Now Deployment Ready!</h3>
            <p><strong>Privacy First:</strong> Use your own OpenAI API key - we don't store it!</p>
            <p><strong>Sample Data Included:</strong> Try the app with our demo Samsung Health data</p>
            <p><strong>Easy Setup:</strong> Just 3 steps to start analyzing your health data</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Getting Started Guide - Using clean card design like Key Features
    st.markdown("<h2 class='section-header'>🚀 Quick Start Guide</h2>", unsafe_allow_html=True)
    
    # Quick Start Cards Grid
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div style="background: #4B79A1; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2em; font-weight: bold; margin: 0 auto 20px auto;">1</div>
                <h3>🔑 Provide Your OpenAI API Key</h3>
                <p>Enter your OpenAI API key in the sidebar. We don't store it - it's only used during your session. <a href="https://platform.openai.com/api-keys" target="_blank" style="color: #4B79A1;">Get your API key here</a>.</p>
            </div>
            <div class="feature-card">
                <div style="background: #4B79A1; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2em; font-weight: bold; margin: 0 auto 20px auto;">2</div>
                <h3>📱 Download Sample Health Data</h3>
                <p>Use our sample Samsung Health data to try the app, or export your own data from the Samsung Health app. Find the download link in the sidebar under "Step 2".</p>
            </div>
            <div class="feature-card">
                <div style="background: #4B79A1; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2em; font-weight: bold; margin: 0 auto 20px auto;">3</div>
                <h3>📊 Upload & Analyze</h3>
                <p>Go to "Input Data" to upload your health data ZIP file, then explore insights in the Dashboard and chat with the AI Assistant about your health patterns!</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("<hr style='border-top: 1px solid #eee; margin: 3em auto; width: 80%;'>", unsafe_allow_html=True)

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
                Then, it uses <b>Retrieval-Augmented Generation (RAG)</b>, powered by your OpenAI API, to provide
                intelligent, conversational answers and personalized insights directly from your unique health patterns
                stored in the graph. Think of it as a smart health companion that truly understands <b>your</b> data.
            </p>
            <div class="tech-highlights">
                <span class="tech-item">🔗 Neo4j Knowledge Graph</span>
                <span class="tech-item">💬 Retrieval-Augmented Generation (RAG)</span>
                <span class="tech-item">💡 Personalized Insights</span>
                <span class="tech-item">🗣️ Conversational AI</span>
                <span class="tech-item">🔒 Privacy First</span>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Tech Stack Section - Using clean card design like Key Features
    st.markdown("<h2 class='section-header'>🛠️ Technology Stack</h2>", unsafe_allow_html=True)
    
    # Deployment Platform
    st.markdown("### 💾 Deployment Platform")
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://download.logo.wine/logo/Google_Cloud_Platform/Google_Cloud_Platform-Logo.wine.png" alt="Google Cloud Platform" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>Google Cloud Platform</h3>
                <p>Scalable cloud infrastructure for reliable deployment and hosting of the Samsung Health GraphRAG application.</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Development Tools
    st.markdown("### 💻 Development Tools")
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://img.favpng.com/24/0/1/python-scalable-vector-graphics-logo-javascript-clip-art-png-favpng-7AMPmkRx5u0JQsydMRxFv8mKn.jpg" alt="Python" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>Python</h3>
                <p>Core programming language powering the backend logic, data processing, and AI integration components.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.svg" alt="Streamlit" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>Streamlit</h3>
                <p>Modern web framework for building the interactive user interface with real-time data visualization.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://brandlogos.net/wp-content/uploads/2025/03/langchain-logo_brandlogos.net_9zgaw.png" alt="LangChain" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>LangChain</h3>
                <p>Framework for building AI applications with language models, enabling sophisticated RAG capabilities.</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Database Technologies
    st.markdown("### 🗄️ Database Technologies")
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/e/e5/Neo4j-logo_color.png" alt="Neo4j" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>Neo4j</h3>
                <p>Graph database for storing health data relationships and enabling complex pattern discovery through GraphRAG.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://cdn.iconscout.com/icon/free/png-256/free-mysql-logo-icon-download-in-svg-png-gif-file-formats--technology-social-media-company-brand-vol-5-pack-logos-icons-2945040.png?f=webp&w=256" alt="MySQL" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>MySQL</h3>
                <p>Relational database for structured health data storage, user management, and chat session history.</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # AI Technologies
    st.markdown("### 🤖 AI Technologies")
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Claude_AI_logo.svg/1280px-Claude_AI_logo.svg.png" alt="Claude Sonnet 4" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>Claude Sonnet 4</h3>
                <p>Advanced AI assistant used for development support, code optimization, and architectural design decisions.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/OpenAI_Logo.svg/1280px-OpenAI_Logo.svg.png" alt="OpenAI GPT-4" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
                <h3>OpenAI GPT-4</h3>
                <p>Large language model powering the conversational AI assistant for natural health data analysis.</p>
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
                <div class="feature-icon"><i class="fas fa-key"></i></div>
                <h3>🔒 Privacy First</h3>
                <p>Use your own OpenAI API key. We don't store your API key or personal data - everything stays private and secure.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-upload"></i></div>
                <h3>📱 Easy Data Input</h3>
                <p>Upload Samsung Health data or use our sample dataset. Support for sleep, steps, food intake, and water consumption data.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                <h3>📊 Smart Analytics</h3>
                <p>Advanced dashboard with health score calculation, trend analysis, weekly patterns, and correlation insights.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-comments"></i></div>
                <h3>🤖 AI Health Assistant</h3>
                <p>Chat naturally with AI about your health data. Get personalized insights, recommendations, and answer complex health questions.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-download"></i></div>
                <h3>📄 Export Reports</h3>
                <p>Generate comprehensive health reports in multiple formats: visual HTML reports, data tables, or markdown summaries.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-network-wired"></i></div>
                <h3>🔗 Graph Intelligence</h3>
                <p>Powered by Neo4j graph database to understand complex relationships between your health metrics and patterns.</p>
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
    
    # Technical Architecture Description
    st.markdown(
        """
        <div class="content-block">
            <h3>🏗️ Technical Architecture</h3>
            <p>
                The application follows a sophisticated GraphRAG architecture where your health data is ingested into a 
                <strong>Neo4j knowledge graph</strong>, creating rich relationships between different health metrics. 
                When you ask questions, the system uses <strong>advanced retrieval techniques</strong> to find relevant 
                data from the graph, then leverages <strong>your OpenAI API</strong> to generate natural, conversational 
                insights about your health patterns and trends.
            </p>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")

    # Meet the Team
    st.markdown("<h2 class='section-header'>Meet the Team</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="team-grid">
            <div class="team-member">
                <img src="{assets_base_url}/author_1_yaffa.png" class="member-img" alt="Yaffazka Afazillah Wijaya"/>
                <p class="member-name">Yaffazka Afazillah Wijaya</p>
                <p class="member-role">Lead Data Scientist</p>
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

    # Project Poster
    st.markdown("<h2 class='section-header'>Project Poster</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="image-display">
            <img src="{assets_base_url}/psd_poster.png" alt="Project Poster"/>
        </div>
        """, unsafe_allow_html=True
    )
    
    # GitHub link
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