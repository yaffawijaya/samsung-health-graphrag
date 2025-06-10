# components/ai_assistant.py
import streamlit as st
import time
from modules.utils.db.db_chat_mysql import (
    get_chat_history, push_chat_message
)
from modules.utils.retrieval.graphrag import get_graphrag_agent, set_user_context

def render_ai_assistant():
    # Stylish header
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>🤖 Your Health AI Assistant</h1>"
        "<p style='text-align:center; color:gray;'>Ask anything about your health data, and let me provide detailed analysis!</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Guard clauses
    if not st.session_state.user_id:
        st.warning("Select a user first.")
        st.stop()

    if not st.session_state.session_id:
        st.warning("Select or create a Chat Session in the sidebar first.")
        st.stop()

    sid   = st.session_state.session_id
    uname = st.session_state.username
    user_id = st.session_state.user_id

    # Set user context for health analytics
    set_user_context(user_id, uname)

    if st.session_state.agent_executor is None:
        st.session_state.agent_executor = get_graphrag_agent()
    agent = st.session_state.agent_executor

    if st.session_state.history_loaded_for != sid:
        hist = get_chat_history(sid)
        st.session_state.chat_history = [
            {"role": row.role, "content": row.message}
            for row in hist.itertuples()
        ]
        st.session_state.history_loaded_for = sid

    # Enhanced chat styling with better visual hierarchy
    chat_style = """
    <style>
        .chat-container {
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }
        .user-msg {
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            color: #1565C0;
            padding: 14px 18px;
            border-radius: 18px 18px 4px 18px;
            max-width: 75%;
            width: fit-content;
            text-align: left;
            margin-left: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #E1F5FE;
        }
        .ai-msg {
            background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%);
            color: #2E7D32;
            padding: 14px 18px;
            border-radius: 18px 18px 18px 4px;
            max-width: 80%;
            width: fit-content;
            text-align: left;
            margin-right: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #E8F5E8;
            line-height: 1.6;
            white-space: pre-line;
        }
        .thinking-msg {
            background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
            color: #E65100;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 60%;
            width: fit-content;
            text-align: left;
            margin-right: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #FFF8E1;
            font-style: italic;
        }
        .quick-btn {
            margin: 5px;
            padding: 8px 16px;
            border-radius: 20px;
            border: 2px solid #4B79A1;
            background: white;
            color: #4B79A1;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .quick-btn:hover {
            background: #4B79A1;
            color: white;
        }
    </style>
    """

    st.markdown(chat_style, unsafe_allow_html=True)

    # Quick action buttons for common queries
    if not st.session_state.chat_history:
        st.markdown(f"### 💡 Quick Health Insights for {uname}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🛌 Sleep Analysis", key="sleep_btn", help="Analyze your sleep patterns and quality"):
                user_q = "What does my sleep pattern look like?"
                st.session_state.quick_query = user_q
        
        with col2:
            if st.button("🍎 Nutrition Review", key="nutrition_btn", help="Review your eating habits and nutrition"):
                user_q = "Analyze my food intake and nutrition"
                st.session_state.quick_query = user_q
        
        with col3:
            if st.button("💧 Hydration Check", key="water_btn", help="Check your water intake levels"):
                user_q = "How is my water intake?"
                st.session_state.quick_query = user_q
        
        with col4:
            if st.button("📊 Health Summary", key="summary_btn", help="Get comprehensive health overview"):
                user_q = "Give me a comprehensive health analysis"
                st.session_state.quick_query = user_q
        
        # Additional quick buttons
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if st.button("🚶 Activity Level", key="activity_btn", help="Analyze your step count and activity"):
                user_q = "How active am I?"
                st.session_state.quick_query = user_q
        
        with col6:
            if st.button("😴 Sleep Quality", key="sleep_quality_btn", help="Detailed sleep quality assessment"):
                user_q = "How is my sleep quality?"
                st.session_state.quick_query = user_q
        
        with col7:
            if st.button("🥗 Eating Habits", key="eating_btn", help="Review your eating patterns"):
                user_q = "What are my eating habits like?"
                st.session_state.quick_query = user_q
                
        with col8:
            if st.button("💪 Fitness Goals", key="fitness_btn", help="Check if you're meeting activity goals"):
                user_q = "Am I getting enough exercise?"
                st.session_state.quick_query = user_q
        
        st.markdown("---")

    # Render Chat History
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-container'><div class='user-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container'><div class='ai-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # Handle quick query buttons
    if hasattr(st.session_state, 'quick_query'):
        user_q = st.session_state.quick_query
        del st.session_state.quick_query
        
        # Process the quick query
        st.markdown(f"<div class='chat-container'><div class='user-msg'>{user_q}</div></div>", unsafe_allow_html=True)
        push_chat_message(sid, "user", user_q)
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        
        # Process AI response
        process_ai_response(user_q, uname, sid, agent)
        st.rerun()

    # New Input
    user_q = st.chat_input("Ask a question about your health data:")
    if user_q:
        # Render user's message
        st.markdown(f"<div class='chat-container'><div class='user-msg'>{user_q}</div></div>", unsafe_allow_html=True)
        push_chat_message(sid, "user", user_q)
        st.session_state.chat_history.append({"role": "user", "content": user_q})

        # Process AI response
        process_ai_response(user_q, uname, sid, agent)

