"""Pytest configuration and shared fixtures"""

import pytest
from datetime import datetime
from schemas import UserInput, Answer, GathererOutput, AnalyzerOutput, SpecOutput, ZachmanModel


@pytest.fixture
def sample_user_input():
    """Sample user input for testing"""
    return UserInput(
        system_description="E-commerce platform for selling products online",
        mode="fast",
    )


@pytest.fixture
def sample_answers():
    """Sample answers for testing"""
    return [
        Answer(
            question_id="CO-01",
            question_text="Jakie główne dane będą przechowywane?",
            answer_text="Produkty, użytkownicy, zamówienia",
            category="CO",
            confidence=0.9,
        ),
        Answer(
            question_id="KTO-01",
            question_text="Jakie role będą w systemie?",
            answer_text="Admin, customer, seller",
            category="KTO",
            confidence=0.85,
        ),
        Answer(
            question_id="DLACZEGO-01",
            question_text="Jakie są główne reguły biznesowe?",
            answer_text="Admin zatwierdza produkty, customers mogą zamawiać",
            category="DLACZEGO",
            confidence=0.8,
        ),
    ]


@pytest.fixture
def sample_gatherer_output(sample_user_input, sample_answers):
    """Sample gatherer output"""
    return GathererOutput(
        system_name="E-commerce Platform",
        system_description=sample_user_input.system_description,
        answers=sample_answers,
        mode=sample_user_input.mode,
        num_questions_asked=6,
        completion_percentage=1.0,
    )


@pytest.fixture
def sample_analyzer_output():
    """Sample analyzer output"""
    return AnalyzerOutput(
        contradictions_found=[],
        gaps_found=[],
        missing_details=[],
        completeness_score=0.85,
        recommendation="COMPLETE",
    )


@pytest.fixture
def sample_zachman_model(sample_user_input):
    """Sample Zachman model"""
    return ZachmanModel(
        system_name="E-commerce Platform",
        system_description=sample_user_input.system_description,
        mode="fast",
        co_what={
            "entities": ["Product", "User", "Order"],
        },
        kto_who={
            "roles": ["Admin", "Customer", "Seller"],
        },
    )


@pytest.fixture
def sample_spec_output(sample_zachman_model):
    """Sample spec output"""
    return SpecOutput(
        title="Specyfikacja: E-commerce Platform",
        markdown_spec="# E-commerce Platform\n\n## CO\nEntities: Product, User, Order",
        json_contract=sample_zachman_model,
        tables_and_diagrams="## Tables\n\n| Entity | Fields |\n|--------|--------|\n| Product | id, name, price |",
    )
