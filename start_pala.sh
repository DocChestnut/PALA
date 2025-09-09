#!/bin/bash

# A script to start the PALA system.
# It ensures the Conda environment is active and then runs the main orchestration script.

echo "--- Activating the PALA Conda environment ---"
source ~/miniconda3/bin/activate pala-env

if [ $? -ne 0 ]; then
  echo "Error: Failed to activate Conda environment 'pala-env'."
  echo "Please ensure Conda is installed and the environment exists."
  exit 1
fi

echo "--- Running the setup script for environment integrity ---"
python setup_env.py

echo "--- Launching the main PALA system (backend agents) ---"
python main.py &

# Wait for a moment to allow the backend agents to boot up
sleep 5

echo "--- Launching the PALA UI (The Conscious Mind) ---"
streamlit run the_conscious_mind.py

# Deactivate the environment when the main script finishes (e.g., on Ctrl+C)
conda deactivate

echo "--- PALA system shutdown complete. ---"

