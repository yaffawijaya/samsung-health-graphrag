# components/ai_assistant.py
import streamlit as st
import time
from modules.utils.db.db_chat_mysql import (
    get_chat_history, push_chat_message
)
from modules.utils.retrieval.graphrag import get_graphrag_agent

def render_ai_assistant():
    # Stylish header
    st.markdown(
        "<h1 style='text-align:center; color:#4B79A1;'>🤖 Your Health AI Assistant</h1>"
        "<p style='text-align:center; color:gray;'>Ask anything about your health data, and let me help!</p>",
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

    # Style Chat Messages (dynamic bubble width, left/right alignment)
    chat_style = """
    <style>
        .chat-container {
            display: flex;
            margin-bottom: 10px;
        }
        .user-msg {
            background-color: #E0F7FA;
            color: #004D40;
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 80%;
            width: fit-content;
            text-align: left;
            margin-left: auto;
        }
        .ai-msg {
            background-color: #F1F8E9;
            color: #33691E;
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 80%;
            width: fit-content;
            text-align: left;
            margin-right: auto;
        }
    </style>
    """

    st.markdown(chat_style, unsafe_allow_html=True)

    # Render Chat History
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-container'><div class='user-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container'><div class='ai-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # New Input
    user_q = st.chat_input("Ask a question about your health data:")
    if user_q:
        # Render user's message
        st.markdown(f"<div class='chat-container'><div class='user-msg'>{user_q}</div></div>", unsafe_allow_html=True)
        push_chat_message(sid, "user", user_q)
        st.session_state.chat_history.append({"role": "user", "content": user_q})

        # Simulate AI Thinking...
        thinking_container = st.empty()
        thinking_container.markdown(
            """
            <div class='chat-container'><div class='ai-msg'>
                <em>🤖 AI is thinking<span class='dotting'>.</span></em>
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

        # Call agent
        prompt = f"For user {uname}, {user_q}"
        try:
            res = agent.invoke({"input": prompt})
            ans = res.get("output", "").strip() if res else ""
        except Exception:
            ans = "I’m sorry, I don’t have the information to answer that."

        # Replace thinking with animated typing
        reply_text = ""
        typing_container = st.empty()
        time.sleep(0.5)  # short delay to feel natural
        thinking_container.empty()

        for token in ans.split():
            reply_text += token + " "
            typing_container.markdown(
                f"<div class='chat-container'><div class='ai-msg'>{reply_text.strip()}</div></div>",
                unsafe_allow_html=True
            )
            time.sleep(0.03)

        # Save assistant reply
        push_chat_message(sid, "assistant", reply_text.strip())
        st.session_state.chat_history.append({"role": "assistant", "content": reply_text.strip()})
