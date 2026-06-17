"""Tests for Gatherer Agent"""

import pytest
import json
from unittest.mock import patch, MagicMock
from schemas import UserInput, Answer
from agents import create_gatherer
from framework import get_questions_by_mode


def _make_llm_response(questions: list) -> str:
    """Build a fake JSON response as if LLM answered all questions"""
    answers = [{"id": q["id"], "answer": f"Odpowiedz na pytanie {q['id']}"} for q in questions]
    return json.dumps({"answers": answers})


class TestGathererAgent:
    """Tests for Gatherer Agent implementation"""

    def test_gatherer_initialization(self):
        """Test gatherer initializes correctly"""
        gatherer = create_gatherer()
        assert gatherer is not None
        assert gatherer.name == "Gatherer Agent"

    def test_gatherer_with_custom_model(self):
        """Test gatherer with custom model"""
        gatherer = create_gatherer(model="claude-3-5-sonnet")
        assert gatherer.model == "claude-3-5-sonnet"

    def test_extract_system_name(self):
        """Test system name extraction"""
        gatherer = create_gatherer()

        assert gatherer._extract_system_name("E-commerce platform for selling") == "E-commerce platform for"
        assert gatherer._extract_system_name("Chat app") == "Chat app"
        assert gatherer._extract_system_name("System") == "System"

    def test_confidence_estimation(self):
        """Test confidence score estimation based on answer length"""
        gatherer = create_gatherer()

        assert gatherer._estimate_confidence("Yes") == 0.5
        assert gatherer._estimate_confidence("Short answer") == 0.5
        assert gatherer._estimate_confidence("This is a medium length answer") == 0.7

        long_answer = "This is a longer and more detailed answer that provides specific information about the system architecture and design decisions made"
        assert gatherer._estimate_confidence(long_answer) == 0.85

        very_long_answer = " ".join(["word"] * 55)
        assert gatherer._estimate_confidence(very_long_answer) == 0.95

    def test_answer_objects_structure(self):
        """Test that Answer objects have correct structure"""
        answer = Answer(
            question_id="CO-01",
            question_text="What is the main data?",
            answer_text="Users, products, orders",
            category="CO",
            confidence=0.8,
        )

        assert answer.question_id == "CO-01"
        assert answer.category == "CO"
        assert answer.confidence == 0.8
        assert len(answer.answer_text) > 0

    def test_gatherer_output_structure(self, sample_user_input):
        """Test GathererOutput has all required fields — LLM is mocked"""
        gatherer = create_gatherer()
        questions = get_questions_by_mode(sample_user_input.mode)

        fake_llm_response = _make_llm_response(questions)

        with patch.object(gatherer.backend, "call", return_value=fake_llm_response):
            output = gatherer.execute(sample_user_input)

        assert output.system_name is not None
        assert output.system_description == sample_user_input.system_description
        assert len(output.answers) == len(questions)
        assert output.mode == sample_user_input.mode
        assert output.completion_percentage == 1.0
        assert output.num_questions_asked == len(questions)

    def test_gatherer_each_answer_has_category(self, sample_user_input):
        """Test that each answer is assigned to correct Zachman category"""
        gatherer = create_gatherer()
        questions = get_questions_by_mode(sample_user_input.mode)

        with patch.object(gatherer.backend, "call", return_value=_make_llm_response(questions)):
            output = gatherer.execute(sample_user_input)

        for answer in output.answers:
            assert answer.category in [
                "CO", "KTO", "GDZIE", "KIEDY", "DLACZEGO",
                "JAK", "ILE", "CO JEŚLI", "JAK MIERZYĆ", "INTEGRACJE",
            ]

    def test_gatherer_handles_markdown_codeblock(self, sample_user_input):
        """Test that LLM response wrapped in markdown code block is handled"""
        gatherer = create_gatherer()
        questions = get_questions_by_mode(sample_user_input.mode)

        json_data = _make_llm_response(questions)
        wrapped = f"```json\n{json_data}\n```"

        with patch.object(gatherer.backend, "call", return_value=wrapped):
            output = gatherer.execute(sample_user_input)

        assert len(output.answers) == len(questions)

    def test_questions_loaded_for_fast_mode(self):
        """Test questions loaded for fast mode"""
        questions = get_questions_by_mode("fast")
        assert len(questions) > 0

    def test_questions_loaded_for_full_mode(self):
        """Test full mode loads more questions than fast"""
        fast = get_questions_by_mode("fast")
        full = get_questions_by_mode("full")
        assert len(full) > len(fast)
