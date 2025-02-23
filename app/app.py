import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from modules.rag import HealthGraphRAG
from modules.graph_construction import HealthGraphBuilder
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env file
load_dotenv()

# Retrieve environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

def get_existing_users():
    """Return a list of existing user names from the Neo4j database."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u.name AS name")
        users = [record["name"] for record in result]
    driver.close()
    return users

def process_samsung_health_zip(uploaded_file, user_name):
    """
    Extracts and processes health data from the uploaded Samsung Health zip file.
    """
    save_path = os.path.join("temp_uploads", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    graph_builder = HealthGraphBuilder()
    graph_builder.extract_samsung_health_data(save_path, user_name)

def health_graph_content():
    """
    Populate the graph using extracted Samsung Health data.
    """
    graph_builder = HealthGraphBuilder()
    graph_builder.index_graph()

def reset_health_graph():
    """
    Resets the health knowledge graph.
    """
    graph_builder = HealthGraphBuilder()
    graph_builder.reset_graph()

def get_health_response(question: str, user: str) -> str:
    """
    Retrieves relevant health data using both structured and vector-based retrieval.
    The selected user is passed to the RAG so that only that user's data is searched.
    """
    # Initialize HealthGraphRAG with the chosen user
    rag = HealthGraphRAG(user=user)
    search_query = rag.create_health_search_query(st.session_state.chat_history, question)

    template = """Answer the question based only on the following health context:
    {context}

    Question: {question}
    Use natural language and be concise.
    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        RunnableParallel(
            {"context": lambda x: rag.health_retriever(question), "question": RunnablePassthrough()}
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({"chat_history": st.session_state.chat_history, "question": question})

def init_health_ui():
    """
    Initializes the Streamlit UI for the Health RAG application.
    Now includes a dropdown to select an existing user from Neo4j.
    """
    st.set_page_config(page_title="Health RAG Assistant", layout="wide")
    st.title("Health RAG Assistant")
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I can help analyze your health data. Ask me anything!")
        ]
    
    user_query = st.chat_input("Ask a health-related question...")
    
    with st.sidebar:
        st.image("./app/assets/graphrag-samsunghealth.png", width=200)
        st.header("Manage Health Graph")
        st.write("Upload your Samsung Health data and manage the graph database.")
        
        existing_users = get_existing_users()
        if existing_users:
            selected_user = st.selectbox("Select Existing User", existing_users)
        else:
            selected_user = ""
        
        new_user = st.text_input("Or enter new User Name", "")
        user_name = new_user if new_user else selected_user
        
        uploaded_file = st.file_uploader("Upload Samsung Health ZIP", type=["zip"])
        
        if uploaded_file and user_name:
            if st.button("Process & Populate Graph"):
                process_samsung_health_zip(uploaded_file, user_name)
                health_graph_content()
        
        if st.button("Reset Graph"):
            reset_health_graph()
    
    if user_query:
        if not user_name:
            st.error("Please select or enter a user name from the sidebar.")
        else:
            response = get_health_response(user_query, user_name)
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            st.session_state.chat_history.append(AIMessage(content=response))
    
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)

if __name__ == "__main__":
    init_health_ui()
