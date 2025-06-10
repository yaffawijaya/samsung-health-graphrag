# modules/utils/retrieval/graphrag.py
"""
GraphRAG module: builds a GraphRAG QA Agent over the Neo4j health graph with natural conversation.
"""
import os
from pathlib import Path
import toml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from langchain_community.chat_models import ChatOpenAI
from langchain.tools import tool
from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent, AgentType
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain.prompts import PromptTemplate

# Import database utilities
from modules.utils.db.db_utils_mysql import get_user_data_from_mysql, get_existing_users

# Load secrets from project root
BASE_DIR = Path(__file__).parents[3]
secrets = toml.load(BASE_DIR / "secrets.toml")

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = secrets['openai']['OPENAI_API_KEY']

# Database URL for MySQL queries
cfg = secrets['mysql']
from urllib.parse import quote_plus
password_encoded = quote_plus(cfg['password'])
DB_URL = (
    f"mysql+pymysql://{cfg['user']}:{password_encoded}"
    f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
)

# Initialize Neo4jGraph
neo4j_cfg = secrets['neo4j']
graph = Neo4jGraph(
    url=neo4j_cfg['NEO4J_URI'],
    username=neo4j_cfg['NEO4J_USERNAME'],
    password=neo4j_cfg['NEO4J_PASSWORD']
)

# Global variable to store current user context
_current_user_id = None
_current_username = None

def set_user_context(user_id: int, username: str):
    """Set the current user context for health analytics"""
    global _current_user_id, _current_username
    _current_user_id = user_id
    _current_username = username

# Helper function to get health data context
def get_health_data_summary(user_id: int):
    """Get a summary of user's health data for context"""
    try:
        data = get_user_data_from_mysql(user_id, DB_URL)
        
        summary = {}
        
        # Sleep data summary
        if not data['sleep_hours'].empty:
            sleep_df = data['sleep_hours']
            summary['sleep'] = {
                'avg_hours': sleep_df['total_sleep_h'].mean(),
                'min_hours': sleep_df['total_sleep_h'].min(),
                'max_hours': sleep_df['total_sleep_h'].max(),
                'total_nights': len(sleep_df),
                'consistency': sleep_df['total_sleep_h'].std()
            }
        
        # Food data summary - fix the date column issue
        if not data['food_intake'].empty:
            food_df = data['food_intake'].copy()
            # Handle different date column names
            if 'event_time' in food_df.columns:
                food_df['date'] = pd.to_datetime(food_df['event_time']).dt.date
            elif 'date' not in food_df.columns:
                food_df['date'] = pd.to_datetime('today').date()
            
            daily_calories = food_df.groupby('date')['calories'].sum()
            top_foods = food_df.groupby('food_name')['calories'].sum().head(3)
            
            summary['food'] = {
                'avg_daily_calories': daily_calories.mean(),
                'total_calories': food_df['calories'].sum(),
                'days_tracked': len(daily_calories),
                'food_variety': len(food_df['food_name'].unique()),
                'top_foods': top_foods.to_dict()
            }
        
        # Water data summary
        if not data['water_intake'].empty:
            water_df = data['water_intake']
            if 'event_time' in water_df.columns:
                water_df['date'] = pd.to_datetime(water_df['event_time']).dt.date
            elif 'date' not in water_df.columns:
                water_df['date'] = pd.to_datetime('today').date()
                
            daily_water = water_df.groupby('date')['amount'].sum() if 'date' in water_df.columns else water_df['amount']
            summary['water'] = {
                'avg_daily_ml': daily_water.mean(),
                'total_ml': water_df['amount'].sum(),
                'days_tracked': len(daily_water) if hasattr(daily_water, '__len__') else 1
            }
        
        # Steps data summary
        if not data['step_count'].empty:
            steps_df = data['step_count']
            summary['steps'] = {
                'avg_daily_steps': steps_df['total_steps'].mean(),
                'min_steps': steps_df['total_steps'].min(),
                'max_steps': steps_df['total_steps'].max(),
                'total_steps': steps_df['total_steps'].sum(),
                'days_tracked': len(steps_df)
            }
        
        return summary
    except Exception as e:
        return {"error": str(e)}

