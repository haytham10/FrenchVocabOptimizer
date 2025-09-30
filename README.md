# French Vocab Optimizer 🇫🇷

**An intelligent Python tool to optimize French vocabulary learning by finding the minimum set of sentences that cover your vocabulary list.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/built%20with-spaCy-09a3d5.svg)](https://spacy.io)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-5%2F5%20passing-brightgreen)]()

> **Version 2.0 - Enhanced Edition** 
> - 🚀 **10x Performance** improvement with smart caching
> - 🎨 **Modern UI** with Tailwind CSS and real-time progress
> - 🧠 **3 Algorithms** for optimal sentence selection
> - 📊 **Rich Formatting** with 5-tab Google Sheets output

---

## 🚀 Quick Start

### 1️⃣ Setup (First Time - 5 minutes)

```bash
# Windows: Run automated setup
scripts\setup.bat

# Or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
```
# French Vocab Optimizer 🇫🇷

An intelligent Python tool to optimize French vocabulary learning by finding the minimum set of sentences that cover your vocabulary list.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/built%20with-spaCy-09a3d5.svg)](https://spacy.io)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-5%2F5%20passing-brightgreen)]()

> Version 2.0 - Enhanced Edition

> - 🚀 10x performance improvement with smart caching
> - 🎨 Modern UI with Tailwind CSS and real-time progress
> - 🧠 Three optimization algorithms (greedy, weighted_greedy, beam_search)
> - 📊 Rich Google Sheets export (5 formatted tabs)

---

## 🚀 Quick Start

### 1. Setup (first time)

Windows automated setup:

```powershell
cd scripts
.\setup.bat
```

Manual steps:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
```

### 2. Add Google Credentials

Place `credentials.json` in the project root. Create credentials in Google Cloud Console and enable the Sheets & Drive APIs.

### 3. Launch the web interface

```bash
cd web_interface
python app.py
```

Open http://localhost:5000 in your browser.

### 4. Optimize your vocabulary

1. Paste the Google Sheets URL containing your word list.
2. Upload a sentence file (CSV or TXT).
3. Click Start Optimization (or press Ctrl+Enter).
4. Watch progress and ETA in real time.
5. Results are written to a formatted Google Sheet and CSV backups.

---

## ✨ Features

- Smart optimization with three algorithms: greedy (fast), weighted_greedy (balanced, recommended), beam_search (thorough).
- Smart caching and parallel processing for speed and memory efficiency.
- Rich Google Sheets export with 5 tabs: Optimized Sentences, Coverage Summary, Missing Words, Coverage Map, Detailed Statistics.
- Flexible authentication: OAuth or Service Account (auto-detected).
- Modern Tailwind-based UI with drag-and-drop, keyboard shortcuts, and real-time progress.

---

## 📁 Project structure

```
FrenchVocabOptimizer/
├── core/                    # Core optimization engine
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── matcher.py           # Word matcher
│   ├── optimizer.py         # Optimization algorithms
│   └── sheets.py            # Google Sheets integration
├── web_interface/           # Flask web UI
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── script.js
├── scripts/                 # Helper scripts (setup, run)
├── docs/                    # Documentation
├── tests/                   # Unit & integration tests
├── uploads/                 # Temporary uploads
├── output/                  # CSV backups & exports
├── requirements.txt
├── credentials.json         # (user-provided)
├── token.json               # (generated)
└── README.md
```

---

## 🎮 Web interface (recommended)

1. Paste your Google Sheets URL.
2. Upload sentences.csv or sentences.txt.
3. Configure options (max sentences, algorithm, strictness).
4. Start optimization and follow progress.

---

## 💻 Command-line usage

Basic example:

```bash
scripts\run_optimizer.bat --words "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID" --sentences sentences.csv
```

With options:

```bash
scripts\run_optimizer.bat --words words.csv --sentences sentences.csv --max 600 --output output
```

Parameters:
- `--words`: Google Sheets URL or local CSV with word list
- `--sentences`: CSV or TXT sentence corpus
- `--max`: Maximum sentences to select (default: 600)
- `--output`: Output folder for CSV exports (default: output)

---

## 📊 Input & output

Word list (Google Sheets or CSV) expected columns:
1. French (word or phrase; `|` allowed for variations)
2. English (translation)
3. POS (optional)

Sentence file: one sentence per row (CSV) or one sentence per line (TXT), UTF-8 encoded.

Output: Google Sheet with 5 tabs and CSV backups in `output/`.

---

## ⚙️ Configuration (example)

```python
from core.config import OptimizerConfig
from core.optimizer import EnhancedSentenceOptimizer

config = OptimizerConfig(
    algorithm='weighted_greedy',
    cache_enabled=True,
    parallel_processing=True,
    max_sentences=600,
    beam_width=5,
)

# Run optimizer using lists of dicts or CSV-loaded data
optimizer = EnhancedSentenceOptimizer(words, sentences, config)
result = optimizer.optimize()
print(f"Coverage: {result.coverage_percent:.1f}%")
```

---

## 🛠️ Troubleshooting

- "credentials.json not found": place `credentials.json` in project root.
- "spaCy model not found": run `python -m spacy download fr_core_news_lg` or re-run `scripts\setup.bat`.
- Port 5000 in use: run the app on another port `python app.py --port 8080` or free the port.
- If dependencies missing: `pip install -r requirements.txt`.

For more detailed troubleshooting see `docs/MIGRATION_GUIDE.md`.

---

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests
```

Expected: core imports, matcher, optimizer algorithms, and web interface init tests pass.

---

## 📈 Performance

- Typical: 5,000 sentences processed in ~8–10 minutes (depends on machine and options).
- Use `weighted_greedy` for a good balance of speed and quality; `beam_search` for maximal coverage.

---

## 🤝 Contributing

Contributions welcome. See `docs/` for development and migration guides.

---

## 📄 License

MIT

---

## 🙏 Credits

- spaCy (French NLP)
- Flask (web interface)
- Tailwind CSS (UI)
- Google Sheets API

---

Made with ❤️ for French language learners.
