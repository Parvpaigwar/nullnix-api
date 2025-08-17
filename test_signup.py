import urllib.request
import urllib.parse
import json

# Test signup endpoint without external dependencies
url = "http://127.0.0.1:8000/api/users/signup/"
data = {
    "name": "Test User",
    "email": "test@example.com"
}

# Convert dict to JSON string
json_data = json.dumps(data).encode('utf-8')

# Create request
req = urllib.request.Request(url, data=json_data)
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        response_text = response.read().decode('utf-8')
        print(f"Status Code: {status_code}")
        print(f"Response: {response_text}")
except urllib.error.HTTPError as e:
    status_code = e.code
    response_text = e.read().decode('utf-8')
    print(f"Status Code: {status_code}")
    print(f"Response: {response_text}")
except Exception as e:
    print(f"Error: {e}")
