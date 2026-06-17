"""Gatherer Agent - auto-generates answers using LLM based on system description"""

import logging
import json
from typing import List
from schemas import GathererOutput, Answer, UserInput
from framework import get_questions_by_mode, ZACHMAN_QUESTIONS
from .base import GathererAgent
from . import backends
import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Jesteś ekspertem od analizy systemów informatycznych.
Na podstawie opisu systemu odpowiedz wyczerpująco na pytania dotyczące systemu.
Twoje odpowiedzi będą użyte do wygenerowania specyfikacji systemu.

Zasady:
- Odpowiadaj w języku polskim
- Bądź konkretny i szczegółowy
- Jeśli opis nie zawiera wystarczających informacji, wnioskuj z kontekstu i zaznacz to
- Odpowiedzi powinny być zwięzłe ale kompletne (2-5 zdań)
"""


class GathererAgentImpl(GathererAgent):
    """Implementation of Gatherer Agent

    Automatically generates answers to Zachman questions using LLM,
    based on the system description provided by the user.
    """

    def __init__(self, model: str = None):
        super().__init__(name="Gatherer Agent", model=model)
        self.backend = backends.get_backend()
        self.model = model or config.MODELS.get("gatherer", config.LLM_MODEL)

    def execute(self, user_input: UserInput) -> GathererOutput:
        """Auto-generate answers to Zachman questions using LLM

        Args:
            user_input: System description and mode

        Returns:
            GathererOutput with LLM-generated answers for all questions
        """
        logger.info(f"Gatherer Agent starting - Mode: {user_input.mode}")

        questions = get_questions_by_mode(user_input.mode)
        logger.info(f"Generating answers for {len(questions)} questions...")

        answers = self._generate_answers(
            system_description=user_input.system_description,
            questions=questions,
        )

        output = GathererOutput(
            system_name=self._extract_system_name(user_input.system_description),
            system_description=user_input.system_description,
            answers=answers,
            mode=user_input.mode,
            num_questions_asked=len(questions),
            completion_percentage=1.0,
        )

        self.log_execution(
            input_summary=f"System: {user_input.system_description}",
            output_summary=f"Generated {len(answers)} answers",
        )

        return output

    def _generate_answers(
        self,
        system_description: str,
        questions: List[dict],
    ) -> List[Answer]:
        """Generate answers to all questions using LLM in one call

        Sends all questions in a single prompt and parses JSON response.

        Args:
            system_description: System description
            questions: List of Zachman questions

        Returns:
            List of Answer objects
        """
        # Build prompt with all questions
        questions_block = "\n".join(
            f'  {{ "id": "{q["id"]}", "question": "{q["text"]}" }}'
            for q in questions
        )

        prompt = f"""Opis systemu:
{system_description}

Odpowiedz na wszystkie poniższe pytania o tym systemie.

Pytania:
[
{questions_block}
]

Zwróć odpowiedzi jako JSON w dokładnie takim formacie:
{{
  "answers": [
    {{"id": "CO-01", "answer": "odpowiedź po polsku..."}},
    {{"id": "KTO-01", "answer": "odpowiedź po polsku..."}},
    ...
  ]
}}

Odpowiedz TYLKO jsonem, bez żadnego dodatkowego tekstu."""

        logger.debug("Calling LLM for batch answer generation...")
        raw = self.backend.call(prompt=prompt, system_prompt=SYSTEM_PROMPT, temperature=0.3)

        # Parse JSON response
        raw = raw.strip()
        if raw.startswith("```"):
            # Strip markdown code block if present
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

        data = json.loads(raw)
        answers_map = {item["id"]: item["answer"] for item in data["answers"]}

        # Build Answer objects
        answers = []
        for q in questions:
            qid = q["id"]
            category = qid.split("-")[0]
            answer_text = answers_map.get(qid, "Brak odpowiedzi")
            answers.append(Answer(
                question_id=qid,
                question_text=q["text"],
                answer_text=answer_text,
                category=category,
                confidence=self._estimate_confidence(answer_text),
            ))

        logger.info(f"Generated {len(answers)} answers")
        return answers

    def _estimate_confidence(self, answer_text: str) -> float:
        """Estimate confidence based on answer length"""
        words = len(answer_text.split())
        if words < 5:
            return 0.5
        elif words < 15:
            return 0.7
        elif words < 50:
            return 0.85
        else:
            return 0.95

    def _extract_system_name(self, description: str) -> str:
        """Extract system name from first 3 words of description"""
        words = description.split()[:3]
        return " ".join(words) if words else "System"


def create_gatherer(model: str = None) -> GathererAgent:
    """Factory function to create Gatherer Agent

    Args:
        model: LLM model to use

    Returns:
        Initialized Gatherer Agent
    """
    return GathererAgentImpl(model=model)
