"""Zachman Framework Questions - 10 Categories × Multiple Depth Levels"""

from typing import List, Dict

# Questions organized by Zachman category
# Each question has: id, text, category, required, priority

ZACHMAN_QUESTIONS = {
    "CO": {
        "name": "WHAT - Dane i Encje",
        "description": "Jakie dane będą przechowywane w systemie?",
        "questions": [
            {
                "id": "CO-01",
                "text": "Jakie główne dane będą przechowywane?",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "CO-02",
                "text": "Jaka struktura danych? (np. entity relationships)",
                "priority": "high",
                "depth": "full",
            },
            {
                "id": "CO-03",
                "text": "Jak długo przechowywać dane? (retention policy)",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "KTO": {
        "name": "WHO - Użytkownicy i Role",
        "description": "Kto będzie używać ten system?",
        "questions": [
            {
                "id": "KTO-01",
                "text": "Jakie role będą w systemie? (np. admin, user, moderator)",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "KTO-02",
                "text": "Jakie uprawnienia ma każda rola?",
                "priority": "high",
                "depth": "full",
            },
            {
                "id": "KTO-03",
                "text": "Ilu użytkowników będzie w systemie?",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "GDZIE": {
        "name": "WHERE - Dostęp i Lokalizacja",
        "description": "Gdzie system będzie dostępny?",
        "questions": [
            {
                "id": "GDZIE-01",
                "text": "Skąd użytkownicy będą dostępu do systemu? (web, mobile, API)",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "GDZIE-02",
                "text": "Jakie są granice dostępu? (np. tylko z sieci firmowej)",
                "priority": "medium",
                "depth": "full",
            },
            {
                "id": "GDZIE-03",
                "text": "Czy system będzie globalne czy lokalny?",
                "priority": "low",
                "depth": "full",
            },
        ],
    },
    "KIEDY": {
        "name": "WHEN - Timing i Zdarzenia",
        "description": "Kiedy różne zdarzenia zachodzą w systemie?",
        "questions": [
            {
                "id": "KIEDY-01",
                "text": "Kiedy system będzie dostępny? (24/7, business hours)",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "KIEDY-02",
                "text": "Jakie są główne zdarzenia w systemie? (np. order placed, user registered)",
                "priority": "high",
                "depth": "full",
            },
            {
                "id": "KIEDY-03",
                "text": "Czy są deadline'y lub SLA'e?",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "DLACZEGO": {
        "name": "WHY - Reguły Biznesowe",
        "description": "Jakie są reguły biznesowe?",
        "questions": [
            {
                "id": "DLACZEGO-01",
                "text": "Jakie są główne reguły biznesowe? (np. admins approve orders)",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "DLACZEGO-02",
                "text": "Jakie ograniczenia musi spełniać system?",
                "priority": "high",
                "depth": "full",
            },
            {
                "id": "DLACZEGO-03",
                "text": "Jakie compliance requierements? (GDPR, etc)",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "JAK": {
        "name": "HOW - Mechanizmy i Procesy",
        "description": "Jak system będzie działać?",
        "questions": [
            {
                "id": "JAK-01",
                "text": "Jaki jest główny flow/proces w systemie?",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "JAK-02",
                "text": "Jak obsługiwane są błędy? (error handling, retries)",
                "priority": "high",
                "depth": "full",
            },
            {
                "id": "JAK-03",
                "text": "Jakie są security mechanisms? (auth, encryption)",
                "priority": "high",
                "depth": "full",
            },
        ],
    },
    "ILE": {
        "name": "HOW MUCH - Skalowanie i Wydajność",
        "description": "Jakie są wymagania na skalowanie?",
        "questions": [
            {
                "id": "ILE-01",
                "text": "Jakie są wymagania wydajności? (requests per second, latency)",
                "priority": "medium",
                "depth": "fast",
            },
            {
                "id": "ILE-02",
                "text": "Jak duże mogą być dane? (storage requirements)",
                "priority": "medium",
                "depth": "full",
            },
            {
                "id": "ILE-03",
                "text": "Ile jednoczesnych użytkowników?",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "CO JEŚLI": {
        "name": "WHAT IF - Edge Cases i Failover",
        "description": "Co się dzieje w wyjątkowych sytuacjach?",
        "questions": [
            {
                "id": "CO JEŚLI-01",
                "text": "Co się dzieje jeśli systemy się połamią? (failover strategy)",
                "priority": "medium",
                "depth": "fast",
            },
            {
                "id": "CO JEŚLI-02",
                "text": "Jakie edge cases powinny być obsługiwane?",
                "priority": "medium",
                "depth": "full",
            },
            {
                "id": "CO JEŚLI-03",
                "text": "Jak system reaguje na nadzwyczajne warunki?",
                "priority": "low",
                "depth": "full",
            },
        ],
    },
    "JAK MIERZYĆ": {
        "name": "HOW TO MEASURE - Metryki i Monitoring",
        "description": "Jak będzie monitorowany system?",
        "questions": [
            {
                "id": "JAK MIERZYĆ-01",
                "text": "Jakie metryki są ważne? (uptime, latency, errors)",
                "priority": "high",
                "depth": "fast",
            },
            {
                "id": "JAK MIERZYĆ-02",
                "text": "Jakie alerty powinny być ustawione?",
                "priority": "medium",
                "depth": "full",
            },
            {
                "id": "JAK MIERZYĆ-03",
                "text": "Jak będą zbierane logi i metrics?",
                "priority": "medium",
                "depth": "full",
            },
        ],
    },
    "INTEGRACJE": {
        "name": "INTEGRATIONS - Systemy Zewnętrzne",
        "description": "Jakie systemy będą zintegrowane?",
        "questions": [
            {
                "id": "INTEGRACJE-01",
                "text": "Jakie systemy muszą być zintegrowane?",
                "priority": "medium",
                "depth": "fast",
            },
            {
                "id": "INTEGRACJE-02",
                "text": "Jakie protokoły/API będą używane?",
                "priority": "medium",
                "depth": "full",
            },
            {
                "id": "INTEGRACJE-03",
                "text": "Jakie są dependency na zewnętrzne systemy? (criticality)",
                "priority": "low",
                "depth": "full",
            },
        ],
    },
}


def get_questions_by_mode(mode: str) -> List[Dict]:
    """Get questions filtered by execution mode (fast or full)"""
    questions = []
    for category, data in ZACHMAN_QUESTIONS.items():
        for question in data["questions"]:
            if question["depth"] == "fast" or mode == "full":
                questions.append(question)
    return sorted(questions, key=lambda x: x["priority"])


def get_questions_by_category(category: str) -> List[Dict]:
    """Get all questions for a specific Zachman category"""
    if category in ZACHMAN_QUESTIONS:
        return ZACHMAN_QUESTIONS[category]["questions"]
    return []


def get_all_categories() -> List[str]:
    """Get list of all Zachman categories"""
    return list(ZACHMAN_QUESTIONS.keys())
