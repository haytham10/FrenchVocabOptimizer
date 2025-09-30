"""
Backward compatibility wrapper for optimizer
Imports from core but maintains old interface
"""

from core.optimizer import EnhancedSentenceOptimizer as SentenceOptimizer
from core.config import OptimizerConfig

__all__ = ['SentenceOptimizer', 'OptimizerConfig']