def process_ai_response(user_q: str, uname: str, sid: int, agent):
    """
    Process the AI response with enhanced thinking animation and conversation context.
    """
    # Enhanced thinking animation
    thinking_container = st.empty()
    thinking_container.markdown(
        """
        <div class='chat-container'><div class='thinking-msg'>
            <em>🧠 Analyzing your health data<span class='dotting'>.</span></em>
        </div></div>
        <style>
            .dotting::after {
                content: '';
                animation: dots 1.5s steps(5, end) infinite;
            }
            @keyframes dots {
                0%, 20% { content: ''; }
                40% { content: '.'; }
                60% { content: '..'; }
                80%, 100% { content: '...'; }
            }
        </style>
        """, unsafe_allow_html=True
    )

    # Build conversation context from chat history
    conversation_context = ""
    if st.session_state.chat_history:
        # Get last few exchanges for context
        recent_messages = st.session_state.chat_history[-4:]  # Last 4 messages (2 exchanges)
        for i, msg in enumerate(recent_messages):
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_context += f"{role}: {msg['content']}\n"
    
    # Build a context-aware prompt
    if conversation_context:
        prompt = f"""
        Previous conversation:
        {conversation_context}
        
        User's current question: {user_q}
        
        Continue this conversation naturally. Do not start with greetings. Reference previous topics when relevant.
        """
    else:
        # First message in the session
        prompt = f"User {uname} asks: {user_q}"
    
    try:
        # Call agent with the context-aware prompt
        res = agent.invoke({"input": prompt})
        ans = res.get("output", "").strip() if res else ""
        
        # If response is empty or generic, provide fallback
        if not ans or len(ans) < 20:
            ans = f"I apologize, but I'm having trouble analyzing your health data right now. Could you try asking about a specific health metric like sleep, nutrition, water intake, or activity level?"
            
    except Exception as e:
        ans = f"I'm sorry, I encountered an issue while analyzing your health data. Please try asking about a specific health metric like sleep, nutrition, water intake, or steps."

    # Enhanced typing animation
    reply_text = ""
    typing_container = st.empty()
    time.sleep(0.8)  # Longer delay for more natural feel
    thinking_container.empty()

    # Split response into words and show typing effect
    words = ans.split()
    for i, word in enumerate(words):
        reply_text += word + " "
        typing_container.markdown(
            f"<div class='chat-container'><div class='ai-msg'>{reply_text.strip()}</div></div>",
            unsafe_allow_html=True
        )
        
        # Variable typing speed based on word length
        delay = 0.04 if len(word) < 5 else 0.06
        time.sleep(delay)

    # Save assistant reply
    final_response = reply_text.strip()
    push_chat_message(sid, "assistant", final_response)
    st.session_state.chat_history.append({"role": "assistant", "content": final_response})