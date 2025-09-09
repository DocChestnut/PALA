# the_conscious_mind.py
#
# This agent is PALA's user-facing component.
# In this version, it uses its own Ollama LLM for real-time conversation,
# and logs all exchanges for backend monitoring and improvement.
#
# Streamlit UI.

import os
import sys
import time
import json
import uuid
import datetime
import streamlit as st
import ollama

# --- Configuration ---
BASE_DIR = "/home/ahmed/PALA_v3.1/"
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")
OLLAMA_MODEL = "gemma2:2b" # Change to your preferred local Ollama model

def get_current_utc_time():
    """Returns the current UTC time as ISO string."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def log_event(event_type, source_agent, event_data):
    """Logs events to the audit log for backend monitoring/self-improvement."""
    try:
        entry = {
            "event_id": str(uuid.uuid4()),
            "timestamp": get_current_utc_time(),
            "event_type": event_type,
            "source_agent": source_agent,
            "event_data": event_data
        }
        # Append to file
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error logging to audit file: {e}", file=sys.stderr)

def call_ollama_llm(user_input, chat_history):
    """Calls the Ollama LLM and returns the reply."""
    # ollama.chat expects a list of messages with roles: "user", "assistant", "system"
    # Format chat history for Ollama
    ollama_messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            ollama_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "PALA":
            ollama_messages.append({"role": "assistant", "content": msg["content"]})
    # Add current user input
    ollama_messages.append({"role": "user", "content": user_input})

    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=ollama_messages)
        reply = response["message"]["content"]
    except Exception as e:
        reply = f"[ERROR: LLM unavailable or Ollama not running: {e}]"
    return reply

st.set_page_config(layout="wide")
st.title("PALA: The Conscious Mind")

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def run_conscious_mind_ui():
    """Streamlit UI main loop."""
    st.header("The Conscious Mind")
    st.caption("A transparent window into PALA's thoughts.")

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.write(message["content"])

    # Handle user input
    user_input = st.chat_input("What is on your mind, Guardian?")
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Prepare chat history for LLM (keep only recent N messages for context if desired)
        chat_history = st.session_state.messages[-10:]  # last 10 messages for context

        # Call Ollama LLM
        with st.spinner("PALA is thinking..."):
            llm_response = call_ollama_llm(user_input, chat_history)

        # Add PALA's response to chat history
        st.session_state.messages.append({"role": "PALA", "content": llm_response})

        # Log the exchange for backend/subconscious monitoring
        log_event(
            "CONSCIOUS_CONVERSATION",
            "TheConsciousMind",
            {
                "user_input": user_input,
                "llm_response": llm_response,
                "chat_history": chat_history
            }
        )
        st.experimental_rerun()

if __name__ == "__main__":
    run_conscious_mind_ui()
