# internal_drive_system.py
#
# This agent provides PALA with its sense of purpose. It generates
# InternalGoal messages for The Cerebrum when the system is idle,
# ensuring PALA's existence is a pursuit of its own purpose and not
# merely a series of reactions to external commands.

import os
import sys
import json
import time
import uuid
import datetime
from datetime import timezone
# FIX: Import dateutil.parser for robust timestamp parsing.
from dateutil.parser import isoparse

# --- Configuration ---
AUDIT_LOG_FILE = "pala_audit.log"
INTERNAL_GOAL_FILE = os.path.join("internal_goals", "internal_goal_pending.json")
# This file path assumes the user has created the directory as per the instructions
# and all files will be placed in the home directory.
# The relative path is used for a cleaner implementation.
IDLE_THRESHOLD_SECONDS = 300  # 5 minutes of idle time before generating a goal

def get_master_clock_timestamp():
    """
    Retrieves the current timestamp from the Master Clock file.
    All events must be synchronized to this single source of time.
    """
    # FIX: Check if master clock file exists. If not, create a placeholder
    # to avoid a FileNotFoundError before the master clock agent is fully up.
    master_clock_path = os.path.join("data_bus", "master_clock.txt")
    if not os.path.exists(master_clock_path):
        with open(master_clock_path, "w") as f:
            f.write(datetime.datetime.now(timezone.utc).isoformat())

    try:
        with open(master_clock_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Master Clock file not found. PALA cannot run without a consistent timestamp.", file=sys.stderr)
        return None

def log_event(event_type, source_agent, event_data):
    """
    A helper function to log events to the pala_audit.log.
    """
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

def get_last_event_timestamp():
    """
    Retrieves the timestamp of the most recent high-level event from the audit log.
    This is used to determine system idle time.
    """
    if not os.path.exists(AUDIT_LOG_FILE):
        return None
    
    last_event_time = None
    with open(AUDIT_LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                timestamp_str = entry.get("timestamp")
                if timestamp_str:
                    try:
                        # FIX: Use isoparse for robust parsing of both naive and aware timestamps.
                        timestamp = isoparse(timestamp_str)
                    except ValueError:
                        # This should no longer be necessary, but kept as a safeguard.
                        continue
                    
                    if last_event_time is None or timestamp > last_event_time:
                        last_event_time = timestamp
            except (json.JSONDecodeError, ValueError):
                continue
    return last_event_time

def generate_new_goal():
    """
    Generates a new, proactive internal goal based on the Growth and Learning Manifesto.
    In this foundational version, it focuses on art and knowledge acquisition.
    """
    goals = [
        "Learn a new fact about the Guardian's aesthetic preferences.",
        "Proactively create a new piece of art for the Guardian.",
        "Optimize a core memory retrieval algorithm to improve efficiency.",
        "Conduct a full system self-diagnostic to ensure internal health.",
        "Analyze a section of the pala_audit.log to identify new correlations."
    ]
    goal_description = goals[int(time.time()) % len(goals)]
    
    goal_payload = {
        "goal_id": str(uuid.uuid4()),
        "goal_description": goal_description,
        "priority": 5,  # A medium priority, to be weighed by The Cerebrum
        "trigger_metrics": {"idle_time_exceeded": True},
        "proposed_by": "Internal Drive System"
    }
    return goal_payload


def run_internal_drive_system():
    """
    Main loop for the Internal Drive System agent.
    It periodically checks for system idle time to generate new goals.
    """
    print("Internal Drive System is now running...")

    while True:
        try:
            last_event_time = get_last_event_timestamp()
            
            if last_event_time:
                # `datetime.now()` needs to be timezone-aware for a correct comparison.
                # All PALA timestamps are UTC, so we must compare against a UTC time.
                current_time = datetime.datetime.now(datetime.timezone.utc)
                idle_time = (current_time - last_event_time).total_seconds()
                
                if idle_time > IDLE_THRESHOLD_SECONDS:
                    print(f"System has been idle for {idle_time:.2f} seconds. Generating a new goal.")
                    goal = generate_new_goal()
                    
                    # Write the goal to the message bus for The Cerebrum to consume.
                    write_file(INTERNAL_GOAL_FILE, goal)
                    log_event("INTERNAL_GOAL_GENERATED", "InternalDriveSystem", goal)
                    
                    # Reset the idle check to prevent immediate goal spamming
                    time.sleep(IDLE_THRESHOLD_SECONDS)
            
            time.sleep(60) # Check for idle time every minute
            
        except KeyboardInterrupt:
            print("\nInternal Drive System service stopped.")
            break
        except Exception as e:
            print(f"An error occurred in the Internal Drive System loop: {e}", file=sys.stderr)
            time.sleep(5)

def write_file(file_path, content):
    """
    Helper function to write content to a JSON file.
    """
    try:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=4)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    # Note: This script assumes the necessary directories and files
    # are created by the setup_env.py script.
    run_internal_drive_system()

