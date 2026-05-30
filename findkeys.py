import os
import requests
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai.errors import APIError

# Ensure we dynamically pinpoint the correct path to the .env file
load_dotenv(find_dotenv())

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BRIGHTDATA_KEY = os.getenv("BRIGHTDATA_API_KEY")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE")

print("==================================================")
print("🔑 LIVE API AUTHENTICATION CHECKER")
print("==================================================\n")

# ---------------------------------------------------------------------
# 1. TEST GOOGLE GEMINI AUTHENTICATION
# ---------------------------------------------------------------------
print("[*] Testing Google Gemini API Key...")
if not GEMINI_KEY:
    print("❌ FAILED: GEMINI_API_KEY is not defined in your environment.\n")
else:
    try:
        # Initialize standard client matching your analyst.py setup
        client = genai.Client(api_key=GEMINI_KEY)

        # Make an ultra-low-token live test request
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="ping"
        )
        print("✅ SUCCESS: Gemini API Key is valid and authenticated live!")
        print(f"   Response Test snippet: '{response.text.strip()}'\n")
    except APIError as e:
        print("❌ FAILED: Gemini server rejected your token.")
        print(f"   Error Details: {e}\n")
    except Exception as e:
        print("❌ FAILED: An unexpected client-side error occurred hitting Gemini.")
        print(f"   Error Details: {e}\n")

# ---------------------------------------------------------------------
# 2. TEST BRIGHT DATA SERP AUTHENTICATION
# ---------------------------------------------------------------------
print("[*] Testing Bright Data Customer Credentials...")
if not BRIGHTDATA_KEY or not BRIGHTDATA_ZONE:
    print("❌ FAILED: Missing BRIGHTDATA_API_KEY or BRIGHTDATA_ZONE configuration.\n")
else:
    # Build a tiny request mirroring your navigator.py connection layout
    endpoint = "https://api.brightdata.com/request"
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "zone": BRIGHTDATA_ZONE,
        "url": "https://www.google.com/search?q=test",
        "format": "json"
    }

    try:
        # We set a low timeout; we just want to see if we get an authentication challenge
        print(f"   [+] Sending authenticating handshake to zone: '{BRIGHTDATA_ZONE}'...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            print("✅ SUCCESS: Bright Data API Key and Zone are valid and active!\n")
        elif response.status_code in [401, 403]:
            print(f"❌ FAILED: Bright Data rejected authentication (Status Code: {response.status_code}).")
            print("   Check for typos in your key string or ensure your zone name matches exactly.\n")
        else:
            print(f"⚠️  ALERT: Network connectivity established, but server returned code {response.status_code}.")
            print("   This usually means your credentials are fine, but your account balance is empty or the zone is paused.\n")

    except requests.exceptions.RequestException as e:
        print("❌ FAILED: Could not reach Bright Data server (Network/Timeout issue).")
        print(f"   Error Details: {e}\n")

print("==================================================")
print("🏁 Verification complete.")
print("==================================================")