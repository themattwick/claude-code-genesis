"""SessionState — pełny stan pipeline serializowany do JSON dla save/resume."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


Mode = Literal["fast", "full"]
Phase = Literal[
    "context", "drafts", "cp1", "interview", "cp2",
    "synthesis", "critique", "cp3", "export", "done"
]


class GapQuestion(BaseModel):
    question: str
    target_question_ids: list[int] = Field(
        default_factory=list,
        description="Pytania z głównej listy 1-100 do których ta luka się odnosi"
    )


class RiskHit(BaseModel):
    question_id: int
    word: str
    why: str


class ConflictHit(BaseModel):
    pair_title: str
    a_id: int
    b_id: int
    overlap: list[str] = Field(default_factory=list)
    note: str = ""


class SessionState(BaseModel):
    system_name: str
    description: str
    mode: Mode = "full"
    phase: Phase = "context"
    iteration: int = 0  # liczba pętli redukcji niejednoznaczności w CP3

    zachman_context: dict | None = None  # wstępna hipoteza z ContextAgent
    drafts: dict[int, str] = Field(default_factory=dict)
    reviewed: dict[int, str] = Field(default_factory=dict)
    gap_questions: list[GapQuestion] = Field(default_factory=list)
    gap_answers: dict[int, str] = Field(default_factory=dict)  # indeks po gap_questions
    final_answers: dict[int, str] = Field(default_factory=dict)
    zachman_model: dict | None = None  # serializowany ZachmanModel
    critique: list[dict] = Field(default_factory=list)
    risks: list[RiskHit] = Field(default_factory=list)
    conflicts: list[ConflictHit] = Field(default_factory=list)

    def slug(self) -> str:
        """Bezpieczna nazwa pliku z system_name."""
        import re
        s = self.system_name.lower().strip()
        s = re.sub(r"[^a-z0-9-]+", "-", s)
        return s.strip("-") or "spec"
