import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
    BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE")
    BRIGHTDATA_UNLOCKER_ZONE = os.getenv("BRIGHTDATA_UNLOCKER_ZONE")
    AIML_API_KEY = os.getenv("AIML_API_KEY")
    EDINET_API_KEY = os.getenv("EDINET_API_KEY")

    # --- GUARDRAILS ---
    MAX_SEARCH_ROUNDS = 3
    MAX_RESULTS_PER_SEARCH = 5

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("CRITICAL: GEMINI_API_KEY is missing in .env")
        if not cls.BRIGHTDATA_API_KEY:
            raise ValueError("CRITICAL: BRIGHTDATA_API_KEY is missing in .env")
        if not cls.BRIGHTDATA_ZONE:
            raise ValueError("CRITICAL: BRIGHTDATA_ZONE is missing in .env")

# Validate keys immediately when this file is imported
Config.validate()