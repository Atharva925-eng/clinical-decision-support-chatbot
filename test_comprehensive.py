import requests
import json

print("=" * 60)
print("TEST 1: Single symptom 'itching'")
print("=" * 60)
url = 'http://127.0.0.1:5000/predict'
payload = {'symptoms': 'itching'}
response = requests.post(url, json=payload)
data = response.json()
diseases_str = ', '.join([f"{d['name']} ({d['confidence']})" for d in data['diseases']])
print(f"✅ Success: {data['success']}")
print(f"📊 Diseases: {diseases_str}")
print(f"💊 Medications: {len(data['medications'])} items")
print(f"⚠️  Precautions: {len(data['precautions'])} items")
print(f"🥗 Diet: {len(data['diet']['recommended'])} recommended foods\n")

print("=" * 60)
print("TEST 2: Multiple symptoms")
print("=" * 60)
payload = {'symptoms': 'fever, cough, body ache, chills'}
response = requests.post(url, json=payload)
data = response.json()
diseases_str = ', '.join([f"{d['name']} ({d['confidence']})" for d in data['diseases']])
print(f"✅ Success: {data['success']}")
print(f"📊 Diseases: {diseases_str}")
print(f"💊 Medications: {len(data['medications'])} items")
print(f"⚠️  Precautions: {len(data['precautions'])} items")
print(f"🥗 Diet: {len(data['diet']['recommended'])} recommended foods\n")

print("=" * 60)
print("TEST 3: Different symptoms")
print("=" * 60)
payload = {'symptoms': 'vomiting, diarrhea, abdominal pain'}
response = requests.post(url, json=payload)
data = response.json()
diseases_str = ', '.join([f"{d['name']} ({d['confidence']})" for d in data['diseases']])
print(f"✅ Success: {data['success']}")
print(f"📊 Diseases: {diseases_str}")
print(f"💊 Medications: {len(data['medications'])} items")
print(f"⚠️  Precautions: {len(data['precautions'])} items")
print(f"🥗 Diet: {len(data['diet']['recommended'])} recommended foods")
