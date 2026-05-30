import streamlit as st
import json
import time
import os
import PyPDF2
from analyst import DocumentIntelligence
from analyst import Planner, Analyst, Reporter
from navigator import Navigator
import concurrent.futures
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# PAGE CONFIGURATION & THEME-AWARE CSS
st.set_page_config(
    page_title="Kizuna 絆 | Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global styles
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0b0914; }
    iframe { border-radius: 6px; background: transparent !important; }
    div[data-testid="stVerticalBlock"] > div:has(iframe) { padding: 0px; margin: 0px; }
    h1, h2, h3, h4, p, span, div { color: #f0e8dc; }
    
    .kizuna-brand-container {
        position: absolute;
        top: -50px;
        left: 0px;
        display: flex;
        align-items: center;
        gap: 10px;
        user-select: none;
        pointer-events: none;
        z-index: 999;
    }
    .brand-kanji {
        font-family: 'Noto Serif JP', serif; font-size: 1.6rem; font-weight: 200; color: #C91A22; opacity: 0.8; letter-spacing: 2px;
    }
    .brand-romaji {
        font-family: 'Helvetica Neue', sans-serif; font-size: 0.75rem; font-weight: 300; color: #f0e8dc; opacity: 0.35; letter-spacing: 5px; text-transform: uppercase;
    }
    
    .terminal-log {
        font-family: 'Courier New', monospace; font-size: 0.75rem; color: #d1c9bc;
        background-color: #13111c; border-left: 2px solid #C91A22; padding: 8px 12px;
        margin-bottom: 6px; border-radius: 0px 4px 4px 0px; line-height: 1.4;
    }
    .terminal-success { border-left: 2px solid #2e7d32; }
    .terminal-header {
        font-family: monospace; letter-spacing: 2px; color: #888;
        border-bottom: 1px solid #252136; padding-bottom: 10px; margin-bottom: 15px;
    }
    
    .risk-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 30px; margin-top: 15px; }
    .risk-card { background-color: #110f1a; border: 1px solid #252136; border-radius: 4px; padding: 12px 15px; display: flex; align-items: center; gap: 15px; transition: transform 0.2s ease, border-color 0.2s ease; }
    .risk-card:hover { transform: translateY(-2px); }
    .risk-kanji { font-family: 'Noto Serif JP', serif; font-size: 24px; font-weight: 300; }
    .risk-details { display: flex; flex-direction: column; }
    .risk-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #888; }
    .risk-status { font-size: 0.9rem; font-weight: 600; letter-spacing: 2px; }
    
    .risk-danger { border-left: 3px solid #C91A22; }
    .risk-danger .risk-kanji { color: #C91A22; }
    .risk-danger .risk-status { color: #C91A22; }
    
    .risk-safe { border-left: 3px solid #2e7d32; }
    .risk-safe .risk-kanji { color: #2e7d32; }
    .risk-safe .risk-status { color: #2e7d32; }
    
    /* Leaderboard Styles */
    .leaderboard-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid #252136; background: #13111c; margin-bottom: 4px;}
    .rank-safe { border-left: 4px solid #2e7d32; }
    .rank-monitor { border-left: 4px solid #f9a825; }
    .rank-danger { border-left: 4px solid #C91A22; }
    .lb-company { font-weight: bold; font-size: 1.1rem; }
    .lb-score { font-family: monospace; font-size: 1rem; color: #888; }
    </style>
    <div class="kizuna-brand-container">
        <span class="brand-kanji">絆</span>
        <span class="brand-romaji">Kizuna Intelligence</span>
    </div>
""", unsafe_allow_html=True)

def load_html(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

IDLE_SCREEN_HTML = load_html("idle.html")
SAKURA_LOADING_HTML = load_html("loading.html")

def log_to_terminal(container, text, success=False):
    css_class = "terminal-log terminal-success" if success else "terminal-log"
    container.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)

def render_risk_dashboard(json_payload):
    """Parses Analyst JSON and generates the Top-Bar Visual Risk Grid"""
    try:
        if isinstance(json_payload, dict):
            data = json_payload
        else:
            clean_json = json_payload.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            data = json.loads(clean_json.strip())
    except Exception as e:
        return f"<div style='color:#C91A22; padding:20px;'>[!] Dashboard Data Error: Could not parse telemetry.</div>"

    html = '<div class="risk-grid">'
    for key, val in data.items():
        if not isinstance(val, dict): continue
        is_risk = val.get("risk_identified", False)
        kanji = "危険" if is_risk else "安全"
        status_text = "RISK DETECTED" if is_risk else "CLEAR"
        color_class = "risk-danger" if is_risk else "risk-safe"
        label = key.replace("_", " ").title()
        html += f'<div class="risk-card {color_class}"><div class="risk-kanji">{kanji}</div><div class="risk-details"><span class="risk-label">{label}</span><span class="risk-status">{status_text}</span></div></div>'
    html += '</div>'
    return html

def calculate_risk_score(json_report_str: str) -> int:
    try:
        data = json.loads(json_report_str)
        score = sum(1 for val in data.values() if isinstance(val, dict) and val.get("risk_identified") is True)
        return score
    except:
        return 14

# --- ASYNC AGENT WRAPPER (NOW WITH LIVE LOGGING ENABLED) ---
def run_agent_pipeline(company_name: str, terminal_window):
    log_to_terminal(terminal_window, f"<b>[SYS]</b> 🕵️ Initiating trace on: {company_name}")
    try:
        search_queries = Planner.generate_queries(company_name)
    except Exception:
        search_queries = [{"query": f'"{company_name}" risk lawsuit issues', "engine": "google"}]

    log_to_terminal(terminal_window, f"<b>[PLANNER]</b> {company_name}: Formulated {len(search_queries)} search tracks.")

    all_collected_evidence = []
    for idx, query_obj in enumerate(search_queries, start=1):
        engine = query_obj.get("engine", "google")
        query = query_obj.get("query", "")
        log_to_terminal(terminal_window, f"<b>[NAVIGATOR]</b> {company_name} (Track {idx}): Routing via {engine.upper()}...")

        results = Navigator.search_web(query=query, engine=engine)
        if results:
            all_collected_evidence.extend(results)

    if not all_collected_evidence:
        log_to_terminal(terminal_window, f"<b>[!]</b> {company_name}: Target unreachable or blocked.")
        return {"company": company_name, "score": 99, "json": "{}", "markdown": "No data found."}

    log_to_terminal(terminal_window, f"<b>[ANALYST]</b> {company_name}: Ingesting {len(all_collected_evidence)} data streams into 14-point schema...")
    json_report = Analyst.analyze_evidence(company_name, all_collected_evidence)

    log_to_terminal(terminal_window, f"<b>[REPORTER]</b> {company_name}: Generating executive markdown briefing...")
    markdown_report = Reporter.generate_executive_report(company_name, json_report)
    score = calculate_risk_score(json_report)

    log_to_terminal(terminal_window, f"<b>[✓]</b> {company_name}: Intelligence loop complete. Score: {score}/14", success=True)
    return {"company": company_name, "score": score, "json": json_report, "markdown": markdown_report}


# Initializing Session States safely
if "execution_state" not in st.session_state:
    st.session_state.execution_state = "idle"
if "batch_results" not in st.session_state:
    st.session_state.batch_results = []
if "bidding_companies" not in st.session_state:
    st.session_state.bidding_companies = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = None

ctrl_col, stage_col, term_col = st.columns([2.5, 5, 2.5], gap="large")

with ctrl_col:
    st.markdown('<div class="terminal-header">⌘ COMMAND CENTER</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📄 DROP BID SHEET / MOU (PDF)", type=["pdf"])

    if uploaded_file is not None and st.session_state.doc_context is None:
        with st.spinner("AI/ML API Parsing Document..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                raw_text = ""
                for page in pdf_reader.pages[:3]:
                    text = page.extract_text()
                    if text:
                        raw_text += text + "\n"

                # Call the AI Extractor
                extracted_data = DocumentIntelligence.extract_entities(raw_text)

                # Check if the AI failed to find anything
                if not extracted_data.get("bidding_companies"):
                    st.error("⚠️ AI Extractor returned 0 companies. Check your backend terminal for API errors!")

                st.session_state.bidding_companies = extracted_data.get("bidding_companies", [])
                st.session_state.doc_context = extracted_data

                st.rerun()  # Hard synchronization frame lock

            except Exception as e:
                st.error(f"Failed to parse PDF: {e}")
                # Ensure doc_context gets populated so the endless loop breaks
                st.session_state.doc_context = {"industry": "Error", "bidding_companies": []}

    if st.session_state.doc_context:
        st.markdown(f"""
        <div style="background-color: #13111c; border-left: 2px solid #C91A22; padding: 10px; margin-bottom: 15px;">
            <p style="font-size: 0.75rem; color: #888; margin:0;"><b>EXTRACTED CONTEXT</b></p>
            <p style="font-size: 0.85rem; color: #d1c9bc; margin: 4px 0 0 0;">
            <b>Industry:</b> {st.session_state.doc_context.get('industry', 'N/A')}<br>
            <b>Bidders Found:</b> {len(st.session_state.bidding_companies)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    default_val = "; ".join(st.session_state.bidding_companies) if st.session_state.bidding_companies else ""
    target_companies = st.text_input("TARGET ENTITIES (Semicolon Separated)", value=default_val, placeholder="e.g. Toyota; Sony; Honda")
    is_processing = st.session_state.execution_state == "processing"
    start_button = st.button("INITIATE BATCH TRACE" if not is_processing else "PROCESSING...", type="primary", use_container_width=True, disabled=is_processing)

    if (st.session_state.bidding_companies or target_companies) and not is_processing:
        if st.button("Clear Workspace", use_container_width=True):
            st.session_state.bidding_companies = []
            st.session_state.doc_context = None
            st.session_state.batch_results = []
            st.session_state.execution_state = "idle"
            st.rerun()

with term_col:
    st.markdown('<div class="terminal-header">⟁ AGENT TERMINAL</div>', unsafe_allow_html=True)
    terminal_window = st.container(height=540)

    if st.session_state.execution_state == "idle":
        terminal_window.markdown('<div class="terminal-log" style="border-left-color: #888;">[SYS] Ready for batch tasking.</div>', unsafe_allow_html=True)

with stage_col:
    main_stage = st.empty()

if start_button and (target_companies or st.session_state.bidding_companies):
    st.session_state.execution_state = "processing"
    st.rerun()

if st.session_state.execution_state == "idle":
    with main_stage.container():
        # RESTORED HEIGHT DECLARATION TO FIX FRONTEND COLLAPSE!
        st.components.v1.html(IDLE_SCREEN_HTML, height=540)

elif st.session_state.execution_state == "processing":
    with main_stage.container():
        # RESTORED HEIGHT DECLARATION TO FIX FRONTEND COLLAPSE!
        st.components.v1.html(SAKURA_LOADING_HTML, height=540)

    terminal_window.markdown('<div class="terminal-log">[SYS] Swarm initialized. Spawning worker processes...</div>', unsafe_allow_html=True)

    entities = [c.strip() for c in target_companies.split(";") if c.strip()]
    if not entities and st.session_state.bidding_companies:
        entities = st.session_state.bidding_companies

    batch_results = []

    # --- THE TERMINAL STREAMING CONCURRENCY FIX ---
    # We grab the main UI thread's context and attach it to the background workers
    ctx = get_script_run_ctx()

    def task_wrapper(comp):
        # Allow the background worker thread to safely write directly to Streamlit UI!
        add_script_run_ctx(threading.current_thread(), ctx)
        return run_agent_pipeline(comp, terminal_window)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_company = {executor.submit(task_wrapper, comp): comp for comp in entities}
        for future in concurrent.futures.as_completed(future_to_company):
            comp = future_to_company[future]
            try:
                data = future.result()
                batch_results.append(data)
            except Exception as e:
                pass

    st.session_state.batch_results = sorted(batch_results, key=lambda x: x['score'])
    st.session_state.execution_state = "complete"
    st.rerun()

elif st.session_state.execution_state == "complete":
    with main_stage.container():
        st.markdown("##  Strategic Procurement Leaderboard")
        st.markdown("Ranked by lowest structural risk across 14 vectors.")

        # 1. Render the Leaderboard UI
        for rank, res in enumerate(st.session_state.batch_results, start=1):
            score = res['score']
            if score == 99:
                rank_class, tier = "rank-danger", "GHOST ENTITY (No Data)"
            elif score <= 4:
                rank_class, tier = "rank-safe", "TIER 1 (SAFE)"
            elif score <= 8:
                rank_class, tier = "rank-monitor", "TIER 2 (MONITOR)"
            else:
                rank_class, tier = "rank-danger", "TIER 3 (HIGH RISK)"

            st.markdown(f"""
            <div class="leaderboard-row {rank_class}">
                <span class="lb-company">#{rank}. {res['company'].upper()}</span>
                <span class="lb-score">Score: {score}/14 &nbsp;|&nbsp; <b>{tier}</b></span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Render the Expandable Dossiers (Reusing the original Risk Grid!)
        st.markdown("### 🗃️ Deep-Dive Dossiers")
        for res in st.session_state.batch_results:
            with st.expander(f"Inspect Data: {res['company'].upper()}"):
                if res['score'] != 99:
                    st.markdown(render_risk_dashboard(res['json']), unsafe_allow_html=True)
                    st.markdown(res['markdown'])

                    with st.popover("View Raw AI Telemetry (JSON)"):
                        st.json(json.loads(res['json']))
                else:
                    st.warning("No intelligence payload could be scraped for this entity.")