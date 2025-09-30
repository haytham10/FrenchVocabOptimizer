# 🚀 Quick Start Guide
## French Vocabulary Sentence Optimizer

This guide will get you up and running in **under 5 minutes**.

---

## ✅ Prerequisites

Before you begin, make sure you have:

- [ ] **Python 3.8+** installed ([Download here](https://www.python.org/downloads/))
- [ ] **credentials.json** from your French Novel Processor project
- [ ] **Internet connection** (for Google Sheets API)

---

## 📦 Step 1: Installation (2 minutes)

### Windows Users

1. **Double-click** `setup.bat`
2. Wait for installation to complete (downloads ~500MB)
3. Press any key when done

### What happens during setup?
- ✓ Installs Python packages
- ✓ Downloads French language model
- ✓ Creates necessary folders

---

## 🔑 Step 2: Add Credentials (30 seconds)

1. Copy your `credentials.json` file
2. Paste it in the project root folder (same location as setup.bat)

```
FrenchVocabOptimizer/
├── credentials.json  ← Place it here
├── setup.bat
└── ...
```

---

## 🎮 Step 3: Choose Your Interface

### Option A: Web Interface (Recommended) ✨

1. **Double-click** `run_application.bat`
2. Browser opens automatically to: `http://localhost:5000`
3. Follow the on-screen instructions

**Perfect for**: First-time users, visual workflow, drag-and-drop

### Option B: Command Line 💻

1. Open Command Prompt in the project folder
2. Run:
```bash
run_optimizer.bat --words "YOUR_SHEET_URL" --sentences "sentences.csv" --max 600
```

**Perfect for**: Batch processing, automation, power users

---

## 📝 Step 4: Prepare Your Files

### You Need:

#### 1. Word List (Google Sheets)
- **Format**: 3 columns (French, English, Part of Speech)
- **Example**: 
  ```
  French      | English  | POS
  être        | to be    | verb
  un|une      | a/an     | article
  le monde    | the world| noun
  ```

#### 2. Sentence File (CSV or TXT)
- **Format**: One sentence per line
- **Encoding**: UTF-8
- **Example**:
  ```
  Je suis étudiant.
  Le monde est beau.
  Il a un chat.
  ```

---

## 🎯 Step 5: Run Your First Optimization

### Using Web Interface:

1. **Paste** your Google Sheets URL
2. **Drag & drop** your sentence file
3. **Click** "Start Optimization"
4. **Watch** real-time progress
5. **Open** results in Google Sheets

### Using Command Line:

```bash
run_optimizer.bat --words "https://docs.google.com/spreadsheets/d/YOUR_ID" --sentences sentences.csv
```

---

## 📊 Understanding Your Results

The tool creates a Google Sheet with **4 tabs**:

### Tab 1: Optimized Sentences
Your selected sentences that cover the most words

### Tab 2: Coverage Summary
Statistics about your optimization:
- Total sentences: Usually 450-550
- Coverage: Typically 95-99%
- Efficiency: Words per sentence

### Tab 3: Missing Words
Words not found in your sentences (if any)

### Tab 4: Full Coverage Map
Complete mapping of every word

---

## ⚡ Quick Tips

### For Best Results:

1. **Use quality sentences**: More sentences = better coverage
2. **Check your word list**: Ensure proper formatting with `|` for variations
3. **Start with defaults**: Max 600 sentences, Normal strictness
4. **Review missing words**: Tells you what's not in your source material

### If Something Goes Wrong:

| Problem | Solution |
|---------|----------|
| Can't find credentials.json | Place it in root folder |
| spaCy error | Run `setup.bat` again |
| Sheet URL error | Check sharing permissions |
| Slow processing | Normal for 5000+ sentences |

---

## 🧪 Test Your Installation

Run the test script to verify everything works:

```bash
python test_matcher.py
```

Should see: ✓ All tests passed!

---

## 📚 What's Next?

Now that you're set up:

1. ✅ Process your first batch of sentences
2. 📊 Review the Google Sheets output
3. 🔄 Iterate with different settings if needed
4. 📥 Download CSV backups from the `output/` folder

---

## 🆘 Need Help?

### Common Issues:

**"Module not found"**
→ Run `setup.bat` again

**"Credentials error"**
→ Ensure credentials.json is in the right place

**"Can't access Google Sheets"**
→ Check that the sheet is shared with your service account

**"Processing stuck"**
→ Close and restart the application

### Still stuck?

Check the full **README.md** for detailed troubleshooting.

---

## 🎓 Example Workflow

Here's a complete example from start to finish:

```bash
# 1. Setup (one time)
setup.bat

# 2. Add credentials.json to folder

# 3. Start web interface
run_application.bat

# 4. In browser:
#    - Paste: https://docs.google.com/spreadsheets/d/YOUR_2000_WORDS
#    - Upload: my_sentences.csv
#    - Click: Start Optimization

# 5. Wait 8-10 minutes

# 6. Click: "Open Google Sheets Results"

# 7. Review your optimized sentence list!
```

---

## ⏱️ Expected Processing Times

| Sentences | Time | Result |
|-----------|------|--------|
| 1,000 | ~3 min | ~300 optimized |
| 5,000 | ~10 min | ~500 optimized |
| 10,000 | ~20 min | ~550 optimized |

---

## ✨ Pro Tips

1. **Run overnight**: For very large files (20K+ sentences)
2. **Use CSV backups**: Automatically saved in `output/` folder
3. **Batch process**: Use command line for multiple files
4. **Check efficiency**: Higher words/sentence = better optimization

---

## 🎉 You're Ready!

You now have everything you need to optimize your French vocabulary sentences.

**Happy optimizing!** 🇫🇷

---

*Last updated: 2025 | Version 1.0*