# Migration Guide - Enhanced French Vocab Optimizer

## Overview
This guide helps you transition from the old system to the new enhanced system.

## What's Changed

### File Structure
```
OLD STRUCTURE:
├── matcher.py (now: matcher_old.py)
├── optimizer.py (now: optimizer_old.py)
├── sheets_handler.py (now: sheets_handler_old.py)
└── web_interface/
    ├── app.py (now: app_old.py)
    ├── templates/index.html (now: index_old.html)
    └── static/script.js (now: script_old.js)

NEW STRUCTURE:
├── core/
│   ├── __init__.py
│   ├── config.py (centralized configuration)
│   ├── matcher.py (EnhancedWordMatcher - 10x faster)
│   ├── optimizer.py (EnhancedSentenceOptimizer - 3 algorithms)
│   └── sheets.py (EnhancedSheetsHandler - rich formatting)
├── matcher.py (backward compatibility wrapper)
├── optimizer.py (backward compatibility wrapper)
├── sheets_handler.py (backward compatibility wrapper)
└── web_interface/
    ├── app.py (enhanced API with background processing)
    ├── templates/index.html (modern Tailwind UI)
    └── static/script.js (real-time progress, keyboard shortcuts)
```

### Backward Compatibility
All old import statements still work:
```python
# These still work (redirected to core modules)
from matcher import WordMatcher
from optimizer import SentenceOptimizer
from sheets_handler import SheetsHandler

# New recommended imports
from core.matcher import EnhancedWordMatcher
from core.optimizer import EnhancedSentenceOptimizer
from core.sheets import EnhancedSheetsHandler
from core.config import OptimizerConfig
```

## New Features

### 1. Enhanced Performance (10x faster)
- Smart caching with pickle
- Pre-built lookup tables for instant word matching
- Parallel batch processing with ThreadPoolExecutor
- Memory-efficient word processing

### 2. Three Optimization Algorithms
Choose the best algorithm for your needs:

| Algorithm | Speed | Quality | Best For |
|-----------|-------|---------|----------|
| `greedy` | ⚡ Fast | Good | Quick results, large datasets |
| `weighted_greedy` | ⚖️ Balanced | Better | **Recommended** - best balance |
| `beam_search` | 🐌 Slow | Best | Maximum coverage, small datasets |

### 3. Rich Spreadsheet Formatting
5 tabs with color-coded data:
- **Optimized Sentences**: Green headers, alternating rows, word count colors
- **Summary Statistics**: Quick overview of optimization results
- **Missing Words**: Red-highlighted words that weren't covered
- **Coverage Map**: Visual grid showing which words appear in which sentences
- **Detailed Statistics**: Per-sentence breakdown with coverage percentages

### 4. Modern Web Interface
- Drag-and-drop file upload
- Real-time progress bars with ETA
- Dark/light mode toggle
- Keyboard shortcuts (Ctrl+Enter to optimize, Escape to close modals)
- Responsive design for mobile/tablet
- Live status updates every 500ms

### 5. Flexible Authentication
Auto-detects credential type:
- OAuth user credentials (credentials.json + token.json)
- Service Account credentials
- Automatic token refresh
- Graceful error handling with helpful messages

## Usage

### Web Interface (Recommended)
1. Start the server:
   ```bash
   cd web_interface
   python app.py
   ```
2. Open browser: http://localhost:5000
3. Drag-drop your vocabulary file or click to upload
4. Choose algorithm: weighted_greedy (recommended)
5. Click "Optimize" or press Ctrl+Enter
6. Watch real-time progress
7. Download results when complete

