import requests
import json

# Test the API
url = "http://127.0.0.1:5000/predict"
payload = {
    "symptoms": "itching, skin rash, nodal skin eruption"
}

response = requests.post(url, json=payload)
print("Status Code:", response.status_code)
print("\nResponse JSON:")
print(json.dumps(response.json(), indent=2))
