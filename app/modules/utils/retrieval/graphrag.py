# modules/utils/retrieval/graphrag.py
"""
GraphRAG module: builds a GraphRAG QA Agent over the Neo4j health graph.
"""
import os
from pathlib import Path
import toml

from langchain.chat_models import ChatOpenAI
from langchain.tools import tool
from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent, AgentType
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# Load secrets from project root
BASE_DIR = Path(__file__).parents[3]
secrets = toml.load(BASE_DIR / "secrets.toml")

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = secrets['openai']['OPENAI_API_KEY']

# Initialize Neo4jGraph
neo4j_cfg = secrets['neo4j']
graph = Neo4jGraph(
    url=neo4j_cfg['NEO4J_URI'],
    username=neo4j_cfg['NEO4J_USERNAME'],
    password=neo4j_cfg['NEO4J_PASSWORD']
)

# Tool: Cypher-based health QA
@tool("health-cypher-tool", return_direct=True)
def health_cypher_tool(query: str) -> str:
    """
    Answer health-graph queries by translating NL to Cypher and returning a natural response.
    """
    chain = GraphCypherQAChain.from_llm(
        llm=ChatOpenAI(temperature=0, model_name="gpt-4-0613"),
        graph=graph,
        verbose=False,
        allow_dangerous_requests=True
    )
    return chain.run(query)

# Tool: Vector + graph hybrid QA (if Neo4j vector index available)
@tool("health-vector-tool", return_direct=True)
def health_vector_tool(query: str) -> str:
    """
    Answer health-graph questions using hybrid vector retrieval over graph embeddings.
    """
    retriever = graph.as_retriever()  # requires Neo4j vector index
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name="gpt-4-0613"),
        retriever=retriever,
        chain_type="stuff"
    )
    return qa_chain.run(query)

# Build the agent executor
def get_graphrag_agent():
    """
    Construct and return an AgentExecutor with health-cypher and health-vector tools.
    Uses OpenAI_Functions agent type for function calling.
    """
    llm = ChatOpenAI(temperature=0, model_name="gpt-4-0613")
    tools = [health_cypher_tool, health_vector_tool]

    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    return agent_executor
