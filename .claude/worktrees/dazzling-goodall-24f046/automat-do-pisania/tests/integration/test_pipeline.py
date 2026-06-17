"""Integration tests for the complete pipeline"""

import pytest
from schemas import UserInput
from pipeline import Pipeline


class TestPipeline:
    """Tests for the complete pipeline"""

    def test_pipeline_initialization(self):
        """Test pipeline initializes with all agents"""
        pipeline = Pipeline()
        assert pipeline.gatherer is not None
        assert pipeline.analyzer is not None
        assert pipeline.spec_writer is not None
        assert pipeline.validator is not None

    @pytest.mark.skip(reason="Requires full agent implementation")
    def test_pipeline_fast_mode_execution(self, sample_user_input):
        """Test pipeline execution in fast mode"""
        sample_user_input.mode = "fast"
        pipeline = Pipeline()
        session = pipeline.execute(sample_user_input)

        assert session is not None
        assert session.completed is True
        assert session.gatherer_output is not None
        assert session.analyzer_output is not None
        assert session.spec_output is not None
        assert session.validator_output is not None

    @pytest.mark.skip(reason="Requires full agent implementation")
    def test_pipeline_full_mode_execution(self, sample_user_input):
        """Test pipeline execution in full mode"""
        sample_user_input.mode = "full"
        pipeline = Pipeline()
        session = pipeline.execute(sample_user_input)

        assert session.completed is True
        assert len(session.user_input.system_description) > 0

    def test_pipeline_session_initialization(self, sample_user_input):
        """Test pipeline initializes session correctly"""
        pipeline = Pipeline()
        # Execute will initialize session (even if it fails)
        try:
            pipeline.execute(sample_user_input)
        except:
            pass

        assert pipeline.session is not None
        assert pipeline.session.user_input == sample_user_input
        assert pipeline.session.mode == sample_user_input.mode
