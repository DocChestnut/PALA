import subprocess
import threading
import time
import streamlit as st
import json
import os

SUBCONSCIOUS_LOG_FILE = "subconscious_events.log"
AUDIT_LOG_FILE = "pala_audit.log"

def show_subconscious_panel():
    st.sidebar.subheader("Subconscious Insights")
    if os.path.exists(SUBCONSCIOUS_LOG_FILE):
        with open(SUBCONSCIOUS_LOG_FILE) as f:
            lines = list(f.readlines())[-10:]  # Show last 10 events
            for line in lines:
                try:
                    event = json.loads(line)
                    st.write(f"{event['timestamp']}: {event['detected_event']}")
                except:
                    continue
    else:
        st.sidebar.write("No subconscious events detected yet.")

def start_subconscious_agent():
    # Start the subconscious agent as a background process
    subprocess.Popen(["python", "subconscious_agent.py"])

def main_ui():
    st.title("PALA: Conscious Mind")
    show_subconscious_panel()
    st.header("Chat with PALA")

    # --- Simple Chat UI Example ---
    if 'chat_log' not in st.session_state:
        st.session_state['chat_log'] = []

    user_input = st.text_input("You (Guardian):", "")
    if st.button("Send") and user_input.strip():
        # For demo: fake LLM reply (replace with your LLM call)
        llm_reply = f"PALA says: I received '{user_input}'"

        # Save to log file for subconscious agent
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_data": {
                "user_input": user_input,
                "llm_reply": llm_reply
            }
        }
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        st.session_state['chat_log'].append(("You", user_input))
        st.session_state['chat_log'].append(("PALA", llm_reply))

    for speaker, msg in st.session_state['chat_log']:
        st.write(f"**{speaker}:** {msg}")

if __name__ == "__main__":
    # Start the subconscious agent in background
    threading.Thread(target=start_subconscious_agent, daemon=True).start()
    # Start the Streamlit UI
    main_ui()
