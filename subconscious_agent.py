import time
import json
import os

AUDIT_LOG_FILE = "/home/ahmed/PALA_v3.1/pala_audit.log"
SUBCONSCIOUS_LOG_FILE = "/home/ahmed/PALA_v3.1/subconscious_events.log"

def analyze_message(message):
    # Simple keyword-based emotional detection (expandable)
    triggers = {
        "sad": "Detected possible sadness.",
        "happy": "Detected possible happiness.",
        "angry": "Detected possible anger.",
        "error": "Detected possible error or system issue.",
        "love": "Detected possible affection."
    }
    events = []
    lower_msg = message.lower()
    for word, event in triggers.items():
        if word in lower_msg:
            events.append(event)
    return events

def monitor_audit_log():
    last_size = 0
    while True:
        if not os.path.exists(AUDIT_LOG_FILE):
            time.sleep(2)
            continue
        with open(AUDIT_LOG_FILE, "r") as f:
            f.seek(last_size)
            new_lines = f.readlines()
            last_size = f.tell()

        for line in new_lines:
            try:
                event = json.loads(line)
                user_input = event.get("event_data", {}).get("user_input", "")
                if user_input:
                    events = analyze_message(user_input)
                    for detected in events:
                        log_entry = {
                            "timestamp": event["timestamp"],
                            "detected_event": detected,
                            "original_message": user_input
                        }
                        with open(SUBCONSCIOUS_LOG_FILE, "a") as out:
                            out.write(json.dumps(log_entry) + "\n")
            except Exception as e:
                continue  # Ignore malformed lines
        time.sleep(2)

if __name__ == "__main__":
    monitor_audit_log()
