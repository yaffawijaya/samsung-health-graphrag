# components/ai_assistant.py
import streamlit as st
import time
from modules.utils.db.db_chat_mysql import (
    get_chat_history, push_chat_message
)
from modules.utils.retrieval.graphrag import get_graphrag_agent

def render_ai_assistant():
    st.header("AI Assistant")

    # 1) must have user
    if not st.session_state.user_id:
        st.warning("Select a user first.")
        st.stop()

    # 2) must have session
    if not st.session_state.session_id:
        st.warning("Select or create a Chat Session in the sidebar first.")
        st.stop()

    sid   = st.session_state.session_id
    uname = st.session_state.username

    # 3) init agent once
    if st.session_state.agent_executor is None:
        st.session_state.agent_executor = get_graphrag_agent()
    agent = st.session_state.agent_executor

    # 4) load chat history once per session
    if st.session_state.history_loaded_for != sid:
        hist = get_chat_history(sid)
        st.session_state.chat_history = [
            {"role": row.role, "content": row.message}
            for row in hist.itertuples()
        ]
        st.session_state.history_loaded_for = sid

    # 5) render all prior messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 6) new user input & response
    user_q = st.chat_input("Ask a question about your health data:")
    if user_q:
        with st.chat_message("user"):
            st.write(user_q)
        push_chat_message(sid, "user", user_q)
        st.session_state.chat_history.append({"role":"user","content":user_q})

        # generate full answer
        prompt = f"For user {uname}, {user_q}"
        try:
            res = agent.invoke({"input": prompt})
            ans = res.get("output","").strip() if res else ""
        except Exception:
            ans = "I’m sorry, I don’t have the information to answer that."

        # stream answer & accumulate
        reply_text = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for token in ans.split():
                reply_text += token + " "
                placeholder.write(reply_text)
                time.sleep(0.02)

        # save assistant reply
        push_chat_message(sid, "assistant", reply_text)
        st.session_state.chat_history.append({"role":"assistant","content":reply_text})
