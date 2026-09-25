"""
Modulo UI de FileOrganizer.
"""

from .constants import THEME, FONT_FAMILY, human_size
from .general import build_general_tab
from .rules import build_rules_tab
from .history_view import build_history_tab

__all__ = [
    "THEME",
    "FONT_FAMILY",
    "human_size",
    "build_general_tab",
    "build_rules_tab",
    "build_history_tab",
]
