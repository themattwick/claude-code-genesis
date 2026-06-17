"""Tests for Analyzer Agent"""

import json
import pytest
from unittest.mock import patch
from schemas import AnalyzerOutput, Contradiction, Gap
from agents import create_analyzer


def _fake_llm(contradictions=None, gaps=None, score=0.85, recommendation="COMPLETE"):
    """Build a fake LLM JSON response for the analyzer."""
    return json.dumps({
        "contradictions": contradictions or [],
        "gaps": gaps or [],
        "missing_details": [],
        "completeness_score": score,
        "recommendation": recommendation,
        "follow_up_questions": [],
    })


class TestAnalyzerAgent:

    def test_initialization(self):
        analyzer = create_analyzer()
        assert analyzer.name == "Analyzer Agent"

    def test_clean_output_no_issues(self, sample_gatherer_output):
        """When LLM finds nothing wrong, recommendation is COMPLETE."""
        analyzer = create_analyzer()
        fake = _fake_llm(recommendation="COMPLETE", score=0.9)

        with patch.object(analyzer.backend, "call", return_value=fake):
            output = analyzer.execute(sample_gatherer_output)

        assert isinstance(output, AnalyzerOutput)
        assert output.recommendation == "COMPLETE"
        assert output.completeness_score == 0.9
        assert output.contradictions_found == []
        assert output.gaps_found == []

    def test_contradictions_parsed(self, sample_gatherer_output):
        """Contradictions returned by LLM are parsed into Contradiction objects."""
        analyzer = create_analyzer()
        fake = _fake_llm(
            contradictions=[{
                "answer_ids": ["CO-01", "KTO-01"],
                "description": "Sprzeczność testowa",
                "severity": "high",
            }],
            recommendation="NEEDS_MORE_INFO",
            score=0.5,
        )

        with patch.object(analyzer.backend, "call", return_value=fake):
            output = analyzer.execute(sample_gatherer_output)

        assert len(output.contradictions_found) == 1
        c = output.contradictions_found[0]
        assert isinstance(c, Contradiction)
        assert c.severity == "high"
        assert "CO-01" in c.answer_ids

    def test_gaps_parsed(self, sample_gatherer_output):
        """Gaps returned by LLM are parsed into Gap objects."""
        analyzer = create_analyzer()
        fake = _fake_llm(
            gaps=[{
                "category": "ILE",
                "description": "Brak informacji o skalowalności",
                "suggested_question": "Ilu użytkowników jednocześnie?",
            }],
            recommendation="ASK_FOLLOW_UP",
            score=0.6,
        )

        with patch.object(analyzer.backend, "call", return_value=fake):
            output = analyzer.execute(sample_gatherer_output)

        assert len(output.gaps_found) == 1
        g = output.gaps_found[0]
        assert isinstance(g, Gap)
        assert g.category == "ILE"
        assert "skalowalności" in g.description

    def test_handles_markdown_codeblock(self, sample_gatherer_output):
        """LLM response wrapped in ```json ... ``` is handled correctly."""
        analyzer = create_analyzer()
        inner = _fake_llm(score=0.75, recommendation="COMPLETE")
        wrapped = f"```json\n{inner}\n```"

        with patch.object(analyzer.backend, "call", return_value=wrapped):
            output = analyzer.execute(sample_gatherer_output)

        assert output.completeness_score == 0.75

    def test_valid_recommendations(self, sample_gatherer_output):
        """All three valid recommendation values are accepted."""
        analyzer = create_analyzer()
        for rec in ["COMPLETE", "NEEDS_MORE_INFO", "ASK_FOLLOW_UP"]:
            fake = _fake_llm(recommendation=rec, score=0.7)
            with patch.object(analyzer.backend, "call", return_value=fake):
                output = analyzer.execute(sample_gatherer_output)
            assert output.recommendation == rec
