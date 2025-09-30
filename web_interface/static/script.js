// Enhanced French Vocabulary Optimizer - Client-side v2.0

let selectedFile = null;
let progressInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDropZone();
    initializeForm();
    testAPIConnection();
});

function initializeDropZone() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('sentenceFile');

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('border-indigo-500', 'bg-indigo-50');
        dropZone.classList.remove('border-gray-300');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
        dropZone.classList.add('border-gray-300');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
        dropZone.classList.add('border-gray-300');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function initializeForm() {
    const form = document.getElementById('optimizerForm');
    form.addEventListener('submit', handleFormSubmit);
}

function handleFileSelect(file) {
    const validExtensions = ['.csv', '.txt', '.tsv'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (validExtensions.includes(fileExt)) {
        selectedFile = file;
        const dropZoneText = document.getElementById('dropZoneText');
        dropZoneText.innerHTML = `
            <span class="text-green-600 font-bold">✓ ${file.name}</span>
            <span class="text-gray-500 text-sm ml-2">(${formatFileSize(file.size)})</span>
        `;
        dropZoneText.classList.add('text-green-600');
    } else {
        showError('Please select a CSV, TXT, or TSV file');
        document.getElementById('sentenceFile').value = '';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const wordListUrl = document.getElementById('wordListUrl').value;
    const maxSentences = document.getElementById('maxSentences').value;
    const strictness = document.getElementById('strictness').value;
    const algorithm = document.getElementById('algorithm').value;

    if (!selectedFile) {
        showError('Please select a sentence file');
        return;
    }

    // Validate URL
    if (!wordListUrl.includes('docs.google.com/spreadsheets')) {
        showError('Please enter a valid Google Sheets URL');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('word_list_url', wordListUrl);
    formData.append('max_sentences', maxSentences);
    formData.append('strictness', strictness);
    formData.append('algorithm', algorithm);
    formData.append('sentence_file', selectedFile);

    // Hide input form, show progress
    document.getElementById('inputForm').classList.add('hidden');
    document.getElementById('progressDisplay').classList.remove('hidden');
    document.getElementById('targetSentences').textContent = maxSentences;

    try {
        // Start optimization
        const response = await fetch('/api/optimize', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start optimization');
        }

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        showError('Error: ' + error.message);
        resetForm();
    }
}

function startProgressPolling() {
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/progress');
            const progress = await response.json();

            updateProgressDisplay(progress);

            // Check if complete
            if (progress.complete) {
                clearInterval(progressInterval);
                if (progress.error) {
                    showError('Error: ' + progress.error);
                    resetForm();
                } else if (progress.results) {
                    showResults(progress.results);
                }
            }
        } catch (error) {
            console.error('Progress polling error:', error);
        }
    }, 500); // Poll every 500ms
}

function updateProgressDisplay(progress) {
    const stage = progress.stage || 'Processing...';
    const wordsCovered = progress.words_covered || 0;
    const sentencesSelected = progress.sentences_selected || 0;
    const total = progress.total || 2000;
    
    const percent = Math.min(Math.round((wordsCovered / total) * 100), 100);

    document.getElementById('progressStage').textContent = stage;
    document.getElementById('progressPercent').textContent = percent + '%';
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('wordsCovered').textContent = wordsCovered.toLocaleString();
    document.getElementById('sentencesSelected').textContent = sentencesSelected.toLocaleString();
    document.getElementById('totalWords').textContent = total.toLocaleString();

    if (progress.current && progress.total) {
        document.getElementById('currentSentence').textContent = 
            `Analyzing sentence ${progress.current.toLocaleString()} of ${progress.total.toLocaleString()}`;
    }
}

