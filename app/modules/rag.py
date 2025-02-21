from typing import List
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class HealthGraphRAG():
    """
    Class to manage GraphRAG functions for personal health insights
    """
    def __init__(self):
        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def create_health_entity_chain(self):
        """
        Extracts health-related entities (food, exercise, sleep, etc.) from user queries
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract health-related entities (food, activity, sleep, biometrics) from text."),
            ("human", "Extract health insights from: {question}"),
        ])
        return prompt | self.llm.with_structured_output(None) # Entities
    
    def generate_health_query(self, input_query: str) -> str:
        """
        Generate a query to search for health-related entities in Neo4j
        """
        words = [el for el in remove_lucene_chars(input_query).split() if el]
        return " AND ".join([f"{word}~2" for word in words])
    
    def structured_health_retriever(self, question: str) -> str:
        """
        Retrieves structured health insights from the knowledge graph
        """
        entity_chain = self.create_health_entity_chain()
        entities = entity_chain.invoke({"question": question})
        
        result = ""
        for entity in entities.names:
            response = self.graph.query(
                """
                CALL db.index.fulltext.queryNodes('health_data', $query, {limit:2})
                YIELD node, score
                CALL {
                    WITH node
                    MATCH (node)-[r]->(neighbor)
                    RETURN node.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                    UNION ALL
                    WITH node
                    MATCH (node)<-[r]-(neighbor)
                    RETURN neighbor.name + ' - ' + type(r) + ' -> ' + node.name AS output
                }
                RETURN output LIMIT 50
                """,
                {"query": self.generate_health_query(entity)},
            )
            result += "\n".join([el['output'] for el in response])
        return result
    
    def create_vector_health_index(self) -> Neo4jVector:
        """
        Creates a vector search index for health-related data
        """
        return Neo4jVector.from_existing_graph(
            OpenAIEmbeddings(),
            search_type="hybrid",
            node_label="HealthData",
            text_node_properties=["description"],
            embedding_node_property="embedding"
        )
    
    def health_retriever(self, question: str) -> str:
        """
        Retrieves relevant health data using structured and vector-based retrieval
        """
        print(f"Health Query: {question}")
        vector_index = self.create_vector_health_index()
        unstructured_data = [el.page_content for el in vector_index.similarity_search(question)]
        structured_data = self.structured_health_retriever(question)
        
        return f"""Structured Data:\n{structured_data}\n\nUnstructured Data:\n{'#Document '.join(unstructured_data)}"""
    
    def create_health_search_query(self, chat_history: List, question: str) -> str:
        """
        Creates a search query combining chat history and health question
        """
        search_query = ChatPromptTemplate.from_messages([
            ("system", "Rephrase the follow-up question as a standalone health query."),
            ("human", "Chat History: {chat_history}\nQuestion: {question}\nStandalone question:")
        ])
        return search_query.format(chat_history=chat_history, question=question)
