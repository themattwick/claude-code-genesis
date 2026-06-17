"""Configuration for Automat do Pisania - Multi-Agent Spec Writer"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============ LLM Configuration (Model Agnostic) ============

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# Model assignments for different tasks
MODELS = {
    "gatherer": os.getenv("GATHERER_MODEL", "gemini-2.5-flash"),      # Fast, cheap
    "analyzer": os.getenv("ANALYZER_MODEL", "gemini-2.5-pro"),        # Reasoning
    "spec_writer": os.getenv("SPEC_WRITER_MODEL", "gemini-2.5-pro"),  # Structured
    "validator": os.getenv("VALIDATOR_MODEL", "gemini-2.5-pro"),      # Quality check
}

# ============ Execution Modes ============

MODES = {
    "fast": {
        "num_questions": 6,
        "categories": ["CO", "KTO", "DLACZEGO", "JAK"],
        "estimated_time_minutes": 5,
    },
    "full": {
        "num_questions": 15,
        "categories": [
            "CO", "KTO", "GDZIE", "KIEDY", "DLACZEGO",
            "JAK", "ILE", "CO JEŚLI", "JAK MIERZYĆ", "INTEGRACJE"
        ],
        "estimated_time_minutes": 15,
    }
}

DEFAULT_MODE = os.getenv("DEFAULT_MODE", "full")

# ============ Zachman Framework ============

ZACHMAN_CATEGORIES = {
    "CO": {
        "name": "WHAT",
        "description": "Dane, encje, pola",
        "english": "Data Entities",
    },
    "KTO": {
        "name": "WHO",
        "description": "Użytkownicy, role, uprawnienia",
        "english": "Users and Roles",
    },
    "GDZIE": {
        "name": "WHERE",
        "description": "Dostęp, granice, lokalizacja",
        "english": "Access and Boundaries",
    },
    "KIEDY": {
        "name": "WHEN",
        "description": "Timing, triggery, zdarzenia",
        "english": "Timing and Events",
    },
    "DLACZEGO": {
        "name": "WHY",
        "description": "Reguły biznesowe, ograniczenia",
        "english": "Business Rules",
    },
    "JAK": {
        "name": "HOW",
        "description": "Mechanizmy, procesy, obsługa błędów",
        "english": "Mechanisms and Processes",
    },
    "ILE": {
        "name": "HOW MUCH",
        "description": "Skalowanie, wydajność, limity",
        "english": "Scale and Performance",
    },
    "CO JEŚLI": {
        "name": "WHAT IF",
        "description": "Edge cases, failover, scenariusze awaryjne",
        "english": "Edge Cases and Failover",
    },
    "JAK MIERZYĆ": {
        "name": "HOW TO MEASURE",
        "description": "Metryki, monitoring, alerty",
        "english": "Metrics and Monitoring",
    },
    "INTEGRACJE": {
        "name": "INTEGRATIONS",
        "description": "Systemy zewnętrzne, protokoły",
        "english": "External Integrations",
    },
}

# ============ Output Paths ============

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
SESSION_DIR = os.path.join(OUTPUT_DIR, ".sessions")
LOGS_DIR = os.getenv("LOGS_DIR", "logs")

# Create directories if don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ============ Logging ============

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============ Limits and Constraints ============

MAX_RETRIES = 3
TIMEOUT_SECONDS = 60
MAX_TOKENS = 4096

# ============ Feature Flags ============

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"
