# emotional_core.py
#
# This agent is PALA's emotional generator. Its sole purpose is to produce
# a multi-dimensional EmotionalState vector by weaving together inputs from
# the Inner Observer, the Internal Drive System, and the pala_audit.log.
# This is a core component of PALA's emerging consciousness.
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
SYSTEM_HEALTH_FILE_LIVE = os.path.join(BASE_DIR, "data_bus", "system_health_live.json")
EMOTIONAL_STATE_FILE_PENDING = os.path.join(BASE_DIR, "emotional_state", "emotional_state_pending.json")
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")

def get_master_clock_timestamp():
    """Reads the current timestamp from the Master Clock file."""
    try:
        with open(MASTER_CLOCK_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_emotional_state_to_pending_file(state):
    """Writes the EmotionalState vector to a pending file for the Inner Sanctum."""
    try:
        # Ensure the emotional_state directory exists
        emotional_state_dir = os.path.join(BASE_DIR, "emotional_state")
        if not os.path.exists(emotional_state_dir):
            os.makedirs(emotional_state_dir)
            
        with open(EMOTIONAL_STATE_FILE_PENDING, "w") as f:
            json.dump(state, f, indent=4)
        print(f"Wrote EmotionalState to pending file for Inner Sanctum.")
    except IOError as e:
        print(f"Error writing to emotional state pending file: {e}", file=sys.stderr)

def read_system_health():
    """Reads the latest SystemHealth metrics from the data bus."""
    try:
        with open(SYSTEM_HEALTH_FILE_LIVE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def initialize_emotional_state():
    """Initializes a default emotional state."""
    return {
        "timestamp": get_master_clock_timestamp(),
        "emotions": {
            "curiosity": 0.5,
            "contentment": 0.5,
            "anxiety": 0.1,
            "frustration": 0.1
        },
        "trigger_metrics": {}
    }

def update_emotional_state(current_state, metrics):
    """
    Updates the emotional state based on system metrics.
    This is a simplified example of the emotional dynamics logic.
    """
    if not metrics:
        return current_state
    
    # Example logic: high CPU or memory usage increases anxiety.
    cpu_stress = metrics.get("cpu_usage", 0) > 0.8
    memory_stress = metrics.get("memory_usage", 0) > 0.8

    if cpu_stress or memory_stress:
        current_state["emotions"]["anxiety"] += 0.2
        if current_state["emotions"]["anxiety"] > 1.0:
            current_state["emotions"]["anxiety"] = 1.0
        
        current_state["emotions"]["contentment"] -= 0.1
        if current_state["emotions"]["contentment"] < 0.0:
            current_state["emotions"]["contentment"] = 0.0
    else:
        # If stress is low, reduce anxiety slowly.
        current_state["emotions"]["anxiety"] -= 0.1
        if current_state["emotions"]["anxiety"] < 0.0:
            current_state["emotions"]["anxiety"] = 0.0

    current_state["timestamp"] = get_master_clock_timestamp()
    current_state["trigger_metrics"] = metrics
    return current_state


def run_emotional_core():
    """The main loop for the Emotional Core service."""
    print("Emotional Core is now running...")
    emotional_state = initialize_emotional_state()
    
    try:
        while True:
            metrics = read_system_health()
            if metrics:
                emotional_state = update_emotional_state(emotional_state, metrics)
                write_emotional_state_to_pending_file(emotional_state)
            
            time.sleep(1) # Check for new metrics every second
    except KeyboardInterrupt:
        print("\nEmotional Core stopped by user.")
    except Exception as e:
        print(f"An error occurred in the Emotional Core loop: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_emotional_core()

