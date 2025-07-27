import requests
import json
import os

# Configuration for the API request
# IMPORTANT: Replace these placeholders with your actual values
API_BASE_URL = os.environ.get("BOT_API_URL", "http://localhost:5000") # Or your deployed URL
API_ENDPOINT = f"{API_BASE_URL}/api/send_message"
API_KEY = os.environ.get("API_KEY", "YOUR_SECURE_API_KEY_HERE") # Replace with the API_KEY set in your bot's environment
TARGET_USER_ID = os.environ.get("TARGET_TELEGRAM_USER_ID", "") # Replace with the Telegram User ID you want to message

# Message details
test_message_content = "Hello from the Flask API! This is a test message."

# Prepare the headers
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Prepare the JSON payload
payload = {
    "user_id": TARGET_USER_ID,
    "message_type": "text",
    "content": test_message_content
}

print(f"Attempting to send message to user ID: {TARGET_USER_ID}")
print(f"API Endpoint: {API_ENDPOINT}")

try:
    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.json().get('error', 'Unknown error')}")

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: Could not connect to the API server at {API_BASE_URL}.")
    print("Please ensure your bot (and its Flask API) is running and accessible at the specified URL.")
    print(f"Details: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
