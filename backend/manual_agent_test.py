import httpx
import json
import sys

def run_tests():
    API_URL = "http://localhost:8000"
    client = httpx.Client(timeout=60.0)
    resp = client.post(f"{API_URL}/api/v1/auth/login", data={"username": "admin@example.com", "password": "admin123"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        sys.exit(1)

    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    def test_prompt(prompt):
        print(f"\n--- Testing: {prompt} ---")
        resp = client.post(f"{API_URL}/api/v1/agent/invoke", json={"prompt": prompt}, headers=headers)
        print(json.dumps(resp.json(), indent=2))

    test_prompt("Get me the information of Naren G")
    test_prompt("Update Naren G's phone number to 9876543210")
    test_prompt("Delete Naren G")

if __name__ == "__main__":
    run_tests()
