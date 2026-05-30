import os

import requests
import io
import zipfile

# Your live EDINET API Key
API_KEY = os.getenv("EDINET_API_KEY")

# A valid Document ID from your previous logs (Toyota's filing)
DOC_ID = "S100LO6W"

def test_edinet_api(doc_id, api_key):
    print(f"==================================================")
    print(f"[*] Testing EDINET API v2 for Document ID: {doc_id}")
    print(f"==================================================")

    endpoint = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
    params = {
        "type": 1, # Type 1 = the full document package
        "Subscription-Key": api_key
    }

    try:
        print(f"[*] Sending authenticated request to FSA servers...")
        response = requests.get(endpoint, params=params, timeout=30)

        print(f"[*] Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"\n[!] FAILED: API returned error code {response.status_code}")
            print(f"    Response: {response.text}")
            return

        print("[✓] SUCCESS: Binary payload received!")
        print("[*] Attempting to unzip stream in-memory...")

        # Load the binary response directly into RAM
        zip_buffer = io.BytesIO(response.content)

        # Attempt to unzip it
        with zipfile.ZipFile(zip_buffer) as archive:
            file_list = archive.namelist()
            print(f"[✓] SUCCESS: Archive opened. Found {len(file_list)} files inside.")

            # Filter for HTML disclosure documents
            html_files = [f for f in file_list if f.endswith(('.htm', '.html'))]
            print(f"[*] Found {len(html_files)} HTML files inside the zip.")

            if html_files:
                target_file = html_files[0]
                print(f"\n[*] Extracting preview from: {target_file}")

                # Open the specific HTML file from inside the zip
                with archive.open(target_file) as doc:
                    content = doc.read().decode('utf-8', errors='ignore')

                    print("\n================ PREVIEW ==================")
                    print(content[:600]) # Print first 600 characters
                    print("===========================================\n")
                    print("[✓] ALL SYSTEMS GO! The in-memory unzipper works perfectly.")
            else:
                print("[!] No HTML files found in the archive.")

    except zipfile.BadZipFile:
        print("\n[!] CRITICAL: The API did not return a valid ZIP file.")
        print("    Check if your Subscription-Key is active or if the DocID is correct.")
    except Exception as e:
        print(f"\n[!] CRITICAL: {e}")

if __name__ == "__main__":
    test_edinet_api(DOC_ID, API_KEY)