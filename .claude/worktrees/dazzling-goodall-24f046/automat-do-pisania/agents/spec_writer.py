"""Spec Writer Agent - writes specification from answers"""

import logging
from schemas import SpecOutput, GathererOutput, AnalyzerOutput, ZachmanModel
from .base import SpecWriterAgent
from . import backends

logger = logging.getLogger(__name__)


class SpecWriterAgentImpl(SpecWriterAgent):
    """Implementation of Spec Writer Agent

    Generates specification from answers in 3 formats:
    1. Markdown (human-readable)
    2. JSON Contract (machine-readable)
    3. Diagrams and Tables
    """

    def __init__(self, model: str = None):
        super().__init__(name="Spec Writer Agent", model=model)
        self.backend = backends.get_backend()

    def execute(
        self,
        gatherer_output: GathererOutput,
        analyzer_output: AnalyzerOutput = None,
    ) -> SpecOutput:
        """Write specification from answers

        Args:
            gatherer_output: Collected answers
            analyzer_output: Analysis results (optional)

        Returns:
            SpecOutput with markdown, JSON, and diagrams
        """
        logger.info("Spec Writer Agent starting")

        # TODO: Implement spec writing logic
        # This would:
        # 1. Map answers to Zachman categories
        # 2. Generate Markdown spec
        # 3. Generate JSON contract (ZachmanModel)
        # 4. Generate tables and diagrams

        zachman_model = ZachmanModel(
            system_name=gatherer_output.system_name,
            system_description=gatherer_output.system_description,
            mode=gatherer_output.mode,
        )

        output = SpecOutput(
            title=f"Specyfikacja: {gatherer_output.system_name}",
            markdown_spec="# TODO: Generate markdown spec",
            json_contract=zachman_model,
            tables_and_diagrams="# TODO: Generate diagrams",
        )

        self.log_execution(
            input_summary=f"System: {gatherer_output.system_name}",
            output_summary="Generated spec in 3 formats",
        )

        return output


def create_spec_writer(model: str = None) -> SpecWriterAgent:
    """Factory function to create Spec Writer Agent"""
    return SpecWriterAgentImpl(model=model)
