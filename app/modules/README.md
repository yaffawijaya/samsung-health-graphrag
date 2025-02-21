# Samsung Health GraphRAG - Modules Documentation

## Overview
The `modules` directory is the initial phase of development for the **Samsung Health GraphRAG** project. This folder contains various scripts intended to support **graph construction, data cleaning, and retrieval-augmented generation (RAG)**.

Currently, these modules are in the early stages and **not fully functional**. The development of these components is ongoing, and future updates will refine their functionality.

## Directory Structure
```
Y:\Developer\projects\samsunghealth-graphrag\app\modules
│-- cleaning.py               # Placeholder for data cleaning module
│-- graph_construction.py     # Early-stage implementation of graph construction
│-- rag.py                    # Initial attempt at Retrieval-Augmented Generation (RAG)
```

## Module Descriptions

### 1. `cleaning.py`
- **Status:** Empty placeholder
- **Purpose:** Will eventually handle preprocessing and cleaning of raw Samsung Health data.
- **Planned Features:**
  - Data validation and format correction.
  - Handling missing values and standardizing entries.
  - Preparing datasets for ingestion into the graph database.

### 2. `graph_construction.py`
- **Status:** Partially implemented
- **Purpose:** Implements the foundation for constructing the knowledge graph using **Neo4j**.
- **Current Implementation:**
  - Contains basic graph-building logic.
  - Defines early structures for storing health-related relationships.
- **Planned Features:**
  - Complete integration with Samsung Health data.
  - Optimization for efficient querying and retrieval.
  - Error handling and robust logging.

### 3. `rag.py`
- **Status:** Early implementation, requires refinement.
- **Purpose:** Supports Retrieval-Augmented Generation (RAG) for querying Samsung Health data.
- **Current Implementation:**
  - Basic retrieval logic for fetching relevant health data.
  - Early version of natural language query processing.
- **Planned Features:**
  - Full integration with **LangChain** and OpenAI models.
  - Context-aware health data retrieval.
  - Improved accuracy and response generation.

## Development Roadmap
- [ ] Implement data cleaning logic in `cleaning.py` so it can get the proper user's health data.
- [ ] Finalize graph schema and improve indexing in `graph_construction.py`.
- [ ] Optimize retrieval methods and enhance AI-driven responses in `rag.py`.
- [ ] Conduct testing and debugging across all modules.


### **Contact & Support**
For any questions, please reach out via GitHub issues or email **yaffazka@gmail.com**.