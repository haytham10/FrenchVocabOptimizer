"""
Enhanced Flask Web Interface - Modern UI with real-time progress
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
import csv
import threading
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import OptimizerConfig, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from core.optimizer import EnhancedSentenceOptimizer
from core.sheets import EnhancedSheetsHandler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create folders
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Global progress tracking
current_progress = {
    'stage': '',
    'current': 0,
    'total': 0,
    'words_covered': 0,
    'sentences_selected': 0,
    'complete': False,
    'error': None,
    'results': None
}

def progress_callback(progress_data):
    """Update global progress"""
    global current_progress
    current_progress.update(progress_data)


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Run optimization process"""
    global current_progress
    
    try:
        # Reset progress
        current_progress = {
            'stage': 'Starting...',
            'current': 0,
            'total': 0,
            'words_covered': 0,
            'sentences_selected': 0,
            'complete': False,
            'error': None,
            'results': None
        }
        
        # Get parameters
        word_list_url = request.form.get('word_list_url')
        max_sentences = int(request.form.get('max_sentences', 600))
        algorithm = request.form.get('algorithm', 'weighted_greedy')
        strictness = request.form.get('strictness', 'normal')
        
        # Get uploaded file
        if 'sentence_file' not in request.files:
            return jsonify({'error': 'No sentence file uploaded'}), 400
        
        file = request.files['sentence_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # Run optimization in background
        def run_optimization():
            global current_progress
            
            try:
                # Configure
                config = OptimizerConfig(
                    max_sentences=max_sentences,
                    parallel_processing=True,
                    enable_caching=True,
                    lemma_matching=(strictness != 'exact'),
                    exact_match=(strictness == 'exact')
                )
                
                # Load word list
                current_progress['stage'] = 'Loading word list...'
                sheets_handler = EnhancedSheetsHandler(config)
                word_list = sheets_handler.load_word_list(word_list_url)
                
                # Load sentences
                current_progress['stage'] = 'Loading sentences...'
                sentences = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    if filename.endswith('.csv') or filename.endswith('.tsv'):
                        delimiter = '\t' if filename.endswith('.tsv') else ','
                        reader = csv.reader(f, delimiter=delimiter)
                        for row in reader:
                            if row and row[0].strip():
                                sentences.append(row[0].strip())
                    else:
                        sentences = [line.strip() for line in f if line.strip()]
                
                current_progress['stage'] = f'Loaded {len(sentences)} sentences'
                
                # Run optimization
                optimizer = EnhancedSentenceOptimizer(
                    word_list,
                    sentences,
                    config,
                    callback=progress_callback
                )
                
                results = optimizer.optimize(algorithm=algorithm)
                
                # Create output sheet
                current_progress['stage'] = 'Creating Google Sheets...'
                sheet_url = sheets_handler.create_output_sheet(results, word_list)
                
                # Save CSV backup
                current_progress['stage'] = 'Saving CSV backup...'
                sheets_handler.save_csv_backup(results)
                
                # Store results
                current_progress['results'] = {
                    'total_sentences': results.total_sentences,
                    'words_covered': results.words_covered,
                    'total_words': results.total_words,
                    'coverage_percent': results.coverage_percent,
                    'efficiency': results.efficiency,
                    'missing_words': results.missing_words,
                    'processing_time': results.processing_time,
                    'algorithm_used': results.algorithm_used,
                    'sheet_url': sheet_url
                }
                current_progress['complete'] = True
                current_progress['stage'] = 'Complete!'
                
            except Exception as e:
                current_progress['error'] = str(e)
                current_progress['complete'] = True
                print(f"Error in optimization: {str(e)}")
                traceback.print_exc()
        
        # Start thread
        thread = threading.Thread(target=run_optimization, daemon=True)
        thread.start()
        
        return jsonify({'status': 'started', 'message': 'Optimization started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress')
def get_progress():
    """Get current progress"""
    return jsonify(current_progress)


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download CSV backup"""
    try:
        filepath = os.path.join('output', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/list-outputs')
def list_outputs():
    """List available output files"""
    try:
        output_dir = 'output'
        if not os.path.exists(output_dir):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(output_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': files[:20]})  # Last 20 files
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'French Vocabulary Optimizer API v2.0',
        'features': [
            'Enhanced word matching',
            'Multiple algorithms',
            'Rich spreadsheet formatting',
            'Real-time progress',
            'Auto-detect authentication'
        ]
    })


if __name__ == '__main__':
    print("=" * 70)
    print("French Vocabulary Sentence Optimizer v2.0")
    print("=" * 70)
    print("\n✓ Server starting...")
    print("✓ Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
