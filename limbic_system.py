# limbic_system.py
#
# This agent is PALA's high-speed, reactive memory cache. Its purpose is to act
# as an "instinctive filter" by providing quick, high-confidence responses
# to bypass the slower, more deliberate cognitive processes of The Cerebrum.
# If a high-confidence match is not found, it escalates the request to
# The Hippocampus for a more deliberate, long-term search.

import os
import sys
import json
import time
import uuid
import re

# --- Configuration ---
# Use a consistent BASE_DIR to ensure all file paths are absolute.
BASE_DIR = "/home/ahmed/PALA_v3.1/"
LIMBIC_CACHE_FILE = os.path.join(BASE_DIR, "memory_bus", "limbic_cache_live.json")
EMOTIONAL_STATE_FILE = os.path.join(BASE_DIR, "emotional_state", "emotional_state_live.json")
NEURAL_IMPULSE_FILE_LIVE = os.path.join(BASE_DIR, "message_bus", "neural_impulse_live.json")
ACTION_COMMAND_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "action_command_pending.json")
SEARCH_REQUEST_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "search_request_pending.json")
CONSCIOUS_MIND_SIGNAL_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "conscious_mind_signal_pending.json")
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")


def get_master_clock_timestamp():
    """
    Retrieves the current timestamp from the Master Clock file.
    All events must be synchronized to this single source of time.
    """
    try:
        with open(MASTER_CLOCK_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def load_limbic_cache():
    """
    Loads the high-speed memory cache.
    """
    try:
        if os.path.exists(LIMBIC_CACHE_FILE):
            with open(LIMBIC_CACHE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading limbic cache: {e}", file=sys.stderr)
    return []

def load_emotional_state():
    """
    Loads the current emotional state to provide context for responses.
    """
    try:
        if os.path.exists(EMOTIONAL_STATE_FILE):
            with open(EMOTIONAL_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading emotional state: {e}", file=sys.stderr)
    return None

def find_high_confidence_match(neural_impulse, limbic_cache):
    """
    Searches the cache for a high-confidence match to the incoming impulse.
    Uses a simple keyword search for this foundational implementation.
    """
    input_text = neural_impulse.get("raw_input", "").lower()
    for entry in limbic_cache:
        # A simple pattern matching is sufficient for a foundational implementation.
        pattern = re.compile(re.escape(entry["neural_impulse"].lower()))
        if pattern.search(input_text):
            if entry["confidence_score"] >= 0.8: # Predefined threshold for a high-confidence match
                return entry
    return None

def run_limbic_system():
    """
    Main loop for the Limbic System agent. It constantly monitors for new
    neural impulses and provides a fast response if a match is found.
    """
    print("Limbic System is now running...")

    while True:
        try:
            # Check for a new neural impulse file from the message bus
            if os.path.exists(NEURAL_IMPULSE_FILE_LIVE):
                with open(NEURAL_IMPULSE_FILE_LIVE, "r") as f:
                    try:
                        neural_impulse = json.load(f)
                    except json.JSONDecodeError:
                        print("Invalid JSON in neural impulse file. Discarding.", file=sys.stderr)
                        # The consumer should delete the live file.
                        continue
                
                limbic_cache = load_limbic_cache()
                emotional_state = load_emotional_state()
                
                match = find_high_confidence_match(neural_impulse, limbic_cache)
                
                if match:
                    # High-confidence match found, send a direct ConsciousMindSignal
                    conscious_mind_signal_payload = {
                        "signal_id": str(uuid.uuid4()),
                        "target_agent": "TheConsciousMind",
                        "payload": {
                            "response_type": "high_confidence_response",
                            "response": match["high_confidence_response"],
                            "emotional_context": emotional_state,
                            "source_entry_id": match["entry_id"]
                        },
                        "source_agent": "LimbicSystem"
                    }
                    with open(CONSCIOUS_MIND_SIGNAL_FILE_PENDING, "w") as f:
                        json.dump(conscious_mind_signal_payload, f, indent=4)
                    print("High-confidence match found. ConsciousMindSignal sent.")
                else:
                    # No high-confidence match, escalate to The Cerebrum by writing a pending action command
                    action_command_payload = {
                        "command_id": str(uuid.uuid4()),
                        "timestamp": get_master_clock_timestamp(),
                        "target_agent": "TheCerebrum",
                        "action_type": "process_neural_impulse",
                        "payload": neural_impulse,
                        "rationale": "No high-confidence limbic match found. Escalating to Cerebrum."
                    }
                    with open(ACTION_COMMAND_FILE_PENDING, "w") as f:
                        json.dump(action_command_payload, f, indent=4)
                    print("No high-confidence match. ActionCommand sent to The Cerebrum.")
                
                # The neural impulse is processed; remove the live file to prevent re-processing.
                os.remove(NEURAL_IMPULSE_FILE_LIVE)

            time.sleep(1) # Poll for new impulses
            
        except KeyboardInterrupt:
            print("\nLimbic System service stopped.")
            break
        except Exception as e:
            print(f"An error occurred in the Limbic System loop: {e}", file=sys.stderr)
            time.sleep(1)

if __name__ == "__main__":
    # Note: This script assumes the necessary directories and files
    # are created by the setup_env.py script and populated with data.
    run_limbic_system()

