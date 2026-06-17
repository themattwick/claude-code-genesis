"""Analyzer Agent - finds gaps and contradictions in LLM-generated answers"""

import logging
import json
from typing import List
from schemas import AnalyzerOutput, GathererOutput, Contradiction, Gap
from .base import AnalyzerAgent
from . import backends
import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Jesteś ekspertem od analizy specyfikacji systemów informatycznych.
Przeanalizuj odpowiedzi na pytania Zachman i znajdź:
1. Sprzeczności - gdy dwie odpowiedzi sobie przeczą
2. Luki - brakujące ważne informacje
3. Niejasności - odpowiedzi zbyt ogólne lub niejednoznaczne

Odpowiadaj zawsze po polsku, zwięźle i konkretnie.
"""


class AnalyzerAgentImpl(AnalyzerAgent):
    """Analyzes LLM-generated answers for contradictions, gaps, and completeness."""

    def __init__(self, model: str = None):
        super().__init__(name="Analyzer Agent", model=model)
        self.backend = backends.get_backend()
        self.model = model or config.MODELS.get("analyzer", config.LLM_MODEL)

    def execute(self, gatherer_output: GathererOutput) -> AnalyzerOutput:
        """Analyze gathered answers using LLM.

        Args:
            gatherer_output: Output from Gatherer Agent

        Returns:
            AnalyzerOutput with contradictions, gaps, and recommendation
        """
        logger.info(f"Analyzer Agent starting - {len(gatherer_output.answers)} answers to analyze")

        # Build Q&A block for the prompt
        qa_block = "\n".join(
            f"[{a.category}] {a.question_text}\n  Odpowiedź: {a.answer_text}"
            for a in gatherer_output.answers
        )

        prompt = f"""System: {gatherer_output.system_description}

Odpowiedzi na pytania Zachman:
{qa_block}

Przeanalizuj powyższe odpowiedzi i zwróć wynik w JSON:
{{
  "contradictions": [
    {{
      "answer_ids": ["CO-01", "KTO-01"],
      "description": "opis sprzeczności po polsku",
      "severity": "low|medium|high"
    }}
  ],
  "gaps": [
    {{
      "category": "KTO",
      "description": "opis brakującej informacji",
      "suggested_question": "pytanie które uzupełni lukę"
    }}
  ],
  "missing_details": ["brakujący szczegół 1", "brakujący szczegół 2"],
  "completeness_score": 0.85,
  "recommendation": "COMPLETE|NEEDS_MORE_INFO|ASK_FOLLOW_UP",
  "follow_up_questions": ["pytanie 1", "pytanie 2"]
}}

Zwróć TYLKO JSON bez żadnego dodatkowego tekstu.
Jeśli nie ma sprzeczności lub luk, zwróć puste listy.
completeness_score to liczba 0.0-1.0 oznaczająca jak kompletne są odpowiedzi."""

        logger.debug("Calling LLM for analysis...")
        raw = self.backend.call(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.2)

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

        data = json.loads(raw)

        contradictions = [Contradiction(**c) for c in data.get("contradictions", [])]
        gaps = [Gap(**g) for g in data.get("gaps", [])]

        output = AnalyzerOutput(
            contradictions_found=contradictions,
            gaps_found=gaps,
            missing_details=data.get("missing_details", []),
            completeness_score=float(data.get("completeness_score", 0.5)),
            recommendation=data.get("recommendation", "NEEDS_MORE_INFO"),
            follow_up_questions=data.get("follow_up_questions", []),
        )

        self.log_execution(
            input_summary=f"System: {gatherer_output.system_name}",
            output_summary=(
                f"Contradictions: {len(contradictions)}, "
                f"Gaps: {len(gaps)}, "
                f"Score: {output.completeness_score:.0%}, "
                f"Recommendation: {output.recommendation}"
            ),
        )

        return output


def create_analyzer(model: str = None) -> AnalyzerAgent:
    """Factory function to create Analyzer Agent"""
    return AnalyzerAgentImpl(model=model)
