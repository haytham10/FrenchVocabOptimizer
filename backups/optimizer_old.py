"""
French Vocabulary Sentence Optimizer
Main optimization logic using greedy algorithm
"""

import sys
import time
from typing import List, Set, Dict, Tuple
from matcher import WordMatcher
from sheets_handler import SheetsHandler


class SentenceOptimizer:
    def __init__(self, word_list: List[Dict], sentences: List[str], 
                 max_sentences: int = 600, callback=None):
        self.word_list = word_list
        self.sentences = sentences
        self.max_sentences = max_sentences
        self.callback = callback  # Progress callback function
        
        self.matcher = WordMatcher(word_list)
        self.selected_sentences = []
        self.coverage_map = {}  # word -> list of sentence indices
        self.uncovered_words = set()
        
    def optimize(self) -> Dict:
        """
        Main optimization algorithm using greedy approach
        Returns optimization results
        """
        start_time = time.time()
        
        # Initialize uncovered words set
        self.uncovered_words = set(range(len(self.word_list)))
        
        # Progress update
        if self.callback:
            self.callback({
                'stage': 'Analyzing sentences...',
                'current': 0,
                'total': len(self.sentences),
                'words_covered': 0,
                'sentences_selected': 0
            })
        
        # Precompute word coverage for all sentences
        print("Precomputing sentence coverage...")
        sentence_coverage = []
        for idx, sentence in enumerate(self.sentences):
            covered = self.matcher.find_words_in_sentence(sentence)
            sentence_coverage.append(covered)
            
            # Track which sentences contain each word
            for word_idx in covered:
                if word_idx not in self.coverage_map:
                    self.coverage_map[word_idx] = []
                self.coverage_map[word_idx].append(idx)
            
            if idx % 100 == 0 and self.callback:
                self.callback({
                    'stage': 'Analyzing sentences...',
                    'current': idx,
                    'total': len(self.sentences),
                    'words_covered': len(self.word_list) - len(self.uncovered_words),
                    'sentences_selected': len(self.selected_sentences)
                })
        
        print(f"Analysis complete. Found coverage in {len(sentence_coverage)} sentences")
        
        # Greedy selection algorithm
        print("Starting greedy optimization...")
        iteration = 0
        
        while self.uncovered_words and len(self.selected_sentences) < self.max_sentences:
            iteration += 1
            best_sentence_idx = None
            best_coverage = set()
            best_score = 0
            
            # Find sentence that covers most uncovered words
            for idx, covered in enumerate(sentence_coverage):
                if idx in [s['index'] for s in self.selected_sentences]:
                    continue  # Already selected
                
                # Calculate new words this sentence would cover
                new_coverage = covered & self.uncovered_words
                score = len(new_coverage)
                
                if score > best_score:
                    best_score = score
                    best_sentence_idx = idx
                    best_coverage = new_coverage
            
            # No more sentences can cover remaining words
            if best_score == 0:
                print(f"No more sentences cover remaining words. Stopping.")
                break
            
            # Add best sentence to selection
            self.selected_sentences.append({
                'index': best_sentence_idx,
                'sentence': self.sentences[best_sentence_idx],
                'words_covered': [self.word_list[w]['french'] for w in best_coverage],
                'new_words_count': len(best_coverage)
            })
            
            # Update uncovered words
            self.uncovered_words -= best_coverage
            
            # Progress update
            if self.callback and iteration % 5 == 0:
                self.callback({
                    'stage': 'Optimizing sentence selection...',
                    'current': iteration,
                    'total': len(self.word_list),
                    'words_covered': len(self.word_list) - len(self.uncovered_words),
                    'sentences_selected': len(self.selected_sentences)
                })
            
            if iteration % 50 == 0:
                print(f"Iteration {iteration}: Selected {len(self.selected_sentences)} sentences, "
                      f"covered {len(self.word_list) - len(self.uncovered_words)}/{len(self.word_list)} words")
        
        # Calculate final statistics
        end_time = time.time()
        processing_time = end_time - start_time
        
        missing_words = [self.word_list[idx] for idx in self.uncovered_words]
        words_covered = len(self.word_list) - len(self.uncovered_words)
        coverage_percent = (words_covered / len(self.word_list)) * 100
        efficiency = words_covered / len(self.selected_sentences) if self.selected_sentences else 0
        
        results = {
            'selected_sentences': self.selected_sentences,
            'total_sentences': len(self.selected_sentences),
            'words_covered': words_covered,
            'total_words': len(self.word_list),
            'coverage_percent': round(coverage_percent, 2),
            'efficiency': round(efficiency, 2),
            'missing_words': missing_words,
            'processing_time': round(processing_time, 2),
            'coverage_map': self._build_coverage_map()
        }
        
        print(f"\n{'='*60}")
        print(f"OPTIMIZATION COMPLETE")
        print(f"{'='*60}")
        print(f"Sentences selected: {results['total_sentences']}")
        print(f"Words covered: {results['words_covered']}/{results['total_words']} ({results['coverage_percent']}%)")
        print(f"Efficiency: {results['efficiency']} words per sentence")
        print(f"Missing words: {len(missing_words)}")
        print(f"Processing time: {results['processing_time']}s")
        print(f"{'='*60}\n")
        
        return results
    
    def _build_coverage_map(self) -> List[Dict]:
        """Build detailed coverage map for each word"""
        coverage_data = []
        selected_indices = set(s['index'] for s in self.selected_sentences)
        
        for idx, word in enumerate(self.word_list):
            sentence_indices = self.coverage_map.get(idx, [])
            # Filter to only selected sentences
            in_selected = [i for i in sentence_indices if i in selected_indices]
            
            coverage_data.append({
                'french': word['french'],
                'english': word['english'],
                'pos': word.get('pos', ''),
                'found': idx not in self.uncovered_words,
                'sentence_count': len(in_selected),
                'sentence_indices': in_selected
            })
        
        return coverage_data