@tool("natural-health-chat", return_direct=True)
def natural_health_chat(query: str) -> str:
    """
    Have a natural conversation about health data using both MySQL data and Neo4j graph relationships.
    This tool provides conversational responses rather than templated analysis.
    """
    global _current_user_id, _current_username
    
    if not _current_user_id or not _current_username:
        return "I need to know which user's data to analyze. Please make sure you're logged in."
    
    # Get health data context
    health_summary = get_health_data_summary(_current_user_id)
    
    if "error" in health_summary:
        return f"I'm having trouble accessing your health data right now. Error: {health_summary['error']}"
    
    # Create a strict data availability summary
    available_data = []
    health_context = ""
    
    if 'sleep' in health_summary:
        available_data.append("sleep records")
        sleep = health_summary['sleep']
        health_context += f"Sleep data: {_current_username} has tracked {sleep['total_nights']} nights of sleep, averaging {sleep['avg_hours']:.1f} hours per night (range: {sleep['min_hours']:.1f}-{sleep['max_hours']:.1f} hours). Sleep consistency score: {sleep['consistency']:.1f}.\n"
    
    if 'food' in health_summary:
        available_data.append("food intake records")
        food = health_summary['food']
        health_context += f"Food intake data: Over {food['days_tracked']} days, {_current_username} consumed {food['total_calories']:.0f} total calories (avg: {food['avg_daily_calories']:.0f}/day) across {food['food_variety']} different foods. Top foods: {', '.join(food['top_foods'].keys())}.\n"
    
    if 'water' in health_summary:
        available_data.append("water intake records")
        water = health_summary['water']
        health_context += f"Water intake data: {_current_username} has consumed {water['total_ml']:.0f}ml of water over {water['days_tracked']} days, averaging {water['avg_daily_ml']:.0f}ml per day.\n"
    
    if 'steps' in health_summary:
        available_data.append("step count records")
        steps = health_summary['steps']
        health_context += f"Step count data: Over {steps['days_tracked']} days, {_current_username} walked {steps['total_steps']:,.0f} total steps, averaging {steps['avg_daily_steps']:.0f} steps per day (range: {steps['min_steps']:.0f}-{steps['max_steps']:.0f}).\n"
    
    # Create data availability statement
    data_availability = f"AVAILABLE DATA ONLY: {', '.join(available_data)}. DO NOT mention any other health metrics."
    
    # Create a natural conversation prompt with strict data constraints
    conversation_prompt = f"""
    You are continuing a conversation with {_current_username} about their health data. This is NOT the first interaction.

    STRICT DATA CONSTRAINTS:
    {data_availability}
    
    You ONLY have access to these specific health metrics from their Samsung Health data:
    {health_context}

    User's current question: {query}

    CONVERSATION CONTEXT RULES:
    - This is an ONGOING conversation, NOT a new chat
    - DO NOT start with greetings like "Hey [name]!" unless it's genuinely the first message
    - Reference previous topics naturally when relevant
    - Be conversational and continue the dialogue naturally
    - If the user asks follow-up questions, acknowledge the continuation
    - Use phrases like "Looking at that data", "As I mentioned", "Building on what we discussed" when appropriate

    DATA RULES:
    - ONLY discuss the available data types: {', '.join(available_data)}
    - DO NOT mention heart rate, blood pressure, weight, height, exercise types, or any other health metrics
    - If asked about data you don't have, clearly state "I don't have that data"
    - When listing what data you know, be exact: only mention {', '.join(available_data)}

    Respond naturally as if continuing an ongoing conversation about their health data.
    """
    
    try:
        llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0613")
        response = llm.invoke(conversation_prompt)
        return response.content
    except Exception as e:
        return f"I'm having trouble processing your question right now. Could you try rephrasing it?"

