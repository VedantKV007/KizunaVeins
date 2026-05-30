import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from config import Config
from openai import OpenAI
from models import CompanyRiskAssessment


# 1. INITIALIZE CLIENT FIRST (Global Scope)
client = genai.Client(api_key=Config.GEMINI_API_KEY)


class TargetQuery(BaseModel):
    query: str
    engine: str  # Will be strictly "google" or "yahoo"

class SearchQuerySchema(BaseModel):
    queries: list[TargetQuery]

class Planner:
    @staticmethod
    def generate_queries(company_name: str) -> list:
        print(f"   [Planner] Formulating up to {Config.MAX_SEARCH_ROUNDS} localized search strategies and routing engines for {company_name}...")

        prompt = f"""
        You are a Bilingual Intelligence Scout for a Japanese Enterprise evaluating global partners.
        Your task is to generate exactly {Config.MAX_SEARCH_ROUNDS} distinct search queries in NATIVE JAPANESE to investigate hidden risks for '{company_name}'.
        CRITICAL ENGINE ROUTING STRATEGY:
        For each query, you MUST select the best search engine target from these 4 options based on this logic:
        - 'google': Best for global news and broad English/Japanese market trends.
        - 'yahoo': Best for domestic Japanese whistleblowers, localized labor disputes, and grassroots scandals (Yahoo! Chiebukuro).
        - 'edinet': MANDATORY for public companies. Best for official Japanese government financial filings (Annual Securities Reports).
        - 'tdb': MANDATORY for private companies. Best for Teikoku Databank (TDB) or Tokyo Shoko Research (TSR) bankruptcy and credit alerts.
        
        TIMELINE STRATIFICATION (MANDATORY):
        Track 1 [LATEST]: Focus on breaking news/current risks. Choose the engine best suited for the angle.
        Track 2 [MID-TERM]: Focus on trends from the last 2-5 years. Choose the engine best suited for the angle.
        Track 3 [HISTORICAL]: Focus on macro-crises or past scandals. Choose the engine best suited for the angle.
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SearchQuerySchema,
                    temperature=0.3
                )
            )
            data = json.loads(response.text)
            # Return a list of dictionaries: [{'query': '...', 'engine': '...'}]
            queries = data.get("queries", [])

            if isinstance(queries, list):
                return queries[:Config.MAX_SEARCH_ROUNDS]
            return []
        except Exception as e:
            print(f"   [Planner Warning] Failed to generate dynamic queries: {e}. Executing fallback track.")
            return [
                       {"query": f'"{company_name}" 訴訟', "engine": "google"},
                       {"query": f'"{company_name}" 倒産 危機', "engine": "google"},
                       {"query": f'"{company_name}" ブラック企業 告発', "engine": "yahoo"}
                   ][:Config.MAX_SEARCH_ROUNDS]

class Analyst:
    @staticmethod
    def analyze_evidence(company_name: str, collected_evidence: list) -> str:
        print(f"\n   [Analyst] Ingesting {len(collected_evidence)} data streams. Mapping to 14-point framework...")

        raw_text_payload = "\n".join(collected_evidence)

        system_instructions = f"""
        You are an expert Corporate Risk Analyst. You are receiving raw, scraped intelligence 
        regarding the target company: {company_name}.
        
        Your task is to ingest this data and map major findings to the 14-point procurement risk framework.
        
        CRITICAL GUARDRAIL AGAINST OVER-FLAGGING:
        1. Only set 'risk_identified' to true if there is a substantive, verifiable operational, financial, or legal risk. 
        2. Do NOT flag standard corporate announcements, administrative filings, routine operational transitions, or minor legal updates as active risks. If an issue is normal business practice, set 'risk_identified' to false.
        3. Translate critical risk findings into English and summarize the evidence concisely.
        4. TIMELINE STRATIFICATION (MANDATORY): Start every sentence with:
           - [LATEST] (Within the last 12 months)
           - [MID-TERM] (1 to 5 years ago)
           - [HISTORICAL] (Older than 5 years)
        5. If no major risk is found for a category, set 'risk_identified' to false and leave evidence blank.
        """

        try:
            # Upgrade: Using the new v1 API surface
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_instructions}\n\nRAW SCRAPED DATA:\n{raw_text_payload}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CompanyRiskAssessment,
                    temperature=0.1
                )
            )
            return response.text
        except Exception as e:
            print(f"   [Analyst Critical Error]: Failed to run AI Analysis - {e}")
            print("   [Analyst Status] Compiling structural fallback schema to protect pipeline stability...")

            empty_category = {"risk_identified": False, "evidence": [f"Analysis halted due to exception: {str(e)}"], "sources": []}

            fallback_payload = {
                "company_name": company_name,
                "financial_stability": empty_category,
                "corruption_integrity": empty_category,
                "technical_capability": empty_category,
                "non_compliance": empty_category,
                "past_performance": empty_category,
                "supply_chain": empty_category,
                "cybersecurity": empty_category,
                "sustainability_esg": empty_category,
                "low_balling": empty_category,
                "over_capacity": empty_category,
                "subcontractor_leakage": empty_category,
                "conflict_of_interest": empty_category,
                "insurance_bonding": empty_category,
                "key_personnel": empty_category
            }
            return json.dumps(fallback_payload)

class Reporter:
    @staticmethod
    def generate_executive_report(company_name: str, risk_json: str) -> str:
        print("[Reporter] Generating Executive Risk Briefing...")

        if not Config.AIML_API_KEY:
            return (
                "Error: AIML_API_KEY is not configured. "
                "Please add the API key to your environment settings."
            )

        try:
            client = OpenAI(
                api_key=Config.AIML_API_KEY,
                base_url="https://api.aimlapi.com/v1",
            )

            system_prompt = f"""