function showResults(results) {
    // Hide progress, show results
    document.getElementById('progressDisplay').classList.add('hidden');
    document.getElementById('resultsDisplay').classList.remove('hidden');

    // Update result values
    document.getElementById('resultSentences').textContent = results.total_sentences.toLocaleString();
    document.getElementById('resultWords').textContent = results.words_covered.toLocaleString();
    document.getElementById('resultEfficiency').textContent = results.efficiency.toFixed(2);
    document.getElementById('resultTime').textContent = results.processing_time.toFixed(1) + 's';
    document.getElementById('algorithmUsed').textContent = results.algorithm_used.replace('_', ' ');
    document.getElementById('coveragePercent').textContent = 
        `${results.coverage_percent}% of ${results.total_words.toLocaleString()} words`;

    // Target status
    const maxTarget = parseInt(document.getElementById('maxSentences').value);
    const targetStatus = document.getElementById('targetStatus');
    if (results.total_sentences <= maxTarget) {
        targetStatus.textContent = `✓ Under ${maxTarget} target`;
        targetStatus.classList.add('text-green-600');
        targetStatus.classList.remove('text-orange-600');
    } else {
        targetStatus.textContent = `${results.total_sentences - maxTarget} over target`;
        targetStatus.classList.add('text-orange-600');
        targetStatus.classList.remove('text-green-600');
    }

    // Missing words warning
    if (results.missing_words && results.missing_words.length > 0) {
        const missingCount = results.missing_words.length;
        document.getElementById('missingWordsWarning').classList.remove('hidden');
        document.getElementById('missingWordsText').textContent = 
            `${missingCount.toLocaleString()} words from your list weren't found in the source sentences. ` +
            `Check the "Missing Words" tab in the output sheet for the complete list and suggestions.`;
    }

    // Sheet link
    if (results.sheet_url) {
        document.getElementById('sheetLink').href = results.sheet_url;
    }

    // Scroll to results
    document.getElementById('resultsDisplay').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function downloadCSV() {
    // Get latest files
    fetch('/api/list-outputs')
        .then(response => response.json())
        .then(data => {
            if (data.files && data.files.length > 0) {
                // Download the 4 most recent files
                const recentFiles = data.files.slice(0, 4);
                recentFiles.forEach((file, index) => {
                    setTimeout(() => {
                        const link = document.createElement('a');
                        link.href = `/api/download/${file.name}`;
                        link.download = file.name;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }, index * 300); // Stagger downloads
                });
            } else {
                showError('No CSV files found. They should be in the output/ folder.');
            }
        })
        .catch(error => {
            showError('Error downloading files: ' + error.message);
        });
}

function resetForm() {
    // Clear intervals
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    // Reset form
    document.getElementById('optimizerForm').reset();
    selectedFile = null;
    document.getElementById('dropZoneText').innerHTML = 
        'Drag & drop your file here<br><span class="text-sm text-gray-500">or click to browse • CSV, TXT, TSV supported</span>';
    document.getElementById('dropZoneText').classList.remove('text-green-600');

    // Show input form, hide others
    document.getElementById('inputForm').classList.remove('hidden');
    document.getElementById('progressDisplay').classList.add('hidden');
    document.getElementById('resultsDisplay').classList.add('hidden');
    document.getElementById('missingWordsWarning').classList.add('hidden');

    // Reset progress values
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('wordsCovered').textContent = '0';
    document.getElementById('sentencesSelected').textContent = '0';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    alert('⚠ ' + message);
}

async function testAPIConnection() {
    try {
        const response = await fetch('/api/test');
        const data = await response.json();
        if (data.status === 'ok') {
            console.log('✓ API Connection OK:', data.message);
            console.log('✓ Features:', data.features);
        }
    } catch (error) {
        console.warn('API connection test failed:', error);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.getElementById('optimizerForm');
        if (!document.getElementById('inputForm').classList.contains('hidden')) {
            form.requestSubmit();
        }
    }
    // Escape to reset
    if (e.key === 'Escape') {
        if (!document.getElementById('resultsDisplay').classList.contains('hidden')) {
            resetForm();
        }
    }
});
