import re
from typing import List
from pydantic import BaseModel
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Define the expected schema for structured output.
class HealthEntities(BaseModel):
    names: List[str]

def extract_date(text: str) -> str:
    """Extract a date in YYYY-MM-DD format from the text, if present."""
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if match:
        return match.group(0)
    return None

class HealthGraphRAG():
    """
    Class to manage GraphRAG functions for personal health insights.
    Works with nodes of types Food, Water, Sleep, and Step, all marked with the common label HealthData.
    """
    def __init__(self, user=None):
        self.user = user
        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def create_health_entity_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract health-related entities (food, activity, sleep, biometrics) from text."),
            ("human", "Extract health insights from: {question}"),
        ])
        return prompt | self.llm.with_structured_output(HealthEntities)
    
    def generate_health_query(self, input_query: str) -> str:
        """Generate a regex pattern to search for health-related entities in Neo4j."""
        words = [el for el in remove_lucene_chars(input_query).split() if el]
        regex = "(?i).*" + ".*".join(words) + ".*"
        return regex
    
    def structured_health_retriever(self, question: str) -> str:
        """
        Retrieves structured health insights from the knowledge graph.
        If the question includes a date (in YYYY-MM-DD format), the query is refined to filter nodes by their recordedOn property.
        """
        entity_chain = self.create_health_entity_chain()
        entities = entity_chain.invoke({"question": question})
        
        # Try to extract a date from the question.
        date_str = extract_date(question)
        
        result = ""
        for entity in entities.names:
            regex_query = self.generate_health_query(entity)
            if date_str:
                query_text = """
                MATCH (n)
                WHERE (n:Food OR n:Water OR n:Sleep OR n:Step)
                  AND n.name =~ $query
                  AND n.recordedOn = date($date)
                WITH n
                CALL {
                    WITH n
                    MATCH (n)-[r]->(neighbor)
                    RETURN n.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH n
                    MATCH (n)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + n.name AS output
                }
                RETURN output LIMIT 50
                """
                params = {"query": regex_query, "date": date_str}
            else:
                query_text = """
                MATCH (n)
                WHERE (n:Food OR n:Water OR n:Sleep OR n:Step)
                  AND n.name =~ $query
                WITH n
                CALL {
                    WITH n
                    MATCH (n)-[r]->(neighbor)
                    RETURN n.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH n
                    MATCH (n)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + n.name AS output
                }
                RETURN output LIMIT 50
                """
                params = {"query": regex_query}
            response = self.graph.query(query_text, params)
            result += "\n".join([el['output'] for el in response]) + "\n"
        return result
    
    def create_vector_health_index(self) -> Neo4jVector:
        """
        Creates a vector search index for health-related data.
        Ensure your measurement nodes have the common label HealthData and use the `name` property for text search.
        """
        return Neo4jVector.from_existing_graph(
            OpenAIEmbeddings(),
            search_type="hybrid",
            node_label="HealthData",
            text_node_properties=["name"],
            embedding_node_property="embedding"
        )
    
    def health_retriever(self, question: str) -> str:
        """
        Retrieves relevant health data using both structured and vector-based retrieval.
        """
        print(f"Health Query: {question}")
        vector_index = self.create_vector_health_index()
        unstructured_data = [el.page_content for el in vector_index.similarity_search(question)]
        structured_data = self.structured_health_retriever(question)
        
        return f"""Structured Data:\n{structured_data}\n\nUnstructured Data:\n{'#Document '.join(unstructured_data)}"""
    
    def create_health_search_query(self, chat_history: List, question: str) -> str:
        """
        Creates a search query combining chat history and the health question.
        """
        search_query = ChatPromptTemplate.from_messages([
            ("system", "Rephrase the follow-up question as a standalone health query."),
            ("human", "Chat History: {chat_history}\nQuestion: {question}\nStandalone question:")
        ])
        return search_query.format(chat_history=chat_history, question=question)