You are a Chief Risk Officer preparing a board-level Executive Risk Briefing for {company_name}.

Your objective is to transform structured risk assessment data into a professional executive report suitable for:
- CEOs
- CFOs
- Investment Committees
- Procurement Teams
- Enterprise Risk Officers

REPORT STRUCTURE

# Executive Risk Briefing

## Executive Summary
Provide a concise overview of the organization's current risk profile.

## Overall Risk Assessment
Assign one overall rating:
- CRITICAL
- HIGH
- MODERATE
- LOW
- CLEAR

Include a brief justification.

## Risk Analysis

Group findings into logical business categories such as:

### Financial Health
### Operational Risk
### Market & Competitive Position
### Regulatory & Compliance Exposure
### Supply Chain Resilience
### Cybersecurity & Technology
### ESG & Sustainability
### Corporate Governance & Reputation

For each identified risk provide:

#### Finding
#### Risk Rating
(CRITICAL / HIGH / MODERATE / LOW / CLEAR)

#### Observation
State the factual finding.

#### Business Impact
Explain why executives should care.

#### Supporting Evidence
Summarize evidence from the source data.

STYLE REQUIREMENTS

- Use professional Markdown.
- Use concise executive language.
- Use tables when beneficial.
- No emojis.
- Always mention that bigger corporations carry slight less risks even though the findings were negative.
- No decorative symbols.
- No JSON output.
- No marketing language.
- No unnecessary repetition.
- Write in the style of a Big Four consulting report.
- Focus on decision-useful insights rather than technical details.
- Do not invent any facts, recommendations, or data outside of what is explicitly given to you in the user payload.
"""

            response = client.chat.completions.create(
                model="claude-haiku-4-5-20251001",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Company: {company_name}\n\n"
                            f"Risk Assessment Data:\n{risk_json}"
                        ),
                    },
                ],
                temperature=0.05,
                max_tokens=2500,
            )

            report = response.choices[0].message.content

            if not report:
                return "Error: The report generator returned an empty response."

            return report

        except Exception as e:
            print(f"[Reporter Error] {str(e)}")

            return (
                "Error: Failed to generate the executive report.\n\n"
                f"Details: {str(e)}"
            )


class DocumentIntelligence:
    @staticmethod
    def extract_entities(raw_text: str) -> dict:
        print("[DocumentIntelligence] Ingesting raw contract/bid list via AI/ML API...")

        if not Config.AIML_API_KEY:
            raise ValueError("AIML_API_KEY is missing.")

        try:
            aiml_client = OpenAI(
                api_key=Config.AIML_API_KEY,
                base_url="https://api.aimlapi.com/v1",
            )

            # [UPDATED] Prompt now explicitly asks for an array of bidding companies
            system_prompt = """
            You are an elite Procurement Intelligence Extraction Agent. 
            The user will provide raw, noisy text extracted from a Solicitation for Bid, MOU, or NDA.
            
            Your job is to identify and extract:
            1. The exact list of ALL Bidding Companies / Target Entities mentioned. 
               CRITICAL: Do not modify corporate entities. Keep full names (e.g., 'Shizuoka Heavy Industries Co., Ltd.') completely whole.
            2. The Industry, Product, or Service being discussed.
            
            Respond ONLY in valid JSON format matching this exact schema:
            {
                "bidding_companies": ["Company A", "Company B"],
                "industry": "Industry description"
            }
            """

            response = aiml_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"RAW CONTRACT TEXT:\n{raw_text[:8000]}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            print(f"[DocumentIntelligence Error] {e}")
            return {"bidding_companies": [], "industry": "Unknown"}