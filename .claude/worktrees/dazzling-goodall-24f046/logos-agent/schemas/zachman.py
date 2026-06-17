"""Pydantic modele dla ZachmanModel — AI's Contract.

Te struktury są wymuszane przez Gemini structured output (response_schema)
w SynthesisAgent. Wszystkie pola po polsku, opisy w prompcie.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(description="Nazwa encji, np. 'Zamówienie'")
    states: list[str] = Field(
        default_factory=list,
        description="Możliwe stany encji, np. ['robocze', 'złożone', 'anulowane']"
    )
    relationships: list[str] = Field(
        default_factory=list,
        description="Relacje do innych encji, np. ['należy do Użytkownika']"
    )
    fields: list[str] = Field(
        default_factory=list,
        description="Kluczowe pola encji"
    )


class Actor(BaseModel):
    name: str = Field(description="Nazwa aktora, np. 'Klient'")
    can: list[str] = Field(
        default_factory=list,
        description="Konkretne akcje które może wykonać"
    )
    cannot: list[str] = Field(
        default_factory=list,
        description="Akcje których wykonywać NIE może"
    )


class Rule(BaseModel):
    id: str = Field(description="Identyfikator reguły, np. 'R1'")
    condition: str = Field(description="Warunek wyrażony konkretnie, np. 'czas_od_złożenia > 1h'")
    action: str = Field(description="Akcja podejmowana gdy warunek spełniony")
    rationale: str = Field(default="", description="Dlaczego ta reguła istnieje")


class Event(BaseModel):
    trigger: str = Field(description="Zdarzenie wyzwalające, np. 'zamowienie.zlozone'")
    action: str = Field(description="Akcja podejmowana w odpowiedzi")
    outcome: str = Field(description="Obserwowalny rezultat akcji")


class Integration(BaseModel):
    system: str = Field(description="Nazwa systemu zewnętrznego")
    direction: Literal["inbound", "outbound", "bidirectional"]
    protocol: str = Field(description="REST, webhook, SMTP, gRPC, ...")
    critical: bool = Field(description="Czy awaria tej integracji blokuje system")


class Scale(BaseModel):
    concurrent_users: int | None = None
    response_time_ms: int | None = None
    uptime_pct: float | None = None
    data_volume_per_day: str | None = None


class ZachmanModel(BaseModel):
    """Pełny ustrukturyzowany model systemu — AI's Contract."""
    system: str
    generated: str = Field(description="Data wygenerowania w formacie ISO")
    ambiguity_score: float = Field(
        ge=0.0, le=1.0,
        description="0.0 = pełna precyzja, 1.0 = same ogólniki"
    )
    entities: list[Entity] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    rules: list[Rule] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    tech_constraints: list[str] = Field(default_factory=list)
    scale: Scale = Field(default_factory=Scale)


class CritiqueFinding(BaseModel):
    severity: Literal["high", "medium", "low"]
    where: str = Field(description="Lokalizacja w modelu, np. 'rules.R3'")
    issue: str = Field(description="Co jest nie tak")
    fix: str = Field(description="Sugestia naprawy")


class CritiqueReport(BaseModel):
    findings: list[CritiqueFinding] = Field(default_factory=list)
