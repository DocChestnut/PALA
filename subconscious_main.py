# subconscious_main.py
#
# This agent is the central conductor and triage unit for the subconscious mind.
# It receives incoming `NEURAL_IMPULSE` messages and routes them to the
# correct specialized agent for processing.
#
# This script runs as a long-running service.

import os
import sys
import time
import json
import uuid

# --- Configuration ---
BASE_DIR = "/home/ahmed/PALA_v3.1/"
NEURAL_IMPULSE_FILE_LIVE = os.path.join(BASE_DIR, "message_bus", "neural_impulse_live.json")
# This agent will now route to other agents by writing to their respective
# pending files, which are then picked up by the Inner Sanctum.
ACTION_COMMAND_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "action_command_pending.json")
SEARCH_REQUEST_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "search_request_pending.json")
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")


def get_master_clock_timestamp():
    """Reads the current timestamp from the Master Clock file."""
    try:
        with open(MASTER_CLOCK_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def log_event(event_type, source_agent, event_data):
    """A helper function to log events to the pala_audit.log."""
    try:
        with open(AUDIT_LOG_FILE, "a") as f:
            entry = {
                "event_id": str(uuid.uuid4()),
                "timestamp": get_master_clock_timestamp(),
                "event_type": event_type,
                "source_agent": source_agent,
                "event_data": event_data
            }
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error logging to audit file: {e}", file=sys.stderr)

def read_neural_impulse():
    """Reads a new neural impulse from the live file."""
    try:
        if os.path.exists(NEURAL_IMPULSE_FILE_LIVE):
            with open(NEURAL_IMPULSE_FILE_LIVE, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return None

def triage_and_route_impulse(impulse):
    """
    Triage and route the incoming neural impulse to the appropriate agent.
    For this foundational version, all impulses are routed to the Cerebrum.
    """
    # The Subconscious now routes by writing a pending file for another agent.
    # The Cerebrum will be responsible for processing this impulse.
    try:
        # For now, we simply create a new action command and let the Cerebrum
        # pick it up. In a real system, this would be a more complex routing.
        command_payload = {
            "command_id": str(uuid.uuid4()),
            "timestamp": get_master_clock_timestamp(),
            "target_agent": "TheCerebrum",
            "action_type": "process_neural_impulse",
            "payload": impulse
        }
        
        with open(ACTION_COMMAND_FILE_PENDING, "w") as f:
            json.dump(command_payload, f, indent=4)
        
        # Log the routing for auditing
        log_event("NEURAL_IMPULSE_ROUTED", "SubconsciousMain", {
            "impulse_id": impulse.get("impulse_id"),
            "destination_agent": "TheCerebrum",
            "routing_strategy": "default_to_cerebrum"
        })
        print(f"Routed neural impulse '{impulse.get('impulse_id')}' to The Cerebrum.")
        
    except Exception as e:
        log_event("SYSTEM_ERROR", "subconscious_main.py", {"message": f"Error routing impulse: {e}"})
        print(f"Error routing impulse: {e}", file=sys.stderr)

def run_subconscious_main():
    """The main loop for the Subconscious Main service."""
    print("Subconscious Main is now running...")

    try:
        while True:
            impulse = read_neural_impulse()
            if impulse:
                log_event("NEURAL_IMPULSE_RECEIVED", "SubconsciousMain", impulse)
                triage_and_route_impulse(impulse)
                os.remove(NEURAL_IMPULSE_FILE_LIVE)
            
            time.sleep(1) # Poll for new impulses

    except KeyboardInterrupt:
        print("\nSubconscious Main stopped by user.")
    except Exception as e:
        log_event("SYSTEM_ERROR", "subconscious_main.py", {"message": f"Subconscious Main crashed with error: {e}"})
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_subconscious_main()

