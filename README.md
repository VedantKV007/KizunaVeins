![kizuna's github banner](https://raw.githubusercontent.com/VedantKV007/VedantKV007/master/banner.svg)


# Kizuna 絆: Cross-Border Strategic Intelligence Suite
Every Western tech giant relies on Asian supply chains—Taiwan for chips, Korea for displays, and Japan for precision robotics. But when American enterprises review overseas bids, they are flying blind.

Contractors present pristine, English marketing facades. Meanwhile, the critical vulnerabilities—domestic lawsuits, localized bankruptcies, and labor disputes—remain completely invisible to Western search engines, buried deep in native-language silos. Betting a multi-million dollar partnership on a Google search isn’t a strategy. It's a massive liability.

Enter Kizuna.

Kizuna is an autonomous, multi-agent intelligence suite that acts as a digital forensic investigator. It bypasses regional constraints to weaponize native-language data, transforming hidden risks into boardroom-ready intelligence.

We don't just bridge the language barrier. We eliminate the blind spot before you sign the contract. try now : https://kizunaveins-garden.streamlit.app
---

## 🚀 Hackathon Sponsor Integrations & Core Pillars

Kizuna was engineered from the ground up to aggressively leverage our hackathon sponsor ecosystems to solve real-world cross-border procurement challenges:

### 💡 Powered by AI/ML API (Special Partner Integration)
The intelligence pipeline relies deeply on **AI/ML API**'s blazing fast, high-availability model routing infrastructure to power our core text intelligence and contract extraction layers:
* **Advanced Document Extraction:** Utilizes `gpt-4o-mini` via **AI/ML API** to handle chaotic, unstructured structural text normalization from complex PDFs.
* **Executive Report Synthesis:** Leverages Next-Gen `claude-haiku-4.5` via **AI/ML API** to translate structural multi-agent telemetry inputs into elite, board-ready corporate consulting dossiers.

### 🌐 Powered by Bright Data Data Retrieval
Bypasses aggressive geo-blocks and native regional constraints utilizing **Bright Data's Web Unlocker and SERP API infrastructure** to orchestrate seamless Japanese network data harvesting across local index sandboxes (EDINET, Teikoku Databank, and Yahoo Japan forums).

---

## 🎯 Solicitations & Bid Processing Assistance

When a Western corporation releases a **Solicitation for Bid (RFP/RFQ)**, they are often flooded with proposals from overseas contractors they know very little about. Kizuna acts as an automated **Solicitation Intake Assistant**:

1. **The Ingestion Phase:** Procurement officers drop raw PDFs of incoming Solicitations, signed NDAs, or incoming Bidding Sheets directly into the interface.
2. **Entity Isolation:** The **AI/ML API Document Intelligence Agent** automatically scans the noisy contract texts up to 8,000 characters, isolates every single participating candidate entity, extracts full unbroken corporate names (e.g., *'Shizuoka Heavy Industries Co., Ltd.'*), and maps out the target industry automatically.
3. **Automated Batch Verification:** These extracted bidders are automatically passed into our parallel agent execution loops for exhaustive background risk checks, generating an instant, interactive Procurement Bids Risk Leaderboard.

---

## 🌟 Key Features

- **Document Context Intelligence (AI-Driven Intake):** Seamlessly parse noisy PDF Solicitation for Bids, MOUs, or NDAs using a structured LLM pipeline (`gpt-4o-mini`) via **AI/ML API** to dynamically map out participating entities and industries without human intervention.
- **Autonomous Multi-Agent Swarm Integration:** Utilizes an integrated architecture featuring specialized, concurrent agent frameworks:
  - 🗺️ **The Planner:** Formulates hyper-targeted, Native-Japanese search strategies categorized by timeline tracks (Latest, Mid-Term, Historical).
  - 🕵️ **The Navigator:** Operates an advanced 3-phase Bright Data routing waterfall to retrieve raw DOM blocks, automatically re-routing blocked assets.
  - 🧠 **The Analyst:** Translates native Japanese streams into English and structurally categorizes observations into a strict 14-point macro-risk matrix.
  - 📊 **The Reporter:** Transforms structural telemetry data into a highly stylized, executive-level consulting dossier using an advanced LLM suite (`claude-haiku-4.5`) powered by **AI/ML API**.
- **Concurrent Stream Threading:** Features an optimized Streamlit deployment utilizing Python's `ThreadPoolExecutor` alongside secure UI thread runtime mapping (`add_script_run_ctx`) to display multi-agent pipeline logs concurrently in a real-time web terminal.
- **Strategic Japan-Market Deep Dive (MVP Focus):** Built natively to extract hidden data from highly restrictive local indices, including Yahoo Japan grassroots forums (Chiebukuro), Teikoku Databank (TDB), Tokyo Shoko Research (TSR), and Japan's Financial Services Agency disclosure platform (EDINET).

---

## 🛠️ The Tech Stack & Architecture

### 1. Data Retrieval Infrastructure (The Bright Data Edge)
Kizuna implements an advanced **Phase 3 Intelligent Re-Routing Waterfall** to maintain total pipeline resilience against anti-bot tracking:
* **Route A (Web Unlocker - Fast):** Attempts standard Web Unlocker execution to capture light raw HTML blobs.
* **Route B (Dynamic JS Failover):** Automatically falls back to Javascript rendering and browser emulation parameters if Route A is throttled or yields minimal byte payloads.
* **Route C (SERP Baseline Context):** Gracefully drops down to SERP baseline search snippet context to guarantee data continuity if localized end-points remain strictly hard-blocked.

### 2. In-Memory Processing & Transformation
- **Serverless-Ready Stream Handling:** Bypasses disk footprint dependencies by handling binary automated data collections directly in RAM using `io.BytesIO` streams and real-time internal extraction.
- **CPU Lockup Guardrails:** Implements algorithmic boundary snapping on oversized scraped DOM payloads (capping text extractions safely to mitigate window boundaries) to completely prevent server-side CPU hangs.

### 3. Application Workflow
* **Frontend UI:** Streamlit Web Application
* **LLM Engine Infrastructure:** Google Gemini Pro (`gemini-2.5-flash`) via the modern `google-genai` SDK, paired with specialized text engines via **AI/ML API** interfaces.

---

## 📂 Repository Structure

```text
├── app.py                # Main Streamlit web application & concurrent thread coordinator
├── analyst.py            # AI core: Contains Planner, Analyst, Reporter, & DocIntelligence agents
├── navigator.py          # Data harvesting engine: Bright Data routing waterfall & HTML processors
├── models.py             # Pydantic typing layout validating the 14-point Risk matrix schema
├── config.py             # Centralized environmental variable validator (Includes AI/ML API key validation)
├── idle.html             # Themed interactive background module for application workspace idle states
├── loading.html          # Custom, high-fidelity Japanese Torii animated loading screen asset
└── requirements.txt      # Automated server environment dependency manifest