def main():
    """Command-line interface"""
    import argparse
    import csv
    
    parser = argparse.ArgumentParser(description='French Vocabulary Sentence Optimizer')
    parser.add_argument('--words', required=True, help='Google Sheets URL or CSV file with word list')
    parser.add_argument('--sentences', required=True, help='CSV/TXT file with sentences')
    parser.add_argument('--max', type=int, default=600, help='Maximum sentences to select')
    parser.add_argument('--output', default='output', help='Output folder for CSV files')
    
    args = parser.parse_args()
    
    print("French Vocabulary Sentence Optimizer")
    print("=" * 60)
    
    # Load word list
    print(f"\nLoading word list from: {args.words}")
    sheets_handler = SheetsHandler()
    
    if args.words.startswith('http'):
        word_list = sheets_handler.load_word_list(args.words)
    else:
        # Load from CSV
        word_list = []
        with open(args.words, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word_list.append({
                    'french': row.get('French', row.get('french', '')),
                    'english': row.get('English', row.get('english', '')),
                    'pos': row.get('POS', row.get('pos', ''))
                })
    
    print(f"Loaded {len(word_list)} words")
    
    # Load sentences
    print(f"\nLoading sentences from: {args.sentences}")
    sentences = []
    with open(args.sentences, 'r', encoding='utf-8') as f:
        if args.sentences.endswith('.csv'):
            reader = csv.reader(f)
            for row in reader:
                if row:
                    sentences.append(row[0])
        else:
            sentences = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(sentences)} sentences")
    
    # Run optimization
    print(f"\nStarting optimization (max {args.max} sentences)...")
    optimizer = SentenceOptimizer(word_list, sentences, args.max)
    results = optimizer.optimize()
    
    # Save results to Google Sheets
    print("\nSaving results to Google Sheets...")
    sheet_url = sheets_handler.create_output_sheet(results, word_list)
    print(f"Results saved to: {sheet_url}")
    
    # Save CSV backup
    print(f"\nSaving CSV backup to {args.output}/...")
    sheets_handler.save_csv_backup(results, args.output)
    print("CSV files saved successfully")
    
    print("\nOptimization complete!")


if __name__ == '__main__':
    main()