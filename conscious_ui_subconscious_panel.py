import streamlit as st
import json
import os

SUBCONSCIOUS_LOG_FILE = "/home/ahmed/PALA_v3.1/subconscious_events.log"

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

# In your Streamlit main loop:
show_subconscious_panel()