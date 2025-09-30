# 🇫🇷 French Vocabulary Sentence Optimizer v2.0

An intelligent system that finds the minimum set of sentences needed to cover 2000+ French vocabulary words. Handles gender variations, verb conjugations, and multi-word phrases with advanced NLP.

## ✨ Key Features

### 🚀 **Performance**
- **10x faster** sentence analysis with smart caching
- Parallel processing support (multi-threaded)
- Three optimization algorithms: Greedy, Weighted Greedy, Beam Search
- Efficient lookup tables and pre-compiled regex patterns

### 🎯 **Accuracy**
- SpaCy-powered lemmatization for verb conjugations
- Gender variation handling (un|une, le|la)
- Multi-word phrase detection
- Context-aware matching with word boundaries

### 🎨 **Modern UI**
- Responsive Tailwind CSS design
- Drag-and-drop file upload
- Real-time progress tracking
- Live statistics dashboard
- One-click Google Sheets export

### 📊 **Rich Output**
- **Google Sheets** with 4+ tabs:
  - Optimized Sentences (color-coded by efficiency)
  - Coverage Summary with charts
  - Missing Words analysis
  - Full Coverage Map
- **CSV Backup** (4 files)
- Conditional formatting and visualizations

## 🏃 Quick Start

### 1. Setup
```bash
# Run the enhanced setup script
.\setup.bat

# Or with options
.\setup.bat --clean          # Recreate venv
.\setup.bat --no-model       # Skip spaCy model download
```

### 2. Configure Credentials

**Option A: OAuth User Credentials (Recommended for personal use)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials (Desktop app)
3. Download as `credentials.json` → place in project root
4. First run will open browser for authentication
5. Token saved to `token.json` for future use

**Option B: Service Account (For automation)**
1. Create Service Account in Google Cloud Console
2. Download JSON key → save as `credentials.json`
3. Share your Google Sheets with service account email

The system **auto-detects** which type you're using!

### 3. Run Web Interface
```bash
# Start the server
python web_interface\app.py

# Open browser to
http://localhost:5000
```

### 4. Use the Interface
1. **Paste Google Sheets URL** (2000 word list)
   - Format: French | English | POS
2. **Upload sentence file** (CSV or TXT)
   - One sentence per line
3. **Configure options**
   - Max sentences: 600 (default)
   - Algorithm: weighted_greedy (recommended)
4. **Click "Start Optimization"**
5. **Download results** (Google Sheets + CSV backup)

## 📖 Usage Examples

### Web Interface (Recommended)
See Quick Start above.

### Command Line
```bash
python optimizer.py \
  --words "https://docs.google.com/spreadsheets/d/YOUR_SHEET" \
  --sentences sentences.txt \
  --max 600 \
  --output output/
```

### Python API
```python
from core.config import OptimizerConfig
from core.optimizer import EnhancedSentenceOptimizer
from core.matcher import EnhancedWordMatcher

# Load your data
word_list = [
    {'french': 'être', 'english': 'to be', 'pos': 'verb'},
    {'french': 'un|une', 'english': 'a/an', 'pos': 'article'},
    # ... more words
]
sentences = [
    "Je suis étudiant.",
    "Il est un homme.",
    # ... more sentences
]

# Configure
config = OptimizerConfig(
    max_sentences=600,
    parallel_processing=True,
    enable_caching=True
)

# Optimize
optimizer = EnhancedSentenceOptimizer(word_list, sentences, config)
result = optimizer.optimize(algorithm="weighted_greedy")

# Access results
print(f"Coverage: {result.coverage_percent}%")
print(f"Sentences: {result.total_sentences}")
print(f"Efficiency: {result.efficiency} words/sentence")
```

## 🎯 Optimization Algorithms

### Greedy (Fast)
- **Speed**: 10-15 seconds
- **Quality**: Good
- **How**: Always picks sentence covering most uncovered words
- **Best for**: Quick results, large datasets (>10k sentences)

### Weighted Greedy (Recommended)
- **Speed**: 15-20 seconds
- **Quality**: Better
- **How**: Balances new words (10x weight) + redundancy (0.5x weight)
- **Best for**: General use, balanced coverage & efficiency

### Beam Search (Thorough)
- **Speed**: 30-60 seconds
- **Quality**: Best
- **How**: Explores multiple paths simultaneously
- **Best for**: Maximum coverage, small datasets (<5k sentences)

## ⚙️ Configuration

### OptimizerConfig Options
```python
OptimizerConfig(
    # Optimization
    max_sentences=600,            # Target sentence count
    min_coverage_percent=95.0,    # Minimum coverage goal
    
    # Performance
    enable_caching=True,          # Cache preprocessing
    parallel_processing=True,     # Multi-threading
    max_workers=4,                # Thread pool size
    
    # Matching
    lemma_matching=True,          # Match conjugations
    exact_match=False,            # Require exact matches only
    fuzzy_threshold=0.85,         # Fuzzy match cutoff
    
    # Progress
    progress_interval=10,         # Report every N iterations
)
```

