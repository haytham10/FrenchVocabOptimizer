// French Vocabulary Sentence Optimizer - Client-side JavaScript

let selectedFile = null;
let progressInterval = null;

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('sentenceFile');
    const form = document.getElementById('optimizerForm');

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('border-indigo-500');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-indigo-500');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-indigo-500');

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

    // Form submission
    form.addEventListener('submit', handleFormSubmit);
});

function handleFileSelect(file) {
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.txt'))) {
        selectedFile = file;
        document.getElementById('dropZoneText').textContent = file.name;
        document.getElementById('dropZoneText').classList.add('text-green-600');
    } else {
        alert('Please select a CSV or TXT file');
        document.getElementById('sentenceFile').value = '';
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const wordListUrl = document.getElementById('wordListUrl').value;
    const maxSentences = document.getElementById('maxSentences').value;
    const strictness = document.getElementById('strictness').value;

    if (!selectedFile) {
        alert('Please select a sentence file');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('word_list_url', wordListUrl);
    formData.append('max_sentences', maxSentences);
    formData.append('strictness', strictness);
    formData.append('sentence_file', selectedFile);

    // Hide input form, show progress
    document.getElementById('inputForm').classList.add('hidden');
    document.getElementById('progressDisplay').classList.remove('hidden');

    try {
        // Start optimization
        const response = await fetch('/api/optimize', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to start optimization');
        }

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        alert('Error: ' + error.message);
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
                    alert('Error: ' + progress.error);
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
    const percent = Math.round((wordsCovered / 2000) * 100);

    document.getElementById('progressStage').textContent = stage;
    document.getElementById('progressPercent').textContent = percent + '%';
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('wordsCovered').textContent = wordsCovered;
    document.getElementById('sentencesSelected').textContent = sentencesSelected;

    if (progress.current && progress.total) {
        document.getElementById('currentSentence').textContent = 
            `Analyzing sentence ${progress.current} of ${progress.total}`;
    }
}

function showResults(results) {
    // Hide progress, show results
    document.getElementById('progressDisplay').classList.add('hidden');
    document.getElementById('resultsDisplay').classList.remove('hidden');

    // Update result values
    document.getElementById('resultSentences').textContent = results.total_sentences;
    document.getElementById('resultWords').textContent = results.words_covered;
    document.getElementById('resultEfficiency').textContent = results.efficiency.toFixed(2);
    document.getElementById('coveragePercent').textContent = results.coverage_percent + '% coverage';

    // Target status
    const maxTarget = parseInt(document.getElementById('maxSentences').value);
    if (results.total_sentences <= maxTarget) {
        document.getElementById('targetStatus').textContent = `✓ Under ${maxTarget} target`;
    } else {
        document.getElementById('targetStatus').textContent = `${results.total_sentences - maxTarget} over target`;
    }

    // Missing words warning
    if (results.missing_words && results.missing_words.length > 0) {
        const missingCount = results.missing_words.length;
        document.getElementById('missingWordsWarning').classList.remove('hidden');
        document.getElementById('missingWordsText').textContent = 
            `${missingCount} words from your list weren't found in the source sentences. Check the "Missing Words" tab in the output sheet for details.`;
    }

    // Sheet link
    if (results.sheet_url) {
        document.getElementById('sheetLink').href = results.sheet_url;
    }
}

function downloadCSV() {
    alert('CSV files have been saved to the output/ folder in your project directory');
}

function resetForm() {
    // Clear intervals
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    // Reset form
    document.getElementById('optimizerForm').reset();
    selectedFile = null;
    document.getElementById('dropZoneText').textContent = 'Drag & drop your sentence file here';
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
}