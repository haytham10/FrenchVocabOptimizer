"""
Flask Web Interface for French Vocabulary Sentence Optimizer
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
import csv
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer import SentenceOptimizer
from sheets_handler import SheetsHandler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable for progress tracking
current_progress = {
    'stage': '',
    'current': 0,
    'total': 0,
    'words_covered': 0,
    'sentences_selected': 0
}

def progress_callback(progress_data):
    """Callback function for optimization progress"""
    global current_progress
    current_progress = progress_data


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Run optimization process"""
    try:
        # Get parameters
        word_list_url = request.form.get('word_list_url')
        max_sentences = int(request.form.get('max_sentences', 600))
        strictness = request.form.get('strictness', 'normal')
        
        # Get uploaded file
        if 'sentence_file' not in request.files:
            return jsonify({'error': 'No sentence file uploaded'}), 400
        
        file = request.files['sentence_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run optimization in background thread
        def run_optimization():
            global current_progress
            
            try:
                # Load word list
                sheets_handler = SheetsHandler()
                word_list = sheets_handler.load_word_list(word_list_url)
                
                # Load sentences
                sentences = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    if filename.endswith('.csv'):
                        reader = csv.reader(f)
                        for row in reader:
                            if row:
                                sentences.append(row[0])
                    else:
                        sentences = [line.strip() for line in f if line.strip()]
                
                # Run optimization
                optimizer = SentenceOptimizer(
                    word_list, 
                    sentences, 
                    max_sentences,
                    callback=progress_callback
                )
                results = optimizer.optimize()
                
                # Save to Google Sheets
                sheet_url = sheets_handler.create_output_sheet(results, word_list)
                results['sheet_url'] = sheet_url
                
                # Save CSV backup
                sheets_handler.save_csv_backup(results, 'output')
                
                # Store results globally
                current_progress['results'] = results
                current_progress['complete'] = True
                
            except Exception as e:
                current_progress['error'] = str(e)
                current_progress['complete'] = True
        
        # Start background thread
        thread = threading.Thread(target=run_optimization)
        thread.start()
        
        return jsonify({'status': 'started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress')
def get_progress():
    """Get current optimization progress"""
    global current_progress
    return jsonify(current_progress)


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download CSV backup file"""
    try:
        filepath = os.path.join('output', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test')
def test():
    """Test endpoint to verify server is running"""
    return jsonify({
        'status': 'ok',
        'message': 'French Vocabulary Optimizer API is running'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("French Vocabulary Sentence Optimizer - Web Interface")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)