# Samsung Health GraphRAG
<p align="center">
    <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/refs/heads/master/app/assets/graphrag-samsunghealth.png" alt="Project Logo" width="30%" />
</p>


## Overview
**Samsung Health GraphRAG** is a Data Science project developed as part of **Data Science Project 2025**, completed by **Group 1**. This project integrates **Samsung Health data** with **Graph-based Retrieval-Augmented Generation (GraphRAG)** to enable structured and unstructured health data analysis.

## Project Structure
```
samsunghealth-graphrag
│-- app/
│   │-- assets/                # Project assets (images, icons, etc.)
│   │-- data/                  # Samsung Health dataset
│   │-- modules/               # Development phase modules
│   │-- __pycache__/           # Python cache directory
│   │-- .env                   # Environment variables (not included in repo)
│   │-- .env-experiment        # Template for environment variables
│   │-- .gitignore             # Git ignore file
│   │-- app.py                 # Main application entry point (Streamlit app)
```

## Installation & Setup
To run this project locally, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/yaffawijaya/samsung-health-graphrag.git
cd samsunghealth-graphrag
```

### 2. Set Up Environment Variables
- Copy the example `.env-experiment` file and rename it to `.env`
- Open `.env` and configure your API keys and database credentials:

#### Example `.env` file:
```
OPENAI_API_KEY=sk-proj
NEO4J_URI=bolt://neo4j:portnumber
NEO4J_USERNAME=username
NEO4J_PASSWORD=userpass
```

### 3. Install Dependencies (REQUIREMENT NOT READY YET)
Make sure you have **Python 3.10+** installed. Then, install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Execute the following command to launch the Streamlit application:
```bash
streamlit run app/app.py
```

## Features
- **Samsung Health Data Processing** - Parses and structures Samsung Health data.
- **Graph-based Retrieval** - Integrates with **Neo4j** for structured querying.
- **AI-powered Health Insights** - Uses **LangChain** & **OpenAI API** to analyze health data.
- **Streamlit UI** - Interactive interface for users to upload and analyze health data.

## Contact & Support
For any questions, feel free to open an issue on GitHub or reach out to **yaffazka@gmail.com**.