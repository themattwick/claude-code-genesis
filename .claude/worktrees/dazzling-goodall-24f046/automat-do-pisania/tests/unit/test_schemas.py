"""Tests for Pydantic schemas"""

import pytest
from datetime import datetime
from schemas import (
    UserInput,
    Answer,
    GathererOutput,
    AnalyzerOutput,
    ZachmanModel,
    SpecOutput,
    ValidatorOutput,
    SessionState,
)


class TestUserInput:
    """Tests for UserInput schema"""

    def test_user_input_valid(self):
        """Test valid user input"""
        user_input = UserInput(
            system_description="E-commerce platform",
            mode="fast",
        )
        assert user_input.system_description == "E-commerce platform"
        assert user_input.mode == "fast"

    def test_user_input_requires_description(self):
        """Test that system_description is required"""
        with pytest.raises(ValueError):
            UserInput(mode="fast")

    def test_user_input_default_mode(self):
        """Test default mode"""
        user_input = UserInput(system_description="System")
        assert user_input.mode == "full"


class TestAnswer:
    """Tests for Answer schema"""

    def test_answer_valid(self):
        """Test valid answer"""
        answer = Answer(
            question_id="CO-01",
            question_text="What data?",
            answer_text="Users and products",
            category="CO",
            confidence=0.9,
        )
        assert answer.confidence == 0.9
        assert answer.category == "CO"

    def test_answer_confidence_bounds(self):
        """Test confidence is between 0 and 1"""
        with pytest.raises(ValueError):
            Answer(
                question_id="CO-01",
                question_text="What data?",
                answer_text="Users",
                category="CO",
                confidence=1.5,  # Invalid
            )


class TestGathererOutput:
    """Tests for GathererOutput schema"""

    def test_gatherer_output_valid(self, sample_gatherer_output):
        """Test valid gatherer output"""
        assert sample_gatherer_output.system_name == "E-commerce Platform"
        assert len(sample_gatherer_output.answers) == 3
        assert sample_gatherer_output.completion_percentage == 1.0

    def test_gatherer_output_completion_percentage(self):
        """Test completion_percentage bounds"""
        with pytest.raises(ValueError):
            GathererOutput(
                system_name="System",
                system_description="Desc",
                answers=[],
                mode="fast",
                num_questions_asked=6,
                completion_percentage=1.5,  # Invalid
            )


class TestAnalyzerOutput:
    """Tests for AnalyzerOutput schema"""

    def test_analyzer_output_valid(self, sample_analyzer_output):
        """Test valid analyzer output"""
        assert sample_analyzer_output.completeness_score == 0.85
        assert sample_analyzer_output.recommendation == "COMPLETE"

    def test_analyzer_output_recommendations(self):
        """Test valid recommendations"""
        valid_recommendations = ["COMPLETE", "NEEDS_MORE_INFO", "ASK_FOLLOW_UP"]
        for rec in valid_recommendations:
            output = AnalyzerOutput(
                contradictions_found=[],
                gaps_found=[],
                missing_details=[],
                completeness_score=0.5,
                recommendation=rec,
            )
            assert output.recommendation == rec


class TestZachmanModel:
    """Tests for ZachmanModel schema"""

    def test_zachman_model_valid(self, sample_zachman_model):
        """Test valid Zachman model"""
        assert sample_zachman_model.system_name == "E-commerce Platform"
        assert sample_zachman_model.mode == "fast"

    def test_zachman_model_scores_bounds(self):
        """Test all scores are between 0 and 1"""
        with pytest.raises(ValueError):
            ZachmanModel(
                system_name="System",
                system_description="Desc",
                mode="fast",
                ambiguity_score=1.5,  # Invalid
            )

    def test_zachman_model_optional_categories(self):
        """Test that Zachman categories are optional"""
        model = ZachmanModel(
            system_name="System",
            system_description="Desc",
            mode="fast",
        )
        assert model.co_what is None
        assert model.kto_who is None


class TestSpecOutput:
    """Tests for SpecOutput schema"""

    def test_spec_output_valid(self, sample_spec_output):
        """Test valid spec output"""
        assert sample_spec_output.title == "Specyfikacja: E-commerce Platform"
        assert "# E-commerce Platform" in sample_spec_output.markdown_spec
        assert sample_spec_output.json_contract.system_name == "E-commerce Platform"


class TestValidatorOutput:
    """Tests for ValidatorOutput schema"""

    def test_validator_output_valid(self):
        """Test valid validator output"""
        output = ValidatorOutput(
            all_categories_present=True,
            issues=[],
            quality_score=0.95,
            recommendation="ACCEPT",
            summary="Specification is good",
        )
        assert output.quality_score == 0.95
        assert output.recommendation == "ACCEPT"

    def test_validator_output_quality_score_bounds(self):
        """Test quality score bounds"""
        with pytest.raises(ValueError):
            ValidatorOutput(
                all_categories_present=True,
                issues=[],
                quality_score=1.5,  # Invalid
                recommendation="ACCEPT",
                summary="Test",
            )


class TestSessionState:
    """Tests for SessionState schema"""

    def test_session_state_valid(self, sample_user_input):
        """Test valid session state"""
        session = SessionState(
            session_id="session-001",
            user_input=sample_user_input,
            mode="fast",
        )
        assert session.session_id == "session-001"
        assert session.completed is False
        assert session.iteration_count == 0

    def test_session_state_default_timestamps(self, sample_user_input):
        """Test default timestamps"""
        session = SessionState(
            session_id="session-001",
            user_input=sample_user_input,
            mode="fast",
        )
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_updated, datetime)

    def test_session_state_phases(self, sample_user_input):
        """Test valid phases"""
        valid_phases = ["gather", "analyze", "write", "validate", "done"]
        for phase in valid_phases:
            session = SessionState(
                session_id="session-001",
                user_input=sample_user_input,
                mode="fast",
                current_phase=phase,
            )
            assert session.current_phase == phase