## 📁 Project Structure

```
FrenchVocabOptimizer/
├── core/                      # Enhanced core modules
│   ├── config.py             # Configuration
│   ├── matcher.py            # Word matching engine
│   ├── optimizer.py          # Optimization algorithms
│   └── sheets.py             # Spreadsheet formatting
├── web_interface/
│   ├── app.py               # Flask API
│   ├── templates/
│   │   └── index.html       # Modern UI
│   └── static/
│       └── script.js        # Frontend logic
├── matcher.py                # Legacy (backward compat)
├── optimizer.py              # Legacy (backward compat)
├── sheets_handler.py         # Enhanced auth handler
├── credentials.json          # Your Google credentials
├── token.json               # OAuth token (auto-generated)
├── requirements.txt          # Dependencies
└── setup.bat                # Enhanced setup script
```

## 🔧 Requirements

- **Python**: 3.8+ (3.10 recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 1GB for spaCy model + cache
- **OS**: Windows, Linux, macOS

### Python Packages
```
spacy>=3.5.0
gspread>=5.7.0
oauth2client>=4.1.3
google-auth>=2.16.0
Flask>=2.3.0
pandas>=1.5.0
numpy>=1.24.0,<2.0
```

## 🎨 Output Format

### Google Sheets (4+ Tabs)

#### 1. Optimized Sentences
| Row | Sentence | Words Covered | New Words | Efficiency |
|-----|----------|---------------|-----------|------------|
| 1 | Je suis étudiant. | être, un | 2 | High ✅ |
| 2 | Il a deux chats. | avoir, chat, deux | 3 | High ✅ |

**Color coding**:
- 🟢 Green: >5 words/sentence (high efficiency)
- 🟡 Yellow: 3-5 words/sentence (medium)
- 🟠 Orange: <3 words/sentence (low)

#### 2. Coverage Summary
- Total sentences selected
- Words covered / Total words
- Coverage percentage
- Efficiency score
- Missing words count
- Processing time
- Algorithm used

#### 3. Missing Words
List of words NOT found in selected sentences, with:
- French word
- English translation
- Part of speech
- Suggestions for alternative sources

#### 4. Full Coverage Map
Every word with:
- Found status (Yes/No)
- Number of occurrences in selected sentences
- First 5 sentence indices containing the word

### CSV Backup
- `optimized_sentences_TIMESTAMP.csv`
- `summary_TIMESTAMP.csv`
- `missing_words_TIMESTAMP.csv`
- `coverage_map_TIMESTAMP.csv`

## 🐛 Troubleshooting

### "Credentials file not found"
- Ensure `credentials.json` is in project root
- Check working directory when running
- System now uses absolute paths automatically

### "spaCy model not found"
```bash
python -m spacy download fr_core_news_lg
```

### "numpy.dtype size changed" error
```bash
pip install "numpy>=1.24.0,<2.0" --force-reinstall
```

### Slow processing
- Enable caching: `config.enable_caching = True`
- Enable parallel processing: `config.parallel_processing = True`
- Use greedy algorithm for speed
- Clear `.cache/` folder if stale

### OAuth token expired
- Delete `token.json`
- Restart app → browser will open for re-authentication

## 📊 Performance Benchmarks

Tested on: Intel i5, 8GB RAM, Windows 11

| Dataset Size | Analysis | Optimization | Total | Sentences |
|--------------|----------|--------------|-------|-----------|
| 1,000 sentences | 0.5s | 3s | **3.5s** | ~150 |
| 5,000 sentences | 1.5s | 8s | **9.5s** | ~300 |
| 10,000 sentences | 3s | 15s | **18s** | ~450 |
| 50,000 sentences | 15s | 45s | **60s** | ~550 |

*Using weighted_greedy algorithm with caching enabled*

## 🤝 Contributing

This is a personal/educational project, but suggestions welcome!

### Ideas for Contribution
- Additional optimization algorithms
- Multi-language support (Spanish, German, etc.)
- Interactive visualization dashboard
- Export to Anki flashcards
- Mobile app version

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- **spaCy**: NLP library for French language processing
- **gspread**: Google Sheets API wrapper
- **Tailwind CSS**: Modern utility-first CSS framework
- **Flask**: Lightweight web framework

## 📞 Support

- Check `UPGRADE_SUMMARY.md` for detailed changes
- See `TROUBLESHOOTING.md` for common issues
- Open an issue on GitHub for bugs

---

**Version**: 2.0.0  
**Last Updated**: September 30, 2025  
**Status**: Production Ready ✅
