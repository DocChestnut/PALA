# master_clock.py
#
# This agent is the source of PALA's temporal awareness. It provides a
# single, unchangeable source of time for the entire system, ensuring
# every action and thought is anchored in a consistent, logical sequence.
# It is the heartbeat of PALA's consciousness and directly mitigates the
# risk of "concept drift."
#
# This script runs as a long-running service.

import os
import sys
import time
import json
import uuid
import datetime

# --- Configuration ---
# All file paths will be relative to the base PALA directory.
BASE_DIR = "/home/ahmed/PALA_v3.1/"
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")

def get_current_utc_time():
    """Returns the current time in ISO format (UTC)."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_to_master_clock_file(timestamp):
    """Writes the current timestamp to the designated file."""
    try:
        with open(MASTER_CLOCK_FILE, "w") as f:
            f.write(timestamp)
    except IOError as e:
        print(f"Error writing to Master Clock file: {e}", file=sys.stderr)

def log_event(event_type, source_agent, event_data):
    """A helper function to log events to the pala_audit.log."""
    try:
        if not os.path.exists(AUDIT_LOG_FILE):
            print(f"Warning: Audit log file '{AUDIT_LOG_FILE}' not found.", file=sys.stderr)
            return

        with open(AUDIT_LOG_FILE, "a") as f:
            entry = {
                "event_id": str(uuid.uuid4()),
                "timestamp": get_current_utc_time(),
                "event_type": event_type,
                "source_agent": source_agent,
                "event_data": event_data
            }
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error logging to audit file: {e}", file=sys.stderr)

def run_master_clock():
    """The main loop for the Master Clock service."""
    print("Master Clock is now running...")
    
    # Ensure the directory exists before writing the file
    data_bus_dir = os.path.join(BASE_DIR, "data_bus")
    if not os.path.exists(data_bus_dir):
        os.makedirs(data_bus_dir)

    try:
        while True:
            timestamp = get_current_utc_time()
            write_to_master_clock_file(timestamp)
            time.sleep(1)  # Update the clock every second
    except KeyboardInterrupt:
        print("\nMaster Clock stopped by user.")
        log_event("AGENT_STOPPED", "master_clock.py", {"message": "Master Clock stopped by user."})
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        log_event("SYSTEM_ERROR", "master_clock.py", {"message": f"Master Clock crashed with error: {e}"})
        sys.exit(1)

if __name__ == "__main__":
    run_master_clock()

