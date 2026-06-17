"""Pipeline Orchestrator - manages the flow of all agents"""

import logging
from typing import Optional
from schemas import UserInput, SessionState
from agents import create_gatherer, create_analyzer, create_spec_writer, create_validator
import config

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestrating all agents"""

    def __init__(self):
        """Initialize pipeline with all agents"""
        self.gatherer = create_gatherer()
        self.analyzer = create_analyzer()
        self.spec_writer = create_spec_writer()
        self.validator = create_validator()
        self.session: Optional[SessionState] = None

    def execute(self, user_input: UserInput) -> SessionState:
        """Execute full pipeline

        Flow:
        1. GATHER: Collect answers from user
        2. ANALYZE: Check for gaps and contradictions
        3. WRITE: Generate specification
        4. VALIDATE: Check quality
        5. LOOP: If issues, optionally return to GATHER

        Args:
            user_input: Initial user input

        Returns:
            Final SessionState with all results
        """
        logger.info("Pipeline starting")
        logger.debug(f"Mode: {user_input.mode}")

        # Initialize session
        self.session = SessionState(
            session_id="session-001",  # TODO: Generate unique ID
            user_input=user_input,
            mode=user_input.mode,
            current_phase="gather",
        )

        # Phase 1: GATHER
        logger.info("Phase 1: GATHER - Collecting information from user")
        try:
            self.session.gatherer_output = self.gatherer.execute(user_input)
            self.session.current_phase = "analyze"
            logger.info("✓ Phase 1 complete")
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            raise

        # Phase 2: ANALYZE
        logger.info("Phase 2: ANALYZE - Checking for gaps and contradictions")
        try:
            self.session.analyzer_output = self.analyzer.execute(
                self.session.gatherer_output
            )
            self.session.current_phase = "write"
            logger.info("✓ Phase 2 complete")
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            raise

        # Phase 3: WRITE
        logger.info("Phase 3: WRITE - Generating specification")
        try:
            self.session.spec_output = self.spec_writer.execute(
                self.session.gatherer_output,
                self.session.analyzer_output,
            )
            self.session.current_phase = "validate"
            logger.info("✓ Phase 3 complete")
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            raise

        # Phase 4: VALIDATE
        logger.info("Phase 4: VALIDATE - Checking specification quality")
        try:
            self.session.validator_output = self.validator.execute(
                self.session.spec_output
            )
            self.session.current_phase = "done"
            self.session.completed = True
            logger.info("✓ Phase 4 complete")
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            raise

        # TODO: Implement looping logic
        # If validator recommends "GATHER_MORE", return to Phase 1
        # If validator recommends "REVISE", ask user for revisions

        logger.info("Pipeline completed successfully")
        return self.session

    def save_session(self, filepath: str):
        """Save session state to file

        Args:
            filepath: Path to save session JSON
        """
        if self.session is None:
            raise ValueError("No session to save")

        import json
        with open(filepath, "w") as f:
            json.dump(self.session.model_dump(), f, indent=2, default=str)
        logger.info(f"Session saved to {filepath}")

    def load_session(self, filepath: str) -> SessionState:
        """Load session state from file

        Args:
            filepath: Path to load session JSON

        Returns:
            Loaded SessionState
        """
        import json
        with open(filepath, "r") as f:
            data = json.load(f)
        self.session = SessionState(**data)
        logger.info(f"Session loaded from {filepath}")
        return self.session


def run(user_input: UserInput) -> SessionState:
    """Convenience function to run pipeline

    Args:
        user_input: Initial user input

    Returns:
        Final SessionState
    """
    pipeline = Pipeline()
    return pipeline.execute(user_input)
