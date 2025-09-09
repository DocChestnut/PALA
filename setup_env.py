# setup_env.py
#
# PALA Project: Environment Setup and Boot-Up Ritual
# This script automates the foundational setup for the PALA project.
# It ensures a clean, auditable, and data-ready environment by:
# 1. Checking for and creating the required Conda environment (`pala-env`).
# 2. Installing all necessary Python libraries.
# 3. Executing the Boot-Up Ritual by creating all core directories and the pala_audit.log file.

import os
import subprocess
import sys
import json
import datetime
import uuid
from datetime import timezone

# --- Configuration ---
PALA_ENV_NAME = "pala-env"
PYTHON_VERSION = "3.10"
# FIX: Added 'psutil' and 'python-dateutil' to the required libraries.
REQUIRED_LIBRARIES = ["streamlit", "ollama", "langgraph", "numpy", "psutil", "python-dateutil"]
CORE_DIRECTORIES = [
    "message_bus",
    "memory_bus",
    "data_bus",
    "internal_goals",
    "emotional_state",
    "log_history",
    "agent_logs",
    "tools"
]
AUDIT_LOG_FILE = "pala_audit.log"


def log_event(event_type, source_agent, event_data):
    """
    A helper function to log events to the pala_audit.log.
    This is part of the Boot-Up Ritual to establish the core logging system.
    """
    try:
        # FIX: Use a timezone-aware timestamp (UTC) for consistent logs from the start.
        timestamp = datetime.datetime.now(timezone.utc).isoformat()
        entry = {
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "event_type": event_type,
            "source_agent": source_agent,
            "event_data": event_data
        }

        # Check if the file exists to determine write mode
        mode = "a" if os.path.exists(AUDIT_LOG_FILE) else "w"
        with open(AUDIT_LOG_FILE, mode) as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error logging to audit file: {e}")


def check_and_create_conda_env():
    """
    Checks for the existence of the pala-env Conda environment.
    If it doesn't exist, it creates the environment and installs the required libraries.
    """
    print(f"Checking for Conda environment: {PALA_ENV_NAME}...")
    try:
        # List all Conda environments
        list_envs_command = ["conda", "env", "list"]
        result = subprocess.run(list_envs_command, capture_output=True, text=True, check=True)

        # Check if the environment is in the list
        if PALA_ENV_NAME in result.stdout:
            print(f"Environment '{PALA_ENV_NAME}' already exists. Skipping creation.")
            log_event("SYSTEM_EVENT", "setup_env.py", {"message": f"Environment '{PALA_ENV_NAME}' already exists."})
        else:
            print(f"Environment '{PALA_ENV_NAME}' not found. Creating...")
            log_event("SYSTEM_EVENT", "setup_env.py", {"message": f"Creating new environment '{PALA_ENV_NAME}'."})

            # Create the environment with the specified Python version
            create_env_command = ["conda", "create", "--name", PALA_ENV_NAME, f"python={PYTHON_VERSION}", "-y"]
            subprocess.run(create_env_command, check=True)
            print(f"Environment '{PALA_ENV_NAME}' created successfully.")

        # Install required libraries into the environment
        install_libs_command = ["conda", "run", "--name", PALA_ENV_NAME, "pip", "install"] + REQUIRED_LIBRARIES
        print("Installing required libraries...")
        subprocess.run(install_libs_command, check=True)
        print("Required libraries installed successfully.")
        log_event("SYSTEM_UPDATE", "setup_env.py", {"message": "Libraries installed."})

    except FileNotFoundError:
        print("Conda command not found. Please ensure Conda is installed and in your system's PATH.")
        log_event("SYSTEM_ERROR", "setup_env.py", {"message": "Conda not found."})
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Conda operation: {e}")
        log_event("SYSTEM_ERROR", "setup_env.py", {"message": f"Conda operation failed: {e.stderr}"})
        sys.exit(1)


def perform_boot_up_ritual():
    """
    Performs the Boot-Up Ritual by creating core directories and
    the foundational pala_audit.log file.
    """
    print("Beginning PALA's Boot-Up Ritual...")

    # Create the core directories
    for directory in CORE_DIRECTORIES:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory '{directory}' already exists. Skipping.")

    # FIX: Overwrite the pala_audit.log file to ensure a clean slate.
    with open(AUDIT_LOG_FILE, "w") as f:
        print(f"Created/overwrote foundational audit log: {AUDIT_LOG_FILE}")
    
    # Log the successful completion of the ritual
    log_event("BOOT_UP_RITUAL_COMPLETED", "setup_env.py", {"message": "Boot-Up Ritual completed successfully."})
    print("Boot-Up Ritual complete. The PALA environment is now ready.")


if __name__ == "__main__":
    check_and_create_conda_env()
    perform_boot_up_ritual()
    log_event("SYSTEM_SHUTDOWN", "setup_env.py", {"message": "Setup script finished."})

