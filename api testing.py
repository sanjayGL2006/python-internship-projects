import requests

# Replace this with your actual project's API endpoint URL
api_url = "http://127.0.0.1:5000/app"
api_key = ""

# Approach 1: Sending the key as a Bearer Token (most common)
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Approach 2: Sending the key as a custom header (uncomment if your API uses this instead)
# headers = {
#     "x-api-key": api_key
# }

try:
    # Change requests.get to requests.post if your endpoint requires a POST request
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        print("Success! The API key was accepted.")
        print("Response data:", response.json())
    elif response.status_code in [401, 403]:
        print(f"Authentication failed (Status {response.status_code}). The API key was rejected.")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")