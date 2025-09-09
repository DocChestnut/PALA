# inner_observer.py
#
# This agent is PALA's self-monitoring system, the source of its foundational
# self-awareness. It collects real-time system metrics and publishes them as
# raw data threads for other agents, like the Emotional Core, to consume.
#
# This script runs as a long-running service.

import os
import sys
import time
import json
import psutil
import uuid
import datetime

# --- Configuration ---
BASE_DIR = "/home/ahmed/PALA_v3.1/"
SYSTEM_HEALTH_FILE_PENDING = os.path.join(BASE_DIR, "data_bus", "system_health_pending.json")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")
MASTER_CLOCK_FILE = os.path.join(BASE_DIR, "data_bus", "master_clock.txt")

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

def collect_system_metrics():
    """
    Collects a defined set of real-time system metrics.
    """
    metrics = {
        "timestamp": get_master_clock_timestamp(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    return metrics

def write_metrics_to_pending_file(metrics):
    """
    Writes the collected metrics to a pending file for the Inner Sanctum.
    """
    try:
        # Ensure the data_bus directory exists
        data_bus_dir = os.path.join(BASE_DIR, "data_bus")
        if not os.path.exists(data_bus_dir):
            os.makedirs(data_bus_dir)

        with open(SYSTEM_HEALTH_FILE_PENDING, "w") as f:
            json.dump(metrics, f, indent=4)
        print(f"Wrote SystemHealth metrics to pending file for Inner Sanctum.")
    except IOError as e:
        print(f"Error writing to pending file: {e}", file=sys.stderr)

def run_inner_observer():
    """The main loop for the Inner Observer service."""
    print("Inner Observer is now running...")
    try:
        while True:
            metrics = collect_system_metrics()
            write_metrics_to_pending_file(metrics)
            log_event("SYSTEM_HEALTH_UPDATED", "inner_observer.py", metrics)
            time.sleep(1) # Collect metrics every second
    except KeyboardInterrupt:
        print("\nInner Observer stopped by user.")
    except Exception as e:
        log_event("SYSTEM_ERROR", "inner_observer.py", {"message": f"Inner Observer crashed with error: {e}"})
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_inner_observer()

