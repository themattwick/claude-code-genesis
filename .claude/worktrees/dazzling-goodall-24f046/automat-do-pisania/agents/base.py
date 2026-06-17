"""Base classes for agents"""

from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, model: str = None):
        """Initialize agent

        Args:
            name: Agent name
            model: LLM model to use
        """
        self.name = name
        self.model = model
        self.created_at = datetime.now()

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute agent with input data

        Args:
            input_data: Input for the agent

        Returns:
            Agent output
        """
        pass

    def log_execution(self, input_summary: str, output_summary: str):
        """Log agent execution"""
        logger.info(f"[{self.name}] Executed")
        logger.debug(f"  Input: {input_summary}")
        logger.debug(f"  Output: {output_summary}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


class GathererAgent(BaseAgent):
    """Base for Gatherer Agent - collects information from user"""

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Collect information from user

        Returns:
            GathererOutput with answers to questions
        """
        pass


class AnalyzerAgent(BaseAgent):
    """Base for Analyzer Agent - analyzes answers for gaps and contradictions"""

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Analyze answers

        Returns:
            AnalyzerOutput with gaps, contradictions, and recommendations
        """
        pass


class SpecWriterAgent(BaseAgent):
    """Base for Spec Writer Agent - writes specifications"""

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Write specification

        Returns:
            SpecOutput with markdown, JSON, and diagrams
        """
        pass


class ValidatorAgent(BaseAgent):
    """Base for Validator Agent - validates specification quality"""

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Validate specification

        Returns:
            ValidatorOutput with issues and recommendation
        """
        pass
