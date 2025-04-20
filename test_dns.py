import httpx

try:
    print("🌐 Testing DNS resolution via httpx...")
    response = httpx.get("https://api.telegram.org")
    print(f"✅ Success! Status: {response.status_code}")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
