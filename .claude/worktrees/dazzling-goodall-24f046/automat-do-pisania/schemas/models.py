"""Pydantic models (data contracts) for Automat do Pisania"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============ INPUT CONTRACTS ============

class UserInput(BaseModel):
    """Initial user input - starting the spec writing process"""
    system_description: str = Field(..., description="Short description of the system (1-2 sentences)")
    mode: str = Field(default="full", description="'fast' or 'full' mode")
    timestamp: datetime = Field(default_factory=datetime.now)


class Answer(BaseModel):
    """Single answer to a question"""
    question_id: str
    question_text: str
    answer_text: str
    category: str  # CO, KTO, GDZIE, etc.
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


# ============ GATHERER OUTPUT ============

class GathererOutput(BaseModel):
    """Output from Agent Zbierający (Information Gatherer)"""
    system_name: str
    system_description: str
    answers: List[Answer]
    mode: str
    num_questions_asked: int
    completion_percentage: float = Field(ge=0.0, le=1.0)


# ============ ANALYZER OUTPUT ============

class Contradiction(BaseModel):
    """Detected contradiction between answers"""
    answer_ids: List[str]
    description: str
    severity: str = Field(default="medium")  # low, medium, high


class Gap(BaseModel):
    """Identified gap in information"""
    category: str
    description: str
    suggested_question: str


class AnalyzerOutput(BaseModel):
    """Output from Agent Analizujący (Analyzer)"""
    contradictions_found: List[Contradiction]
    gaps_found: List[Gap]
    missing_details: List[str]
    completeness_score: float = Field(ge=0.0, le=1.0)
    recommendation: str  # COMPLETE, NEEDS_MORE_INFO, ASK_FOLLOW_UP
    follow_up_questions: List[str] = Field(default_factory=list)


# ============ ZACHMAN MODEL ============

class Entity(BaseModel):
    """Data entity in the system"""
    name: str
    description: str
    fields: Dict[str, str]  # field_name: field_type


class Actor(BaseModel):
    """User role or actor"""
    name: str
    description: str
    permissions: List[str]
    responsibilities: List[str]


class Rule(BaseModel):
    """Business rule"""
    id: str
    name: str
    description: str
    category: str


class Event(BaseModel):
    """System event"""
    name: str
    trigger: str
    action: str
    result: str


class Integration(BaseModel):
    """External system integration"""
    system_name: str
    protocol: str
    data_exchange: str
    criticality: str  # critical, important, optional


class ZachmanCategory(BaseModel):
    """Single Zachman category with all its data"""
    name: str  # CO, KTO, GDZIE, etc.
    description: str
    content: Dict[str, Any]  # Flexible content for each category


class ZachmanModel(BaseModel):
    """Complete Zachman specification model"""
    system_name: str
    system_description: str
    created_at: datetime
    updated_at: datetime
    mode: str  # fast or full

    # Zachman categories
    co_what: Optional[Dict[str, Any]] = None
    kto_who: Optional[Dict[str, Any]] = None
    gdzie_where: Optional[Dict[str, Any]] = None
    kiedy_when: Optional[Dict[str, Any]] = None
    dlaczego_why: Optional[Dict[str, Any]] = None
    jak_how: Optional[Dict[str, Any]] = None
    ile_how_much: Optional[Dict[str, Any]] = None
    co_jesli_what_if: Optional[Dict[str, Any]] = None
    jak_mierzyc_how_to_measure: Optional[Dict[str, Any]] = None
    integracje_integrations: Optional[Dict[str, Any]] = None

    # Quality metrics
    ambiguity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    consistency_score: float = Field(default=0.0, ge=0.0, le=1.0)


# ============ SPEC WRITER OUTPUT ============

class SpecOutput(BaseModel):
    """Output from Agent Piszący (Spec Writer)"""
    title: str
    markdown_spec: str
    json_contract: ZachmanModel
    tables_and_diagrams: str
    generation_timestamp: datetime = Field(default_factory=datetime.now)


# ============ VALIDATOR OUTPUT ============

class ValidationIssue(BaseModel):
    """Single validation issue"""
    severity: str  # info, warning, error
    category: str
    description: str
    suggestion: str


class ValidatorOutput(BaseModel):
    """Output from Agent Walidujący (Validator)"""
    all_categories_present: bool
    issues: List[ValidationIssue]
    quality_score: float = Field(ge=0.0, le=1.0)
    recommendation: str  # ACCEPT, REVISE, GATHER_MORE
    summary: str
    validation_timestamp: datetime = Field(default_factory=datetime.now)


# ============ SESSION STATE ============

class SessionState(BaseModel):
    """Complete session state for save/resume"""
    session_id: str
    user_input: UserInput

    # Phase outputs
    gatherer_output: Optional[GathererOutput] = None
    analyzer_output: Optional[AnalyzerOutput] = None
    spec_output: Optional[SpecOutput] = None
    validator_output: Optional[ValidatorOutput] = None

    # Current phase
    current_phase: str  # gather, analyze, write, validate
    iteration_count: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Metadata
    mode: str
    completed: bool = False
