import requests
import json

try:
    response = requests.get('http://localhost:5001/api/blocked-times')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Number of blocks: {len(data)}")
        for block in data:
            print(f"  - {block}")
    else:
        print("❌ API returned error")
except Exception as e:
    print(f"❌ Error: {e}")
