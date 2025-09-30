# French Vocabulary Sentence Optimizer

An intelligent tool that analyzes sentences and finds the minimum number needed to cover 2000 common French words, accounting for gender variations, verb conjugations, and multi-word phrases.

## 🎯 Features

- **Smart Word Matching**: Handles gender variations (un|une), verb conjugations, and multi-word phrases
- **Greedy Optimization**: Finds the minimum sentence set to cover your word list
- **Google Sheets Integration**: Loads word lists and outputs results directly to Sheets
- **Progress Tracking**: Real-time progress updates during processing
- **Detailed Reports**: 4-tab output with sentences, summary, missing words, and coverage map
- **Dual Interface**: Web UI and command-line options

## 📋 Requirements

- Python 3.8 or higher
- Google API credentials (credentials.json)
- Internet connection for Google Sheets API

## 🚀 Quick Start

### 1. Setup (First Time Only)

Run the setup batch file:
```bash
setup.bat
```

This will:
- Install all Python dependencies
- Download the French spaCy model
- Create necessary folders

**Time**: ~5 minutes

### 2. Add Google Credentials

Place your `credentials.json` file in the project root folder. You can reuse the credentials from the French Novel Processor project.

### 3. Run the Application

**Option A: Web Interface (Recommended)**
```bash
run_application.bat
```
Then open your browser to: http://localhost:5000

**Option B: Command Line**
```bash
run_optimizer.bat --words "SHEET_URL" --sentences "sentences.csv" --max 600
```

## 📁 Project Structure

```
FrenchVocabOptimizer/
├── setup.bat                    # Dependency installer
├── run_application.bat          # Launch web interface
├── run_optimizer.bat           # Command-line launcher
├── optimizer.py                # Main optimization logic
├── matcher.py                  # Word matching engine
├── sheets_handler.py           # Google Sheets integration
├── requirements.txt            # Python dependencies
├── credentials.json            # Google API credentials (you provide)
├── web_interface/
│   ├── app.py                  # Flask web server
│   ├── templates/
│   │   └── index.html          # Web UI
│   └── static/
│       └── script.js           # Client-side JavaScript
├── uploads/                    # Temporary file storage
├── output/                     # CSV backup files
└── README.md                   # This file
```

## 🎮 Using the Web Interface

1. **Enter Google Sheets URL**: Paste the URL of your 2000-word list
2. **Upload Sentence File**: Drag & drop or browse for your CSV/TXT file
3. **Configure Settings**: 
   - Max Sentences Target (default: 600)
   - Matching Strictness (Normal recommended)
4. **Click "Start Optimization"**: Watch the progress in real-time
5. **View Results**: 
   - Click to open Google Sheets with results
   - Download CSV backups
   - Process another file

## 💻 Command-Line Usage

### Basic Usage
```bash
run_optimizer.bat --words "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID" --sentences sentences.csv
```

### With Options
```bash
run_optimizer.bat --words "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID" --sentences sentences.csv --max 600 --output results
```

### Parameters
- `--words`: Google Sheets URL or local CSV file with word list
- `--sentences`: CSV or TXT file containing sentences
- `--max`: Maximum sentences to select (default: 600)
- `--output`: Output folder for CSV files (default: output)

## 📊 Input Format

### Word List (Google Sheets or CSV)
Expected columns:
1. **French**: Word or phrase (may include `|` for variations)
2. **English**: Translation
3. **POS**: Part of speech (optional)

Examples:
- `un|une` - Gender variations
- `le monde` - Multi-word phrase
- `être` - Verb (will match all conjugations)

### Sentence File (CSV or TXT)
- CSV: One sentence per row
- TXT: One sentence per line
- Encoding: UTF-8

## 📈 Output Format

The tool creates a Google Sheet with 4 tabs:

### Tab 1: Optimized Sentences
- Row number
- Selected sentence
- Words covered by this sentence
- Number of new words covered

### Tab 2: Coverage Summary
- Total sentences selected
- Words covered (X/2000)
- Coverage percentage
- Efficiency score (words per sentence)
- Processing time

### Tab 3: Missing Words
- Words from your list not found in sentences
- Possible reasons for missing

### Tab 4: Full Coverage Map
- Each word from the 2000 list
- Whether it was found
- How many times it appears
- Which sentences contain it

## 🔧 How It Works

1. **Load Word List**: Reads 2000 words from Google Sheets
2. **Preprocess**: Identifies variations, phrases, and lemmas
3. **Analyze Sentences**: Uses spaCy to find all word matches
4. **Greedy Optimization**: Selects sentences that cover most uncovered words
5. **Generate Output**: Creates Google Sheet and CSV backups

### Matching Logic

- **Gender Variations**: `un|une` matches both forms
- **Verb Conjugations**: `être` matches `suis`, `es`, `est`, `sommes`, `êtes`, `sont`
- **Multi-word Phrases**: `le monde` matches exact phrase in order
- **Noun Forms**: Matches singular and plural
- **Lemmatization**: Uses spaCy for accurate matching

## ⚙️ Configuration

Edit these settings in the web interface or command line:

- **Max Sentences**: Target number of sentences (default: 600)
- **Strictness**: 
  - Exact: Only exact matches
  - Normal: Includes lemmatization (recommended)
  - Fuzzy: More lenient matching

## 🐛 Troubleshooting

### "Credentials file not found"
- Place `credentials.json` in the project root folder
- Ensure it's the same file from French Novel Processor

### "spaCy model not found"
- Run `setup.bat` again
- Or manually: `python -m spacy download fr_core_news_lg`

### "Failed to load word list"
- Check Google Sheets URL is correct
- Ensure sheet is shared with service account email
- Verify first row has headers

### Web interface won't start
- Check if port 5000 is already in use
- Try running: `pip install -r requirements.txt`

### Processing is slow
- Normal for large datasets (5000+ sentences)
- Expected time: 8-10 minutes for 5000 sentences
- Ensure you have 1GB+ RAM available

## 📝 Tips for Best Results

1. **Word List Quality**: Ensure your 2000 words are formatted correctly
2. **Sentence Quality**: More sentences = better coverage
3. **Preprocessing**: Remove duplicate sentences from input
4. **Target Settings**: Start with 600, adjust based on results
5. **Missing Words**: Check "Missing Words" tab to understand gaps

## 🎓 Example Workflow

```bash
# 1. Setup (first time)
setup.bat

# 2. Place credentials.json in folder

# 3. Run web interface
run_application.bat

# 4. In browser:
#    - Paste Google Sheets URL
#    - Upload sentences.csv
#    - Click "Start Optimization"

# 5. View results in Google Sheets
#    - Review optimized sentences
#    - Check coverage statistics
#    - Download CSV backups
```

## 📞 Support

- **Bug Reports**: Check the Missing Words tab for coverage issues
- **Setup Help**: Ensure all dependencies are installed via setup.bat
- **API Issues**: Verify credentials.json is correct

## ⏱️ Performance Benchmarks

- **5,000 sentences**: ~8-10 minutes
- **10,000 sentences**: ~15-20 minutes
- **Target Achievement**: Typically under 600 sentences for diverse content

## 🔒 Privacy & Security

- All processing happens locally on your machine
- Google Sheets API only accesses sheets you specify
- No data is sent to external servers
- Credentials remain on your computer

## 📄 License

This tool is provided as-is for the client's use as specified in the Development Requirements Plan.

## 🙏 Credits

Built with:
- spaCy (French NLP)
- Google Sheets API
- Flask (Web interface)
- Tailwind CSS (UI styling)

---

**Version**: 1.0  
**Developer**: Haytham Mokhtari  
**Client**: Stan Jones  