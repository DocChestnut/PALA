# the_hippocampus.py
#
# This agent is PALA's long-term memory archive. Its purpose is to act as a
# deliberate memory bank, providing detailed, contextual information that the
# Limbic System cannot provide. It stores persistent knowledge, conversations, and
# experiences with a crucial layer of emotional metadata.

import os
import sys
import json
import time
import uuid
import re

# --- Configuration ---
# Use a consistent BASE_DIR to ensure all file paths are absolute.
BASE_DIR = "/home/ahmed/PALA_v3.1/"
HIPPOCAMPUS_FILE = os.path.join(BASE_DIR, "memory_bus", "hippocampus_v1.json")
SEARCH_REQUEST_FILE_LIVE = os.path.join(BASE_DIR, "message_bus", "search_request_live.json")
MEMORY_RESPONSE_FILE_PENDING = os.path.join(BASE_DIR, "message_bus", "memory_response_pending.json")
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "pala_audit.log")
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
        print("Master Clock file not found. PALA cannot run without a consistent timestamp.", file=sys.stderr)
        return None

def load_hippocampus_memories():
    """
    Loads all memories from the long-term memory archive.
    """
    try:
        if os.path.exists(HIPPOCAMPUS_FILE):
            with open(HIPPOCAMPUS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading Hippocampus memories: {e}", file=sys.stderr)
    return []

def log_event(event_type, source_agent, event_data):
    """
    A helper function to log events to the pala_audit.log.
    """
    try:
        if not os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, "a") as f:
                f.write(json.dumps({
                    "event_id": str(uuid.uuid4()),
                    "timestamp": get_master_clock_timestamp(),
                    "event_type": "SYSTEM_START",
                    "source_agent": "the_hippocampus.py",
                    "event_data": {"message": "Hippocampus logging started."}
                }) + "\n")

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

def run_the_hippocampus():
    """
    Main loop for The Hippocampus agent. It constantly monitors for new
    search requests from the Limbic System and provides a deliberate,
    contextual memory response.
    """
    print("The Hippocampus is now running...")

    while True:
        try:
            # Check for a new search request from the Limbic System
            if os.path.exists(SEARCH_REQUEST_FILE_LIVE):
                with open(SEARCH_REQUEST_FILE_LIVE, "r") as f:
                    try:
                        search_request = json.load(f)
                    except json.JSONDecodeError:
                        print("Invalid JSON in search request file. Discarding.", file=sys.stderr)
                        os.remove(SEARCH_REQUEST_FILE_LIVE) # The consumer deletes the live file
                        continue

                # Load all memories for a comprehensive search
                memories = load_hippocampus_memories()
                query_text = search_request["query"]["raw_input"].lower()
                emotional_filter = search_request.get("emotional_context_at_request")
                
                relevant_memories = []
                # --- Retrieval Logic: Filter by emotional context first ---
                for memory in memories:
                    # For this foundational version, we'll check for a high degree of "frustration"
                    # as a simple emotional filter, per the blueprint example.
                    if emotional_filter and emotional_filter.get("emotions", {}).get("frustration", 0) > 0.5:
                        if memory.get("emotional_context", {}).get("frustration", 0) > 0.5:
                            if query_text in memory["content"].lower():
                                relevant_memories.append(memory)
                    else:
                        # If no strong emotional filter, just search for content
                        if query_text in memory["content"].lower():
                            relevant_memories.append(memory)

                # Prepare the memory response
                memory_response_payload = {
                    "request_id": search_request["request_id"],
                    "timestamp": get_master_clock_timestamp(),
                    "status": "success" if relevant_memories else "no_results",
                    "retrieved_memories": relevant_memories
                }

                # Write the response to a pending file
                with open(MEMORY_RESPONSE_FILE_PENDING, "w") as f:
                    json.dump(memory_response_payload, f, indent=4)
                print(f"Search complete. MemoryResponse sent to The Cerebrum with status: {memory_response_payload['status']}.")
                log_event("MEMORY_RETRIEVED", "TheHippocampus", {
                    "request_id": search_request["request_id"],
                    "status": memory_response_payload["status"],
                    "query": query_text,
                    "results_count": len(relevant_memories)
                })

                # The request is processed; remove the file to prevent re-processing
                os.remove(SEARCH_REQUEST_FILE_LIVE)

            time.sleep(1) # Poll for new requests

        except KeyboardInterrupt:
            print("\nThe Hippocampus service stopped.")
            break
        except Exception as e:
            print(f"An error occurred in The Hippocampus loop: {e}", file=sys.stderr)
            time.sleep(5)

if __name__ == "__main__":
    # Note: This script assumes the necessary directories and files
    # are created by the setup_env.py script and populated with data.
    run_the_hippocampus()

