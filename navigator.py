import requests
import urllib.parse
import json
import time
import random
import re
from config import Config
import requests
import sys
import codecs
import re
from config import Config
import io
import zipfile

#sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class Navigator:
    session = requests.Session()
    @staticmethod
    def _fetch_edinet_api_v2(doc_id: str) -> str:
        """Retrieves a corporate filing directly from the Government API v2 and unzips it in-memory."""
        print(f"      [EDINET API v2] Direct targeting engaged for DocID: {doc_id}")

        endpoint = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        params = {"type": 1, "Subscription-Key": Config.EDINET_API_KEY}

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            if response.status_code != 200:
                return f"[EDINET API Error] Government server returned status code: {response.status_code}"

            zip_buffer = io.BytesIO(response.content)
            extracted_text_blocks = []

            with zipfile.ZipFile(zip_buffer) as archive:
                for file_path in archive.namelist():
                    if file_path.endswith(".htm") or file_path.endswith(".html"):
                        with archive.open(file_path) as document_file:
                            raw_html = document_file.read().decode('utf-8', errors='ignore')
                            clean_block = Navigator._clean_html(raw_html)
                            if clean_block and "[No Extractable Body Text]" not in clean_block:
                                extracted_text_blocks.append(clean_block)

            if extracted_text_blocks:
                print("      [✓ EDINET API v2 Success] Document unzipped and parsed cleanly in memory.")
                return "\n\n".join(extracted_text_blocks[:2]) # Cap data footprint safely

            return "[EDINET API Error] No readable HTML components found inside document container archive."

        except Exception as err:
            print(f"      [!] EDINET API Critical Exception: {err}")
            return f"[EDINET API Exception Failover]: Processing halted due to: {err}"
    @staticmethod
    def _scrape_full_text(url: str, fallback_snippet: str) -> str:
        """
        Helper Method: Deep Extractor with Phase 3 Intelligent Re-routing Waterfall.
        Routes targets through Web Unlocker, falls back to JS rendering, and drops to
        SERP snippet context if the asset is completely blocked.
        """

        # --- EDINET API INTERCEPTOR ---
        if "disclosure.edinet-fsa.go.jp" in url:
            # Rip the 8-character document ID (e.g., S100X123) out of the URL
            match = re.search(r'\b(S[0-9][0-9A-Z]{6})\b', url, re.IGNORECASE)
            if match:
                return Navigator._fetch_edinet_api_v2(match.group(1).upper())
        endpoint = "https://api.brightdata.com/request"

        headers = {
            "Authorization": f"Bearer {Config.BRIGHTDATA_API_KEY}",
            "Content-Type": "application/json"
        }

        # ROUTE A: Standard Web Unlocker Pipeline (Fast Raw HTML)

        print(f"      [Route A] Trying Web Unlocker for: {url}")
        payload_route_a = {
            "zone": Config.BRIGHTDATA_UNLOCKER_ZONE,
            "url": url,
            "format": "raw"
        }

        try:
            response = Navigator.session.post(endpoint, headers=headers, json=payload_route_a, timeout=25)
            print(f"      [DEBUG Route A] Status: {response.status_code} | Length: {len(response.text)}\n      [DEBUG Preview]: {response.text[:200]}")
            # new stabilty fix up

            # If successful and contains substantial content, process immediately
            if response.status_code == 200 and len(response.text) > 500:
                html_data = response.text
                extracted = Navigator._clean_html(html_data)
                if extracted and "[No Extractable Body Text]" not in extracted:
                    print("      [✓ Route A Success] Content captured cleanly.")
                    return extracted

            print(f"      [!] Route A Failed or Throttled (Status: {response.status_code}). Triggering Re-route...")

        except requests.exceptions.RequestException as e:
            print(f"      [!] Route A Exception: {e}. Activating failover tracking...")

       # ROUTE B: Intelligent Failover (Dynamic JS Rendering & Browser Emulation+New Unlocker Update)

        print(f"      [Route B Fallback] Re-routing request to Javascript Rendering Suite...")
        payload_route_b = {
            "zone": Config.BRIGHTDATA_UNLOCKER_ZONE,
            "url": url,
            "format": "raw",
            "render": True  # Instructs Bright Data to handle client-side rendering/SPA framework elements
        }

        try:
            response = Navigator.session.post(endpoint, headers=headers, json=payload_route_b, timeout=35)

            # CRITICAL FIX: Added 'and len(response.text) > 500' to reject tiny API error payloads
            if response.status_code == 200 and len(response.text) > 500:
                html_data = response.text
                extracted = Navigator._clean_html(html_data)
                if extracted and "[No Extractable Body Text]" not in extracted:
                    print("      [✓ Route B Success] Dynamic JS rendered content captured.")
                    return extracted

            print(f"      [!] Route B Blocked or Dead End (Status: {response.status_code}). Dropping to context guardrail...")
        except requests.exceptions.RequestException as e:
            print(f"      [!] Route B Exception: {e}. Moving to secondary survival vector...")


        # ---------------------------------------------------------------------
        # ROUTE C: Context Guardrail (Fallback to SERP Snippet Context)
        # ---------------------------------------------------------------------
        print("      [Route C Last Resort] Source inaccessible. Saving pipeline via SERP baseline context.")
        return f"[Live Data Blocked/Unavailable - Fallback to Search Snippet Analysis]: {fallback_snippet}"

    @staticmethod
    def _clean_html(html_content: str) -> str:
        """
        Parses and scrubs raw HTML blobs into clean string blocks without relying on specific tags.
        """
        import re
        # Stability Fix: Prevent CPU lockup on massive DOM payloads
        if len(html_content) > 250000:
            # Snap backward to the nearest closed tag arrow to prevent broken tag strings
            safe_boundary = html_content.rfind('>', 0, 250000)
            if safe_boundary != -1:
                html_content = html_content[:safe_boundary + 1]
            else:
                html_content = html_content[:250000]

        # Strip out scripts, styles, SVGs, and navigational clutter entirely
        html_content = re.sub(r'<(script|style|noscript|header|footer|nav|svg)[^>]*>.*?</\1>', ' ', html_content, flags=re.I | re.S)

        # Remove all remaining HTML tags to extract the raw DOM text (including heavy <div> usage)
        clean_text = re.sub(r'<[^>]+>', ' ', html_content)

        # Collapse multiple spaces and newlines into single spaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        # Guardrail context chunk length to safe threshold
        max_char_limit = 4000
        if len(clean_text) > max_char_limit:
            clean_text = clean_text[:max_char_limit] + "\n... [Content Truncated for Analysis Context Bounds] ..."

        return clean_text if len(clean_text) > 50 else "[No Extractable Body Text Discovered on Page]"


    @staticmethod
    def search_web(query: str, engine: str = "google") -> list:
        """
        Agent 2: The Web Worker (Stabilized Localized Router).
        Routes queries cleanly through Google's working JSON pipeline, applying
        strict domestic constraints when 'Yahoo' is requested to surface grassroots tea.
        """
        endpoint = "https://api.brightdata.com/request"


        # --- ENTERPRISE ROUTER FIX ---
        if engine.lower() == "yahoo":
            print(f"   [Navigator]  Applying Yahoo-Style Domestic Filters via JSON network...")
            scandal_query = f"{query} (site:.jp OR site:co.jp OR site:chiebukuro.yahoo.co.jp)"
            encoded_query = urllib.parse.quote(scandal_query)
            target_url = f"https://www.google.com/search?q={encoded_query}&hl=ja&gl=jp"

        elif engine.lower() == "edinet":
            print(f"   [Navigator]  Routing to Official EDINET Government Database...")
            # Target the viewable document index pages which host the explicit Document ID tokens
            scandal_query = f"{query} site:disclosure.edinet-fsa.go.jp"
            encoded_query = urllib.parse.quote(scandal_query)
            target_url = f"https://www.google.com/search?q={encoded_query}&hl=ja&gl=jp"

        elif engine.lower() == "tdb":
            print(f"   [Navigator]  Routing to Teikoku Databank/TSR (Credit DB)...")
            # Target Japan's top two credit agencies for bankruptcy/credit news
            scandal_query = f"{query} (倒産 OR 信用 OR 評点 OR ニュース) (site:tdb.co.jp OR site:tsr-net.co.jp)"
            encoded_query = urllib.parse.quote(scandal_query)
            target_url = f"https://www.google.com/search?q={encoded_query}&hl=ja&gl=jp"

        else:
            print(f"   [Navigator]  Routing search through Google global network...")
            encoded_query = urllib.parse.quote(query)
            target_url = f"https://www.google.com/search?q={encoded_query}"

        headers = {
            "Authorization": f"Bearer {Config.BRIGHTDATA_API_KEY}",
            "Content-Type": "application/json"
        }

        # Keep format as "json" globally so it NEVER crashes or drops tracks
        payload = {
            "zone": Config.BRIGHTDATA_ZONE,
            "url": target_url,
            "format": "json"
        }

        max_retries = 3
        base_delay = 2.0

        for attempt in range(1, max_retries + 1):
            print(f"   [Navigator] Track Request (Attempt {attempt}/{max_retries}) for query: {query}")
            try:
                response = Navigator.session.post(endpoint, headers=headers, json=payload, timeout=45)
                response.raise_for_status()

                outer_data = response.json()
                serp_data = {}
                #stabity update

                if isinstance(outer_data, dict):
                    if "body" in outer_data:
                        body_content = outer_data["body"]
                        if isinstance(body_content, str):
                            try:
                                serp_data = json.loads(body_content)
                            except Exception:
                                pass
                        elif isinstance(body_content, dict):
                            serp_data = body_content
                    else:
                        serp_data = outer_data
                else:
                    # If Bright Data returned an unexpected string or array,
                    # we treat it as an empty result so the retry loop can try again.
                    print("   [Navigator Warning] Received malformed non-dictionary JSON response from API.")
                    serp_data = {}

                organic_results = []
                if isinstance(serp_data, dict):
                    if "organic" in serp_data:
                        organic_results = serp_data["organic"]
                    elif "organic_results" in serp_data:
                        organic_results = serp_data["organic_results"]
                elif isinstance(serp_data, list):
                    organic_results = serp_data

                if not isinstance(organic_results, list):
                    organic_results = []

                truncated_results = organic_results[:Config.MAX_RESULTS_PER_SEARCH]
                deep_extracted_evidence = []

                for item in truncated_results:
                    if not isinstance(item, dict):
                        continue

                    # Protect individual link extraction tracks from spoiling the whole search session
                    try:
                        title = item.get("title", "No Title Available")
                        snippet = item.get("description", item.get("snippet", "No Context Snippet Found"))

                        link = item.get("link") or item.get("url") or "No Valid Link Source"
                        link = str(link)

                        # --- AUTHORITATIVE EDINET BINARY & SESSION TRANSFORMATION ---
                        if "disclosure.edinet-fsa.go.jp" in link:
                            # 1. Reroute from binary downloads to the HTML viewer
                            if "download" in link:
                                link = link.replace("/download", "/control/W1E63011Action-htm")

                            # 2. Strip dead session keys so EDINET doesn't infinite-redirect
                            if "SESSIONKEY" in link:
                                link = re.sub(r'&SESSIONKEY=[^&]+', '', link)

                            print(f"   [Navigator Bypass] Cleaned EDINET URL for live access: {link}")


                        if link.startswith("http"):
                            full_page_body = Navigator._scrape_full_text(link, fallback_snippet=snippet)
                        else:
                            full_page_body = f"[No source link available to execute analysis]: {snippet}"

                        compiled_data = (
                            f"Source Document Title: {title}\n"
                            f"Target Source URL: {link}\n"
                            f"DEEP DATA EXTRACT:\n{full_page_body}\n"
                            f"----------------------------------------\n"
                        )
                        deep_extracted_evidence.append(compiled_data)

                    except Exception as item_err:
                        print(f"   [Navigator Warning] Skipping item due to an unexpected parsing error: {item_err}")
                        # Provide a minimal baseline so the pipeline doesn't drop the context entirely
                        fallback_snippet = item.get("description", item.get("snippet", "No Context Snippet Found"))
                        deep_extracted_evidence.append(
                            f"Source Document Title: {item.get('title', 'Unknown')}\n"
                            f"Target Source URL: {item.get('link', 'Unknown')}\n"
                            f"DEEP DATA EXTRACT:\n[Item Processing Failed]: {fallback_snippet}\n"
                            f"----------------------------------------\n"
                        )


                return deep_extracted_evidence

            except (requests.exceptions.RequestException, ValueError) as err:
                print(f"   [Navigator Warning] Attempt {attempt} failed due to: {err}")
                if attempt == max_retries:
                    print("   [Navigator Error] Maximum retries exhausted. Returning empty collection.")
                    return []

                delay = (base_delay ** attempt) + random.uniform(0.5, 1.5)
                print(f"   [Navigator Status] Sleeping for {delay:.2f} seconds before reconnecting...")
                time.sleep(delay)

        return []