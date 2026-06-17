"""Zachman Framework definitions"""

from .questions import (
    ZACHMAN_QUESTIONS,
    get_questions_by_mode,
    get_questions_by_category,
    get_all_categories,
)

__all__ = [
    "ZACHMAN_QUESTIONS",
    "get_questions_by_mode",
    "get_questions_by_category",
    "get_all_categories",
]