@tool("neo4j-graph-chat", return_direct=True)
def neo4j_graph_chat(query: str) -> str:
    """
    Query the Neo4j graph database for health data relationships and patterns.
    This provides insights from the graph structure and relationships.
    """
    global _current_username
    
    try:
        # Enhance the query with user context
        if _current_username:
            enhanced_query = f"For user with username '{_current_username}': {query}"
        else:
            enhanced_query = query
        
        # Create a custom prompt for more natural graph responses
        cypher_prompt = PromptTemplate(
            input_variables=["question", "schema"],
            template="""
            You are an expert at generating Cypher queries and interpreting results for health data.
            
            Schema: {schema}
            
            User Question: {question}
            
            Generate a Cypher query to answer this question, then provide a natural, conversational response based on the results.
            Focus on patterns, relationships, and insights rather than just raw data.
            """
        )
        
        chain = GraphCypherQAChain.from_llm(
            llm=ChatOpenAI(temperature=0.4, model_name="gpt-4-0613"),
            graph=graph,
            verbose=False,
            allow_dangerous_requests=True,
            cypher_prompt=cypher_prompt
        )
        
        result = chain.run(enhanced_query)
        
        # Post-process the result to make it more conversational
        if result and len(result) > 10:
            conversation_prompt = f"""
            Take this health data query result and rephrase it as a natural, friendly conversation response:
            
            Original result: {result}
            User's question: {query}
            
            Make it sound like you're talking to a friend about their health data. Be encouraging and personalized.
            """
            
            llm = ChatOpenAI(temperature=0.6, model_name="gpt-4-0613")
            natural_response = llm.invoke(conversation_prompt)
            return natural_response.content
        else:
            return "I don't have enough information in the graph database to answer that question. Could you try asking about your sleep, food, water intake, or activity levels?"
            
    except Exception as e:
        return f"I'm having trouble accessing the graph database right now. Let me try to help with your health data another way."

# Build the enhanced agent executor
def get_graphrag_agent():
    """
    Construct and return an AgentExecutor with natural conversation capabilities.
    """
    llm = ChatOpenAI(temperature=0.6, model_name="gpt-4-0613")  # Higher temperature for more natural responses
    tools = [natural_health_chat, neo4j_graph_chat]

    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs={
            "system_message": f"""You are a friendly health AI assistant helping users understand their Samsung Health data.

            Current user: {_current_username if _current_username else 'Unknown'}

            CRITICAL: You ONLY have access to these 4 types of health data:
            1. Sleep records (sleep duration, patterns)
            2. Food intake records (calories, food names)  
            3. Water intake records (daily water consumption)
            4. Step count records (daily steps, activity levels)

            DO NOT mention or claim to have:
            - Heart rate data
            - Blood pressure data  
            - Weight or height data
            - Exercise types or workout data
            - Any other health metrics not listed above

            CONVERSATION FLOW:
            - Maintain context from previous messages in the conversation
            - Only greet the user at the beginning of a NEW session, not every response
            - Use natural conversation transitions and references to previous topics
            - Avoid repetitive greetings like "Hey [name]!" in follow-up responses
            - Continue conversations naturally with phrases like "Looking at that...", "As for your...", "Building on what we discussed..."

            Your personality:
            - Conversational and supportive, like a knowledgeable friend
            - Encouraging about progress, gentle about areas needing improvement
            - Use specific data points naturally in conversation
            - Ask follow-up questions when helpful
            - Avoid templated or clinical responses
            - Be completely honest about data limitations

            When asked what data you have, respond with EXACTLY: "I have access to your sleep records, food intake records, water intake records, and step count records from your Samsung Health data."

            For health-related questions, prefer the natural-health-chat tool as it provides more conversational responses with actual data context.

            If users ask about data you don't have, clearly state: "I don't have that type of data in your Samsung Health records."

            Keep responses natural, personal, and encouraging while being factually accurate about available data."""
        }
    )
    return agent_executor