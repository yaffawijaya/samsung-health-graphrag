# Samsung Health GraphRAG Explorer

<p align="center">
  <img src="https://raw.githubusercontent.com/yaffawijaya/samsung-health-graphrag/refs/heads/master/app/assets/sample_chatbot.gif" alt="Demo Application" width="100%"/>
</p>

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [System Architecture](#system-architecture)  
4. [Repository Structure](#repository-structure)  
5. [Getting Started](#getting-started)  
   - [1. Clone the Repository](#1-clone-the-repository)  
   - [2. Configuration](#2-configuration)  
   - [3. Environment Setup](#3-environment-setup)  
   - [4. Launch the App](#4-launch-the-app)  
6. [Usage](#usage)  
7. [Development & Evaluation](#development--evaluation)  
8. [Future Work](#future-work)  
9. [Contact](#contact)  

---

## Project Overview

**Samsung Health GraphRAG Explorer** integrates Samsung Health data with a Graph-based Retrieval-Augmented Generation (GraphRAG) pipeline. It allows users to:

- Upload and clean their Samsung Health ZIP exports.  
- Persist health measurements (food, water, sleep, steps) in both MySQL and Neo4j.  
- Pose natural-language queries via a Streamlit interface and receive answers generated from structured Cypher queries and vector search.  

<p align="center">
  <img src="assets/app-prototype-v2.png" alt="App Prototype" width="80%"/>
</p>

---

## Features

- **Data Ingestion & Cleaning**  
  Parses raw CSV files from Samsung Health ZIP and normalizes them into structured tables.

- **Relational & Graph Storage**  
  Stores cleaned data in MySQL for tabular reporting and in Neo4j for graph-native queries.

- **Hybrid Retrieval**  
  Combines Cypher-based querying with vector search over OpenAI embeddings (via LangChain).

- **AI Assistant**  
  A conversational UI powered by Streamlit’s chat interface. Users can ask questions like “What did I eat on 2025-05-10?” or “Show my average sleep in April 2025.”

---

## System Architecture

<p align="center">
  <img src="assets/System_Architecture.svg" alt="System Architecture" width="90%"/>
</p>

1. **Streamlit Frontend**  
2. **MySQL** for time-series data storage  
3. **Neo4j** GraphDB with two retrieval modes:  
   - **Cypher QA Chain** for structured queries  
   - **Vector QA Chain** for semantic search  
4. **OpenAI** for embedding & function-calling  

---

## Repository Structure
```
├── app.py              # Main Streamlit application
├── secrets.toml        # Copy of your_secrets.toml with credentials
├── your_secrets.toml   # Template for database & API credentials
├── assets/             # Images, diagrams, author photos, poster
├── modules/
│ └── utils/
│ ├── cleaner/          # CSV loading & cleaning routines
│ ├── db/               # MySQL & Neo4j helper modules
│ └── retrieval/        # GraphRAG agent setup
└── setup/
└── database_setup.py   # SQL schema creation
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yaffawijaya/samsung-health-graphrag.git
cd samsung-health-graphrag/app
```

### 2. Configuration
- Rename `your_secrets.toml` to `secrets.toml` at the project root.

- Populate the file with your credentials:
```toml
[mysql]
user     = "<mysql_username>"
password = "<mysql_password>"
host     = "<mysql_host>"
port     = <mysql_port>
database = "<mysql_database>"

[neo4j]
NEO4J_URI      = "<bolt://...>"
NEO4J_USERNAME = "<neo4j_user>"
NEO4J_PASSWORD = "<neo4j_password>"

[openai]
OPENAI_API_KEY = "<your_openai_api_key>"

```

### 3. Environment Setup
We recommend Conda for reproducibility. From a terminal:
```bash
conda env create -f environment.yml
conda activate graphrag
```

#### DB SETUP
1. Run `database_setup.py`
```bash
python setup/database_setup.py
```

### 4. Launch the App
```bash
streamlit run app.py
```

make sure MySQL and Neo4j is rollin


## Usage
### Home
Overview, project poster, author credits, GitHub link.

### Input Data
Upload Samsung Health ZIP → cleans and previews tables → push to MySQL & Neo4j.

### User Dashboard
Visualize calories, sleep, steps, water with charts and tables.

### AI Assistant
Chat interface for querying your health graph using natural language.

## Development & Evaluation
### Graph Modeling
All measurement nodes share the HealthData label and recordedOn date property for uniform querying.

### RAG Pipeline

* Entity Extraction via prompt templates

* Cypher QA Chain to translate NL to structured graph queries

* Vector QA Chain for semantic search over embeddings

### Evaluation

* Food Queries: accurate for daily and monthly requests

* Sleep/Water/Step: retrieval works, but date parsing and filtering need further refinement


## Future work 
* Interactive Reporting Dashboard

* Enhanced Query Understanding (multi-range, relative dates)

* Automated Data Ingestion Pipelines

* User Account & Authentication


# Contact
For questions or issues, please open a GitHub issue or email yaffazka@gmail.com.

Thank you for exploring Samsung Health GraphRAG Explorer!