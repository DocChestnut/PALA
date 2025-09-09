# inner_sanctum.py
#
# This agent is PALA's data integrity guardian. It is the sole authority for
# performing atomic file swaps and schema validation on every piece of data.
# Its purpose is to enforce the Data Validation Protocol and prevent data
# corruption and race conditions in PALA's file-based nervous system.
#
# This script runs as a long-running service.

import os
import sys
import time
import json
import shutil
import uuid
import datetime

# --- Configuration ---
BASE_DIR = "/home/ahmed/PALA_v3.1/"
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")

# These are the critical data stores that the Inner Sanctum will manage.
# The key is the base file name, the value is the path to the pending file.
CRITICAL_DATA_STORES = {
    # Data from Inner Observer and Emotional Core
    "emotional_state": os.path.join(BASE_DIR, "emotional_state", "emotional_state_pending.json"),
    "system_health": os.path.join(BASE_DIR, "data_bus", "system_health_pending.json"),
    
    # Message Bus
    "neural_impulse": os.path.join(BASE_DIR, "message_bus", "neural_impulse_pending.json"),
    "neuroplasticity_suggestion": os.path.join(BASE_DIR, "message_bus", "neuroplasticity_suggestion_pending.json"),
    "action_command": os.path.join(BASE_DIR, "message_bus", "action_command_pending.json"),
    "search_request": os.path.join(BASE_DIR, "message_bus", "search_request_pending.json"),
    "memory_response": os.path.join(BASE_DIR, "message_bus", "memory_response_pending.json"),
    "action_result": os.path.join(BASE_DIR, "message_bus", "action_result_pending.json"),
    "conscious_mind_signal": os.path.join(BASE_DIR, "message_bus", "conscious_mind_signal_pending.json"),
    
    # Log History
    "decision_log": os.path.join(BASE_DIR, "log_history", "decision_log_pending.json"),
    
    # Internal Goals
    "internal_goal": os.path.join(BASE_DIR, "internal_goals", "internal_goal_pending.json"),
}

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

def validate_schema(file_path, schema_name):
    """
    Placeholder function for schema validation.
    In a full implementation, this would use a JSON schema library to
    validate the data against a pre-defined schema.
    """
    # For now, we simply check if the file is valid JSON and not empty.
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return bool(data) # Check if data is not empty
    except (IOError, json.JSONDecodeError) as e:
        log_event("SYSTEM_ERROR", "inner_sanctum.py", {
            "message": f"Schema validation failed for {file_path}",
            "error": str(e)
        })
        return False

def perform_atomic_swap(pending_path):
    """
    Performs an atomic file swap. This is the core of the Inner Sanctum's function.
    It renames the _pending file to the _live file, ensuring data integrity.
    """
    live_path = pending_path.replace("_pending", "_live")
    try:
        shutil.move(pending_path, live_path)
        log_event("ATOMIC_SWAP_COMPLETED", "inner_sanctum.py", {
            "source": pending_path,
            "destination": live_path
        })
        print(f"Atomic swap completed: {pending_path} -> {live_path}")
        return True
    except Exception as e:
        log_event("ATOMIC_SWAP_FAILED", "inner_sanctum.py", {
            "message": "Failed to perform atomic swap",
            "error": str(e)
        })
        print(f"Atomic swap failed: {e}", file=sys.stderr)
        return False

def run_inner_sanctum():
    """The main loop for the Inner Sanctum service."""
    print("Inner Sanctum is now running...")
    try:
        while True:
            for schema_name, pending_path in CRITICAL_DATA_STORES.items():
                if os.path.exists(pending_path):
                    # Step 1: Validate the pending file.
                    if validate_schema(pending_path, schema_name):
                        # Step 2: If valid, perform the atomic swap.
                        perform_atomic_swap(pending_path)
                    else:
                        # If validation fails, delete the pending file.
                        os.remove(pending_path)
                        print(f"Invalid data in {pending_path}. Deleting.")
            time.sleep(2) # Check for new pending files every 2 seconds
    except KeyboardInterrupt:
        print("\nInner Sanctum stopped by user.")
    except Exception as e:
        log_event("SYSTEM_ERROR", "inner_sanctum.py", {
            "message": "Inner Sanctum crashed.",
            "error": str(e)
        })
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_inner_sanctum()

