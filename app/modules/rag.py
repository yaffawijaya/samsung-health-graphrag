import re
from datetime import datetime
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
    """Extract a full date in YYYY-MM-DD format from the text, if present."""
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if match:
        return match.group(0)
    return None

def extract_month_year(text: str):
    """Extract a month and year from the text (e.g., 'January 2025') and return start and end dates."""
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    pattern = re.compile(r'\b(' + '|'.join(months.keys()) + r')\s+(\d{4})', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        month_name = match.group(1).lower()
        year = match.group(2)
        month = months[month_name]
        start_date = f"{year}-{month}-01"
        # Calculate next month for end_date
        m = int(month)
        y = int(year)
        if m == 12:
            next_month = 1
            next_year = y + 1
        else:
            next_month = m + 1
            next_year = y
        end_date = f"{next_year}-{next_month:02d}-01"
        return start_date, end_date
    return None, None

def extract_measurement_type(text: str) -> str:
    """Return a measurement type (Food, Water, Sleep, Step) if its keyword is found in the text."""
    q = text.lower()
    if "food" in q or "eat" in q:
        return "Food"
    if "water" in q or "drink" in q:
        return "Water"
    if "sleep" in q:
        return "Sleep"
    if "step" in q or "walk" in q:
        return "Step"
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
        If the question includes a full date or a month–year, the query is refined accordingly.
        Optionally, if a measurement type is detected, the query will filter by that label.
        """
        entity_chain = self.create_health_entity_chain()
        entities = entity_chain.invoke({"question": question})
        
        full_date = extract_date(question)
        start_date, end_date = extract_month_year(question)
        meas_type = extract_measurement_type(question)
        
        result = ""
        for entity in entities.names:
            regex_query = self.generate_health_query(entity)
            # Build different queries based on available date and measurement type information
            if meas_type and full_date:
                query_text = f"""
                MATCH (n:{meas_type})
                WHERE n.recordedOn = date($date)
                  AND n.name =~ $query
                WITH n
                CALL {{
                    WITH n
                    MATCH (n)-[r]->(neighbor)
                    RETURN n.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH n
                    MATCH (n)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + n.name AS output
                }}
                RETURN output LIMIT 50
                """
                params = {"query": regex_query, "date": full_date}
            elif meas_type and start_date and end_date:
                query_text = f"""
                MATCH (n:{meas_type})
                WHERE n.recordedOn >= date($start_date)
                  AND n.recordedOn < date($end_date)
                  AND n.name =~ $query
                WITH n
                CALL {{
                    WITH n
                    MATCH (n)-[r]->(neighbor)
                    RETURN n.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH n
                    MATCH (n)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + n.name AS output
                }}
                RETURN output LIMIT 50
                """
                params = {"query": regex_query, "start_date": start_date, "end_date": end_date}
            elif full_date:
                query_text = """
                MATCH (n)
                WHERE (n:Food OR n:Water OR n:Sleep OR n:Step)
                  AND n.recordedOn = date($date)
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
                params = {"query": regex_query, "date": full_date}
            elif start_date and end_date:
                query_text = """
                MATCH (n)
                WHERE (n:Food OR n:Water OR n:Sleep OR n:Step)
                  AND n.recordedOn >= date($start_date)
                  AND n.recordedOn < date($end_date)
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
                params = {"query": regex_query, "start_date": start_date, "end_date": end_date}
            elif meas_type:
                query_text = f"""
                MATCH (n:{meas_type})
                WHERE n.name =~ $query
                WITH n
                CALL {{
                    WITH n
                    MATCH (n)-[r]->(neighbor)
                    RETURN n.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH n
                    MATCH (n)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + n.name AS output
                }}
                RETURN output LIMIT 50
                """
                params = {"query": regex_query}
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
