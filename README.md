# Samsung Health GraphRAG
<p align="center">
    <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/refs/heads/master/app/assets/graphrag-samsunghealth.png" alt="Project Logo" width="30%" />
</p>


## Overview
**Samsung Health GraphRAG** is a Data Science project developed as part of **Data Science Project 2025**, completed by **Group 1**. This project integrates **Samsung Health data** with **Graph-based Retrieval-Augmented Generation (GraphRAG)** to enable structured and unstructured health data analysis.

<p align="center">
    <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/refs/heads/master/app/assets/app-prototpye.jpeg" alt="Project Logo" width="100%" />
</p>


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
MYSQL_HOST=mysql
MYSQL_USER=root
MYSQL_PASSWORD=secret
MYSQL_DATABASE=app
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
- **Samsung Health Data Processing** - Parses, structures, and uploads Samsung Health data into a Neo4j graph database.
- **Graph-based Retrieval** - Uses Neo4j to store health data (Food, Water, Sleep, and Steps) with a unified date property (recordedOn) and a common label (HealthData).
- **Hybrid Retrieval-Augmented Generation** - Integrates LangChain and OpenAI to extract structured health entities from user queries, build precise Cypher queries (including date and measurement type filtering), and perform vector search over the graph data.
- **Streamlit UI** - Provides an interactive interface for users to select existing users, upload Samsung Health ZIP files, manage the graph database, and ask natural language health questions.


## Development Summary and Evaluation
What We Did
- **Graph Database Setup:**

* Developed a Cypher query to create a User node ("Yaffa") and measurement nodes (Food, Water, Sleep, Step) for 14 consecutive days starting from January 1, 2025.
* Each measurement node now includes a common label (HealthData) and a unified date property (recordedOn), which enables uniform querying across all types.

- **RAG Module (rag.py):**

* Implemented structured retrieval using LangChain’s prompt templates to extract health-related entities from user questions.
* Enhanced retrieval accuracy by adding helper functions to extract both full dates (YYYY-MM-DD) and month–year ranges (e.g., "January 2025") from queries.
* Incorporated measurement type extraction (e.g., Food, Water, Sleep, Step) so that queries can be narrowed to a specific health metric.
* Built a vector search index using OpenAI embeddings over nodes with the HealthData label.

- **Sreamlit App (app.py):**

* Developed a user interface with a sidebar dropdown to select an existing user from the Neo4j database, or to input a new user.
Provided functionality to upload Samsung Health data ZIP files and manage the graph database.
* Integrated the RAG retrieval system with the UI, allowing users to ask questions (e.g., "What food did I eat on 2025-01-05?" or "Can you provide a summary of my health data for January 2025?") and receive answers based on both structured and vector-based searches.
* Evaluation (As of February 23, 2025)
Food Data Retrieval:
The system accurately returns food-related data when specific dates (e.g., January 5, 2025) or broader queries (e.g., "in January 2025") are used.


- **Water, Sleep, and Step Data Retrieval:**
While the system successfully retrieves some data, testing revealed that queries for sleep duration and step count (especially when specifying exact dates) need further refinement. The extraction of measurement types and date filtering is working, but additional tuning (e.g., improved regex and data indexing) may be required to ensure comprehensive retrieval for these metrics.

- **User Interface:**
The Streamlit app functions smoothly, with a clear dropdown for user selection and an intuitive file upload mechanism. The provided screenshot here confirms the current prototype.

**Overall:**
The GraphRAG system shows strong potential for providing health insights from Samsung Health data. While food data is retrieved accurately, further work is needed to enhance the retrieval accuracy for water, sleep, and steps. Future improvements will focus on refining entity extraction and query filtering.

## Future Development

- **Interactive Dashboard User Report**: PIC dapa, hasna
- **Retrieval Refinement**: PIC yaffa
- **Seamless Data Cleaning Process**: PIC hijrah

## Contact & Support
For any questions, feel free to open an issue on GitHub or reach out to **yaffazka@gmail.com**.