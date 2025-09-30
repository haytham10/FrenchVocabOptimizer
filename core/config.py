"""
Configuration and Constants
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class OptimizerConfig:
    """Configuration for the optimization process"""
    # Optimization algorithm
    algorithm: str = 'weighted_greedy'  # 'greedy' | 'weighted_greedy' | 'beam_search'
    
    # Performance settings
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    batch_size: int = 50  # For batch processing
    
    # Algorithm-specific parameters
    beam_width: int = 5  # For beam_search algorithm
    max_iterations: int = 1000  # Maximum iterations before stopping
    
    # Coverage targets
    max_sentences: int = 600
    min_coverage_percent: float = 95.0
    progress_interval: int = 10  # Report progress every N iterations
    
    # Matching strictness
    exact_match: bool = False
    lemma_matching: bool = True
    fuzzy_threshold: float = 0.85
    
    # SpaCy model
    spacy_model: str = 'fr_core_news_lg'
    
    # Google Sheets
    spreadsheet_name: str = 'FrenchVocabOptimizer'
    
    # Paths
    credentials_path: str = 'credentials.json'
    token_path: str = 'token.json'
    upload_folder: str = 'uploads'
    output_folder: str = 'output'
    cache_folder: str = '.cache'


# Google Sheets API scopes
SHEETS_SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Spreadsheet formatting colors
COLORS = {
    'header': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
    'summary_header': {'red': 0.2, 'green': 0.6, 'blue': 0.4},
    'missing_header': {'red': 0.9, 'green': 0.5, 'blue': 0.2},
    'coverage_header': {'red': 0.4, 'green': 0.2, 'blue': 0.8},
    'high_efficiency': {'red': 0.2, 'green': 0.8, 'blue': 0.3},
    'medium_efficiency': {'red': 1.0, 'green': 0.9, 'blue': 0.4},
    'low_efficiency': {'red': 1.0, 'green': 0.6, 'blue': 0.4}
}

# File upload limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'.csv', '.txt', '.tsv'}
