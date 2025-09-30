"""
Backward compatibility wrapper for sheets_handler
Imports from core.sheets but maintains old interface
"""

from core.sheets import EnhancedSheetsHandler as SheetsHandler

# For backward compatibility
__all__ = ['SheetsHandler']
