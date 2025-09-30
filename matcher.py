"""
Backward compatibility wrapper for matcher
Imports from core but maintains old interface
"""

from core.matcher import EnhancedWordMatcher as WordMatcher
from core.config import OptimizerConfig

__all__ = ['WordMatcher', 'OptimizerConfig']
