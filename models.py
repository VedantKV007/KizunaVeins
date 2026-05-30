from pydantic import BaseModel, Field
from typing import List

class RiskCategory(BaseModel):
    """The structure for how Gemini will report on a single risk dimension."""

    risk_identified: bool = Field(
        description="True if any risk was found, False otherwise"
    )

    # DO NOT use default or default_factory.
    # Just declare the type and description. Gemini handles the rest!
    evidence: List[str] = Field(
        description="List of specific facts, quotes, or summaries found"
    )

    sources: List[str] = Field(
        description="URLs or document names where the evidence was found"
    )


class CompanyRiskAssessment(BaseModel):

    company_name: str
    financial_stability: RiskCategory = Field(description="A. Financial Stability Risk")
    corruption_integrity: RiskCategory = Field(description="B. Corruption & Integrity Risk")
    technical_capability: RiskCategory = Field(description="C. Technical Capability Risk")
    non_compliance: RiskCategory = Field(description="D. Non-Compliance Risk")
    past_performance: RiskCategory = Field(description="E. Past Performance Risk")
    supply_chain: RiskCategory = Field(description="F. Supply Chain & Subcontractor Risk")
    cybersecurity: RiskCategory = Field(description="G. Cybersecurity & Data Privacy Risk")
    sustainability_esg: RiskCategory = Field(description="H. Sustainability & ESG Risk")
    low_balling: RiskCategory = Field(description="I. Low-Balling Risk")
    over_capacity: RiskCategory = Field(description="J. Over-Capacity Risk")
    subcontractor_leakage: RiskCategory = Field(description="K. Subcontractor Leakage Risk")
    conflict_of_interest: RiskCategory = Field(description="L. Conflict of Interest Risk")
    insurance_bonding: RiskCategory = Field(description="M. Insurance & Bonding Risk")
    key_personnel: RiskCategory = Field(description="N. Key Personnel Risk")