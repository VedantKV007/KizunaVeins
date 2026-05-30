import json
import sys
import concurrent.futures
from config import Config
from navigator import Navigator
from analyst import Planner, Analyst, Reporter

def calculate_risk_score(json_report_str: str) -> int:
    """Calculates a risk score from 0-14 based on the Boolean triggers."""
    try:
        data = json.loads(json_report_str)
        score = 0
        for key, val in data.items():
            if isinstance(val, dict) and val.get("risk_identified") is True:
                score += 1
        return score
    except:
        return 14 # Maximum penalty if parsing fails

def process_single_entity(company_name: str) -> dict:
    """The isolated agent loop for a single company."""
    print(f"\n[+] Initiating trace on: {company_name}")

    try:
        search_queries = Planner.generate_queries(company_name)
        if not search_queries:
            search_queries = [{"query": f'"{company_name}" risk lawsuit issues', "engine": "google"}]
    except Exception:
        search_queries = [{"query": f'"{company_name}" risk lawsuit', "engine": "google"}]

    all_collected_evidence = []
    for query_obj in search_queries:
        results = Navigator.search_web(query=query_obj.get("query", ""), engine=query_obj.get("engine", "google"))
        if results:
            all_collected_evidence.extend(results)

    if not all_collected_evidence:
        return {"company": company_name, "score": 99, "status": "NO DATA FOUND", "json": "{}"}

    # Run the Analyst
    json_report_str = Analyst.analyze_evidence(company_name, all_collected_evidence)

    # Run the Scoring Algorithm
    risk_score = calculate_risk_score(json_report_str)

    return {
        "company": company_name,
        "score": risk_score,
        "status": "SUCCESS",
        "json": json_report_str
    }

def run_batch_investigation(company_names: list):
    print(f"\n==================================================")
    print(f" KIZUNA BATCH PROTOCOL ENGAGED")
    print(f" TARGETS DEPLOYED: {len(company_names)} Entities")
    print(f"==================================================")

    results = []

    # 🔥 The Magic Sauce: Run agents concurrently using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_company = {executor.submit(process_single_entity, comp): comp for comp in company_names}

        for future in concurrent.futures.as_completed(future_to_company):
            comp = future_to_company[future]
            try:
                data = future.result()
                results.append(data)
                print(f"[✓] Trace complete for {comp}. Score: {data['score']}/14")
            except Exception as exc:
                print(f"[!]  Trace generated an exception for {comp}: {exc}")

    print("\n==================================================")
    print("PROCUREMENT BIDS LEADERBOARD (Ranked by Risk)")
    print("==================================================")

    # Rank the companies (Lowest Risk Score is Best)
    ranked_results = sorted(results, key=lambda x: x['score'])

    for rank, res in enumerate(ranked_results, start=1):
        score = res['score']
        if score == 99:
            tier = "UNKNOWN (GHOST ENTITY)"
        elif score <= 4:
            tier = "🟢 TIER 1 (SAFE)"
        elif score <= 8:
            tier = "🟡 TIER 2 (MONITOR)"
        else:
            tier = "🔴 TIER 3 (HIGH RISK/REJECT)"

        print(f"#{rank} | {res['company'].upper().ljust(25)} | Score: {score}/14 | {tier}")

    print("==================================================\n")

if __name__ == "__main__":
    import sys
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


    while True:
        print("\n==================================================")
        print("   KIZUNA 絆: PROCUREMENT DUE DILIGENCE AGENT   ")
        print("   (Enter a comma-separated list of bidders)      ")
        print("   (Type 'exit' or 'quit' to close the program)   ")
        print("==================================================")

        try:
            target_input = input("Enter company names to investigate: ").strip()

            if target_input.lower() in ["exit", "quit"]:
                print("\n[✓] Shutting down investigation engine gracefully. Goodbye!")
                sys.exit(0)

            if target_input:
                # Split the input by commas and clean up whitespace
                print("   (Enter a semicolon-separated list of bidders)      ")
                companies_to_scan = [c.strip() for c in target_input.split(";") if c.strip()]
                run_batch_investigation(companies_to_scan)
            else:
                print("[!] Input cannot be blank. Please try again.")

        except KeyboardInterrupt:
            print("\n\n[!] Session interrupted by user (Ctrl+C). Shutting down engine gracefully.")
            sys.exit(0)


#streamlit run app.py
