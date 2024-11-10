import json
import time
import os

# File path for the status.json
status_file = "status.json"

def update_status():
    # Prepare data to be written to status.json
    status_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "Running",
        "details": [{"message": "Process is running", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}],
    }

    # Write status data to status.json
    try:
        with open(status_file, "w") as json_file:
            json.dump(status_data, json_file, indent=4)  # Pretty-print JSON data
        print(f"Status updated to {status_file} at {status_data['timestamp']}")
    except Exception as e:
        print(f"Error writing to {status_file}: {e}")

if __name__ == "__main__":
    update_status()
