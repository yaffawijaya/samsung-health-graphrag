# components/ai_assistant.py - Improved UX with Sample Prompts
import streamlit as st
import time
import os
from modules.utils.db.db_chat_mysql import (
    get_chat_history, push_chat_message
)
from modules.utils.retrieval.graphrag import get_graphrag_agent, set_user_context

def render_ai_assistant():
    # Stylish header
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>🤖 Your Health AI Assistant</h1>"
        "<p style='text-align:center; color:gray;'>Chat with AI about your health data patterns and get personalized insights!</p>",
        unsafe_allow_html=True
    )

    # Guard clauses
    if not st.session_state.get('api_key_valid', False):
        st.warning("🔑 Please provide your OpenAI API key in the sidebar to use the AI Assistant.")
        st.info("👈 Look for 'Step 1: OpenAI API Key' in the sidebar to get started.")
        st.stop()

    if not st.session_state.user_id:
        st.warning("👤 Select a user first in the sidebar.")
        st.stop()

    if not st.session_state.session_id:
        st.warning("💬 Select or create a Chat Session in the sidebar first.")
        st.stop()

    sid   = st.session_state.session_id
    uname = st.session_state.username
    user_id = st.session_state.user_id

    # Set user context for health analytics
    set_user_context(user_id, uname)

    # Initialize agent with API key validation
    if st.session_state.agent_executor is None:
        try:
            # Ensure OpenAI API key is set in environment
            if st.session_state.get('openai_api_key'):
                os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
            
            st.session_state.agent_executor = get_graphrag_agent()
        except ValueError as e:
            st.error(f"❌ Error initializing AI agent: {str(e)}")
            st.info("Please check your OpenAI API key and try again.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.stop()

    agent = st.session_state.agent_executor

    # Load chat history
    if st.session_state.history_loaded_for != sid:
        hist = get_chat_history(sid)
        st.session_state.chat_history = [
            {"role": row.role, "content": row.message}
            for row in hist.itertuples()
        ]
        st.session_state.history_loaded_for = sid
    
    # API Status indicator
    if st.session_state.get('openai_api_key'):
        masked_key = st.session_state.openai_api_key[:8] + "..." + st.session_state.openai_api_key[-4:]
        st.markdown(
            f"""
            <div class="api-status">
                ✅ AI Assistant Ready | Using API Key: {masked_key} | Analyzing health data for {uname}
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Sample Prompts Section (ALWAYS visible regardless of session changes)
    with st.expander("📝 Sample Prompts - Click to Copy", expanded=False):
        st.markdown("**Copy any prompt below and paste it in the chat to get started:**")
        
        # Sample prompts organized by category
        prompt_categories = {
            "🛌 Sleep Analysis": [
                "What does my sleep pattern look like? Are there any concerning trends?",
                "How consistent is my sleep schedule? What days do I sleep the worst?",
                "Based on my sleep data, what recommendations do you have for better rest?"
            ],
            "🍎 Nutrition & Diet": [
                "Analyze my food intake patterns. What are my eating habits like?",
                "What are my most frequently consumed foods and their nutritional impact?",
                "Are there any patterns between my food choices and other health metrics?"
            ],
            "💧 Hydration": [
                "How is my daily water intake? Am I staying properly hydrated?",
                "What days do I drink the least water, and how can I improve?",
                "Is there a correlation between my water intake and activity levels?"
            ],
            "🚶 Physical Activity": [
                "How active am I on average? What's my activity pattern throughout the week?",
                "What are my most and least active days? How can I be more consistent?",
                "Compare my step count with health recommendations. Am I meeting fitness goals?"
            ],
            "📊 Overall Health": [
                "Give me a comprehensive analysis of all my health metrics and overall patterns",
                "What correlations do you see between my sleep, diet, activity, and hydration?",
                "Based on my data, what are 3 specific areas I should focus on improving?"
            ]
        }
        
        for category, prompts in prompt_categories.items():
            st.markdown(f"**{category}**")
            for i, prompt in enumerate(prompts):
                # Create a unique key for each prompt
                prompt_key = f"{category.replace(' ', '_')}_{i}"
                
                # Display prompt in a copyable format
                st.markdown(
                    f"""
                    <div class="sample-prompt" onclick="navigator.clipboard.writeText('{prompt}')">
                        {prompt}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            st.markdown("")  # Add spacing between categories
        
        st.info("💡 **Tip:** Click on any prompt above to copy it, then paste it in the chat input below to start your conversation!")


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
        .api-status {
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            color: #155724;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9em;
            text-align: center;
            border: 1px solid #c3e6cb;
        }
        .warning-notice {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            color: #856404;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            border-left: 4px solid #ffc107;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .sample-prompt {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        .sample-prompt:hover {
            background: #e9ecef;
        }
        .copy-button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 0.8em;
            cursor: pointer;
            margin-left: 10px;
        }
        .copy-button:hover {
            background: #0056b3;
        }
    </style>
    """

    st.markdown(chat_style, unsafe_allow_html=True)

    

    # Important Warning Notice
    st.markdown(
        """
        <div class="warning-notice">
            <h4 style="margin-top: 0; color: #856404;">⚠️ Important Medical Disclaimer</h4>
            <p style="margin-bottom: 0;">
                <strong>This AI assistant analyzes patterns from your health data and provides insights based on general knowledge.</strong><br>
                • Recommendations may not meet medical standards and should not replace professional healthcare advice<br>
                • This is a prototype application for educational and research purposes<br>
                • <strong>Future work:</strong> Integration with medical research papers for more accurate, evidence-based recommendations<br>
                • Always consult healthcare professionals for medical decisions and health concerns
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Sample Prompts Section (only show if no chat history)
    if not st.session_state.chat_history:
        st.markdown(f"### 💬 Start Conversation with {uname}")
        
        with st.expander("📝 Sample Prompts - Click to Copy", expanded=True):
            st.markdown("**Copy any prompt below and paste it in the chat to get started:**")
            
            # Sample prompts organized by category
            prompt_categories = {
                "🛌 Sleep Analysis": [
                    "What does my sleep pattern look like? Are there any concerning trends?",
                    "How consistent is my sleep schedule? What days do I sleep the worst?",
                    "Based on my sleep data, what recommendations do you have for better rest?"
                ],
                "🍎 Nutrition & Diet": [
                    "Analyze my food intake patterns. What are my eating habits like?",
                    "What are my most frequently consumed foods and their nutritional impact?",
                    "Are there any patterns between my food choices and other health metrics?"
                ],
                "💧 Hydration": [
                    "How is my daily water intake? Am I staying properly hydrated?",
                    "What days do I drink the least water, and how can I improve?",
                    "Is there a correlation between my water intake and activity levels?"
                ],
                "🚶 Physical Activity": [
                    "How active am I on average? What's my activity pattern throughout the week?",
                    "What are my most and least active days? How can I be more consistent?",
                    "Compare my step count with health recommendations. Am I meeting fitness goals?"
                ],
                "📊 Overall Health": [
                    "Give me a comprehensive analysis of all my health metrics and overall patterns",
                    "What correlations do you see between my sleep, diet, activity, and hydration?",
                    "Based on my data, what are 3 specific areas I should focus on improving?"
                ]
            }
            
            for category, prompts in prompt_categories.items():
                st.markdown(f"**{category}**")
                for i, prompt in enumerate(prompts):
                    # Create a unique key for each prompt
                    prompt_key = f"{category.replace(' ', '_')}_{i}"
                    
                    # Display prompt in a copyable format
                    st.markdown(
                        f"""
                        <div class="sample-prompt" onclick="navigator.clipboard.writeText('{prompt}')">
                            {prompt}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                st.markdown("")  # Add spacing between categories
            
            st.info("💡 **Tip:** Click on any prompt above to copy it, then paste it in the chat input below to start your conversation!")
        
        st.markdown("---")

    # Render Chat History
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-container'><div class='user-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container'><div class='ai-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # New Input
    user_q = st.chat_input("Ask a question about your health data or use a sample prompt from above:")
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
    Updated with better error handling for API key issues.
    """
    # Enhanced thinking animation
    thinking_container = st.empty()
    thinking_container.markdown(
        """
        <div class='chat-container'><div class='thinking-msg'>
            <em>🧠 Analyzing your health data with AI<span class='dotting'>.</span></em>
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
        # Ensure API key is set
        if st.session_state.get('openai_api_key'):
            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
        
        # Call agent with the context-aware prompt
        res = agent.invoke({"input": prompt})
        ans = res.get("output", "").strip() if res else ""
        
        # If response is empty or generic, provide fallback
        if not ans or len(ans) < 20:
            ans = f"I apologize, but I'm having trouble analyzing your health data right now. Could you try asking about a specific health metric like sleep, nutrition, water intake, or activity level?"
            
    except Exception as e:
        error_msg = str(e).lower()
        if "api" in error_msg and ("key" in error_msg or "authentication" in error_msg):
            ans = "I'm having trouble with the OpenAI API connection. Please check that your API key is valid and has sufficient credits. You can update your API key in the sidebar."
        else:
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