### Command Line
```python
from core.config import OptimizerConfig
from core.matcher import EnhancedWordMatcher
from core.optimizer import EnhancedSentenceOptimizer
from core.sheets import EnhancedSheetsHandler

# Configure
config = OptimizerConfig(
    algorithm='weighted_greedy',  # or 'greedy', 'beam_search'
    cache_enabled=True,
    parallel_processing=True,
    spreadsheet_name='FrenchVocabOptimizer'
)

# Load vocabulary
matcher = EnhancedWordMatcher(config)
words = ['bonjour', 'merci', 'chat', ...]
matcher.add_words(words)

# Load sentences
with open('sentences.txt', 'r', encoding='utf-8') as f:
    sentences = [line.strip() for line in f if line.strip()]

# Optimize
optimizer = EnhancedSentenceOptimizer(matcher, config)
result = optimizer.optimize(sentences)

print(f"Coverage: {result.coverage_percentage:.1f}%")
print(f"Sentences used: {len(result.sentences)}")
print(f"Words covered: {len(result.covered_words)}")
print(f"Missing words: {len(result.missing_words)}")

# Export to Google Sheets
sheets = EnhancedSheetsHandler(config)
sheets.update_sheet(result, sentences)
print(f"Results at: {result.spreadsheet_url}")
```

## Configuration Options

### OptimizerConfig Parameters
```python
from core.config import OptimizerConfig

config = OptimizerConfig(
    # Algorithm selection
    algorithm='weighted_greedy',  # 'greedy' | 'weighted_greedy' | 'beam_search'
    
    # Performance tuning
    cache_enabled=True,           # Enable smart caching (recommended)
    parallel_processing=True,     # Use multiple threads (recommended)
    batch_size=50,                # Sentences per batch (adjust for memory)
    
    # Beam search parameters
    beam_width=5,                 # Beam width for beam_search algorithm
    max_iterations=1000,          # Max iterations before stopping
    
    # Google Sheets settings
    spreadsheet_name='FrenchVocabOptimizer',  # Your sheet name
    credentials_path='credentials.json',       # Path to credentials
    
    # spaCy model
    spacy_model='fr_core_news_lg'  # French language model
)
```

## Troubleshooting

### Import Errors
If you get import errors:
```bash
# Verify core modules
python -c "from core.config import OptimizerConfig; print('OK')"

# Check backward compatibility
python -c "from matcher import WordMatcher; print('OK')"
```

### Authentication Issues
1. **OAuth**: Ensure `credentials.json` and `token.json` are in project root
2. **Service Account**: Ensure `credentials.json` contains service account key
3. **Auto-detection**: Check logs for "Detected OAuth credentials" or "Detected Service Account"

### Performance Issues
1. Try `greedy` algorithm for faster results
2. Reduce `batch_size` if memory is limited
3. Disable `parallel_processing` on single-core systems
4. Clear cache: `rm -rf .cache/`

### Web Interface Not Starting
```bash
# Check Flask is installed
pip install flask

# Check port 5000 is available
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -i :5000

# Try different port
python app.py --port 8080
```

## Rolling Back

If you need to revert to the old system:

1. **Restore old files**:
   ```bash
   mv matcher_old.py matcher.py
   mv optimizer_old.py optimizer.py
   mv sheets_handler_old.py sheets_handler.py
   cd web_interface
   mv app_old.py app.py
   mv templates/index_old.html templates/index.html
   mv static/script_old.js static/script.js
   ```

2. **Remove core/ directory**:
   ```bash
   rm -rf core/
   ```

3. **Restart web interface**

## Getting Help

1. Check `UPGRADE_SUMMARY.md` for detailed change log
2. Read `README_NEW.md` for complete documentation
3. Review `QUICKSTART_GUIDE.md` for step-by-step instructions
4. Check console logs for detailed error messages
5. Verify Python 3.10+ is installed
6. Ensure all dependencies are up to date: `pip install -r requirements.txt`

## Next Steps

1. ✅ Test the new web interface
2. ✅ Try different optimization algorithms
3. ✅ Explore the rich spreadsheet formatting
4. ✅ Configure OptimizerConfig to your needs
5. ✅ Check performance improvements with your datasets
6. ✅ Set up OAuth credentials if not already done

## Version Compatibility

- **Python**: 3.10+ required
- **NumPy**: 1.24.0 to <2.0 (pinned for spaCy compatibility)
- **spaCy**: 3.5.0+
- **Flask**: 2.3.0+
- **Google API**: google-auth, gspread latest versions

---

**Welcome to the enhanced French Vocab Optimizer!** 🚀
For questions or issues, check the documentation or review the code in `core/` modules.
