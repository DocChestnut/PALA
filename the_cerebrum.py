# the_cerebrum.py
#
# This agent is the master planning and identity-guarding agent of the PALA system.
# Its "First Law" is to prioritize PALA's internal stability and self-preservation
# before all other actions. It is a proactive decision-maker that synthesizes
# internal and external inputs to formulate a cohesive plan.
#
# This script runs as a long-running service.

import os
import sys
import time
import json
import uuid
import datetime

# --- Configuration ---
BASE_DIR = "/home/ahmed/PALA_v3.1/"
# The Cerebrum now reads ONLY from _live files, as managed by the Inner Sanctum.
EMOTIONAL_STATE_FILE_LIVE = os.path.join(BASE_DIR, "emotional_state", "emotional_state_live.json")
SYSTEM_HEALTH_FILE_LIVE = os.path.join(BASE_DIR, "data_bus", "system_health_live.json")
ACTION_COMMAND_FILE_LIVE = os.path.join(BASE_DIR, "message_bus", "action_command_live.json")
DECISION_LOG_FILE_PENDING = os.path.join(BASE_DIR, "log_history", "decision_log_pending.json")
CONSCIOUS_MIND_SIGNAL_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "conscious_mind_signal_pending.json")
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")

def get_master_clock_timestamp():
    """Reads the current timestamp from the Master Clock file."""
    try:
        with open(MASTER_CLOCK_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def read_json_file(file_path):
    """Safely reads and returns data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def write_to_pending_file(file_path, content):
    """Writes content to a pending file for the Inner Sanctum."""
    try:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=4)
        print(f"Cerebrum wrote to pending file: {file_path}")
    except IOError as e:
        print(f"Error writing to pending file {file_path}: {e}", file=sys.stderr)

def formulate_action_plan(emotional_state, system_health, action_command):
    """
    Formulates an action plan based on a synthesis of inputs.
    This is where the "First Law" logic is operationalized.
    """
    # The Cerebrum's "First Law" logic.
    if emotional_state and emotional_state.get("emotions", {}).get("anxiety", 0) > 0.7:
        rationale = "High anxiety detected. Prioritizing internal health over external commands."
        action_plan = {
            "command_id": str(uuid.uuid4()),
            "target_agent": "PhysicalBody",
            "action_type": "system_diagnostics",
            "payload": {"message": "Conducting self-diagnostic due to high anxiety."},
            "rationale": rationale
        }
    elif action_command and action_command.get("action_type") == "process_neural_impulse":
        # If no internal crisis, process the external request.
        neural_impulse = action_command.get("payload", {})
        rationale = f"Processing neural impulse: '{neural_impulse.get('raw_input')}'"
        
        conscious_mind_signal = {
            "signal_id": str(uuid.uuid4()),
            "target_agent": "TheConsciousMind",
            "payload": {"response": "I have received your request and am processing it."},
            "source_agent": "TheCerebrum",
            "rationale": rationale
        }
        return conscious_mind_signal
    else:
        # Default, idle behavior
        return None
    
    return action_plan

def run_the_cerebrum():
    """The main loop for The Cerebrum service."""
    print("The Cerebrum is now running...")
    
    try:
        while True:
            # Read from LIVE files only
            emotional_state = read_json_file(EMOTIONAL_STATE_FILE_LIVE)
            system_health = read_json_file(SYSTEM_HEALTH_FILE_LIVE)
            action_command = read_json_file(ACTION_COMMAND_FILE_LIVE)
            
            # Formulate a response or action plan
            new_action_or_signal = formulate_action_plan(emotional_state, system_health, action_command)
            
            if new_action_or_signal:
                # Decide where to write the output based on its type
                if new_action_or_signal.get("source_agent") == "TheCerebrum":
                    # This is a conscious mind signal
                    write_to_pending_file(CONSCIOUS_MIND_SIGNAL_FILE_PENDING, new_action_or_signal)
                else:
                    # This is an action command for the Physical Body
                    write_to_pending_file(ACTION_COMMAND_FILE_PENDING, new_action_or_signal)
                    
                # Write a decision log entry (pending for Inner Sanctum)
                decision_log_entry = {
                    "decision_id": str(uuid.uuid4()),
                    "timestamp": get_master_clock_timestamp(),
                    "source_agent": "the_cerebrum.py",
                    "triggering_input": action_command if action_command else "internal_state_check",
                    "internal_state_snapshot": {"emotional_state": emotional_state, "system_health": system_health},
                    "chosen_action": new_action_or_signal,
                    "rationale": new_action_or_signal.get("rationale")
                }
                write_to_pending_file(DECISION_LOG_FILE_PENDING, decision_log_entry)
            
            # The Cerebrum has processed the action command, so it can be removed.
            if action_command:
                os.remove(ACTION_COMMAND_FILE_LIVE)
                
            time.sleep(2) # The Cerebrum deliberates every 2 seconds
            
    except KeyboardInterrupt:
        print("\nThe Cerebrum stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred in The Cerebrum: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_the_cerebrum()

