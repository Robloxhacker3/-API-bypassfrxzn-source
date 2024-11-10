import re
import tls_client
import random
import time
import logging
import json

# Setup logging with a timestamp format
logging.basicConfig(filename="bypass_debug.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base link
linkvertise = "https://linkvertise.com/"

# TLS session setup with random Firefox version
session = tls_client.Session(client_identifier="Firefox110", random_tls_extension_order=True)
browser_version = random.randint(110, 115)

# Custom headers to help mimic a browser request
headers = {
    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{browser_version}.0) Gecko/20100101 Firefox/{browser_version}.0",
    "Referer": linkvertise
}

# Prompt the user for a Fluxus link
link = input("Enter Key Link: ")

# Extract HWID from the link
if not link.startswith("https://flux.li/windows/start.php?HWID="):
    print("Invalid link! Please provide a valid Fluxus link.")
    exit()

# Isolate HWID for further use
hwid = link.split("HWID=")[1]
print(f"Extracted HWID: {hwid}")

# Key regex to match response content
key_regex = r'let content = \("([^"]+)"\);'

# List of endpoints to sequentially access, with referers
endpoints = [
    {"url": f"https://flux.li/windows/start.php?HWID={hwid}", "referer": ""},
    {"url": f"https://flux.li/windows/start.php?[OFFSET_REPLACE]=false&HWID={hwid}", "referer": f"https://flux.li/windows/start.php?HWID={hwid}"},
    {"url": "https://fluxteam.net/windows/checkpoint/check1.php", "referer": linkvertise},
    {"url": "https://fluxteam.net/windows/checkpoint/check2.php", "referer": linkvertise},
    {"url": "https://fluxteam.net/windows/checkpoint/main.php", "referer": linkvertise}
]

OFFSET = ""  # Offset placeholder for dynamic URL construction
safe_mode = input("Enable safe mode? (yes/no): ").strip().lower() == "yes"

# Adaptive safe mode to delay requests
if safe_mode:
    print("Safe mode enabled. Requests will be delayed.")

# Function to retry requests in case of temporary failures
def make_request(url, headers, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                return response
            else:
                logging.warning(f"Request to {url} failed with status: {response.status_code}")
        except Exception as e:
            logging.error(f"Request to {url} encountered an error: {e}")
        time.sleep(2)  # Wait before retrying
    print(f"Failed to get a successful response from {url} after {retries} attempts.")
    return None

# Initialize JSON dictionary
json_output = {
    "status": "failed",
    "message": "",
    "key": None
}

# Main process of handling each endpoint
for i, endpoint in enumerate(endpoints):
    url = endpoint["url"].replace("[OFFSET_REPLACE]", OFFSET)
    headers["Referer"] = endpoint["referer"]
    
    # Execute request with retry support
    response = make_request(url, headers)
    
    if response is None:
        json_output["message"] = f"Endpoint {i} failed. Check bypass_debug.log for more info."
        continue

    # Log the response details
    logging.info(f"[{i}] Response {response.status_code} from {url}")

    # Process the first response to extract OFFSET
    if i == 0:
        match = re.search(r'start.php\?(.*?)=false&HWID=', response.text)
        if match:
            OFFSET = match.group(1)
            logging.info(f"Extracted OFFSET: {OFFSET}")
        else:
            json_output["message"] = "Fluxus has likely patched the bypass or changed its structure."
            with open("bypass.html", "w") as f:
                f.write(response.text)
            break

    # Process the final response to extract the key
    if i == len(endpoints) - 1:
        match = re.search(key_regex, response.text)
        if match:
            json_output["status"] = "success"
            json_output["key"] = match.group(1)
            json_output["message"] = "Bypass successful."
            logging.info(f"Success! Key obtained: {match.group(1)}")
        else:
            json_output["message"] = "Failed to extract key from response."
            with open("bypass.html", "w") as f:
                f.write(response.text)

    # Delay requests in safe mode
    if safe_mode:
        delay = random.uniform(4, 7)
        logging.info(f"Safe mode delay: {delay:.2f} seconds")
        time.sleep(delay)

# Write the JSON output to status.json
with open("status.json", "w") as json_file:
    json.dump(json_output, json_file, indent=4)

print("Bypass script completed. Check status.json for the status.")
input("Press Enter to exit...")
