import json
import os
import streamlit as st
from integrate_agent import run_scenario_agent, query_mesa_agent

st.set_page_config(page_title="Banking Agent Chat", layout="centered")
st.title("💬 Banking Agent ")

CHAT_FILE = "chat_history.json"

# REMOVED: Loading existing chat from file
# Always start with a fresh session
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Function to save chat to file (optional - you can remove this too if you don't want to save)
def save_chat():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state["messages"], f, indent=2, ensure_ascii=False)

# User input
if prompt := st.chat_input("Ask something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Decide which agent to call
    if "scenario" in prompt.lower():
        scenario_results = run_scenario_agent()
        response = f"✅ Generated {len(scenario_results['scenarios'])} scenarios. Check console/logs for details."
    else:
        # Behavioral/RAG agent
        answer, shock = query_mesa_agent(prompt)
        response = f"{answer} (Media shock: {shock})"

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(response)

    # Save message in session state only (removed file saving if you want completely fresh sessions)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    
    # Optional: If you still want to save to file but want fresh sessions on each opening,
    # you can remove the save_chat() call below
    # save_chat()