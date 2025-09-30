"""
Enhanced Sentence Optimizer with improved algorithms and performance
Supports greedy, weighted greedy, and beam search optimization
"""

import time
import heapq
from typing import List, Set, Dict, Callable, Optional, Tuple
from dataclasses import dataclass, field
from core.matcher import EnhancedWordMatcher
from core.config import OptimizerConfig


@dataclass
class OptimizationResult:
    """Structured optimization results"""
    selected_sentences: List[Dict] = field(default_factory=list)
    total_sentences: int = 0
    words_covered: int = 0
    total_words: int = 0
    coverage_percent: float = 0.0
    efficiency: float = 0.0
    missing_words: List[Dict] = field(default_factory=list)
    processing_time: float = 0.0
    coverage_map: List[Dict] = field(default_factory=list)
    algorithm_used: str = "greedy"
    iterations: int = 0


class EnhancedSentenceOptimizer:
    """
    Enhanced optimizer with multiple algorithms and performance improvements
    """
    
    def __init__(self, 
                 word_list: List[Dict], 
                 sentences: List[str],
                 config: OptimizerConfig = None,
                 callback: Optional[Callable] = None):
        
        self.word_list = word_list
        self.sentences = sentences
        self.config = config or OptimizerConfig()
        self.callback = callback
        
        self.matcher = EnhancedWordMatcher(word_list, config)
        self.selected_sentences = []
        self.coverage_map = {}  # word_idx -> list of sentence indices
        self.uncovered_words = set()
        self.sentence_coverage = []  # Precomputed coverage for each sentence
    
    def optimize(self, algorithm: str = "weighted_greedy") -> OptimizationResult:
        """
        Run optimization with specified algorithm
        Algorithms: 'greedy', 'weighted_greedy', 'beam_search'
        """
        start_time = time.time()
        
        # Precompute sentence coverage
        self._precompute_coverage()
        
        # Run selected algorithm
        if algorithm == "greedy":
            self._optimize_greedy()
        elif algorithm == "weighted_greedy":
            self._optimize_weighted_greedy()
        elif algorithm == "beam_search":
            self._optimize_beam_search()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Build results
        end_time = time.time()
        return self._build_results(end_time - start_time, algorithm)
    
    def _precompute_coverage(self):
        """Precompute word coverage for all sentences with progress"""
        print("Precomputing sentence coverage...")
        self._report_progress('Analyzing sentences...', 0, len(self.sentences), 0, 0)
        
        # Use batch processing if enabled
        if self.config.parallel_processing:
            self.sentence_coverage = self.matcher.batch_process_sentences(self.sentences)
        else:
            self.sentence_coverage = []
            for idx, sentence in enumerate(self.sentences):
                covered = self.matcher.find_words_in_sentence(sentence)
                self.sentence_coverage.append(covered)
                
                if (idx + 1) % 100 == 0:
                    self._report_progress('Analyzing sentences...', idx + 1, 
                                        len(self.sentences), 0, 0)
        
        # Build coverage map
        for sent_idx, covered in enumerate(self.sentence_coverage):
            for word_idx in covered:
                if word_idx not in self.coverage_map:
                    self.coverage_map[word_idx] = []
                self.coverage_map[word_idx].append(sent_idx)
        
        # Initialize uncovered words
        self.uncovered_words = set(range(len(self.word_list)))
        
        print(f"✓ Analysis complete: {len(self.sentences)} sentences processed")
    
    def _optimize_greedy(self):
        """Standard greedy algorithm - always pick sentence covering most uncovered words"""
        print("Running greedy optimization...")
        iteration = 0
        
        while self.uncovered_words and len(self.selected_sentences) < self.config.max_sentences:
            iteration += 1
            best_idx, best_coverage, best_score = None, set(), 0
            
            # Find best sentence
            for idx, covered in enumerate(self.sentence_coverage):
                if self._is_already_selected(idx):
                    continue
                
                new_coverage = covered & self.uncovered_words
                score = len(new_coverage)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
                    best_coverage = new_coverage
            
            # No improvement possible
            if best_score == 0:
                print(f"  No more improvements possible at iteration {iteration}")
                break
            
            # Add best sentence
            self._add_sentence(best_idx, best_coverage)
            
            # Progress report
            if iteration % self.config.progress_interval == 0:
                self._report_progress(
                    'Optimizing (Greedy)...',
                    iteration,
                    len(self.word_list),
                    len(self.word_list) - len(self.uncovered_words),
                    len(self.selected_sentences)
                )
    
    def _optimize_weighted_greedy(self):
        """
        Weighted greedy - considers both new words AND reinforcement of existing coverage
        Better for finding robust sentence sets
        """
        print("Running weighted greedy optimization...")
        iteration = 0
        
        # Weights
        NEW_WORD_WEIGHT = 10.0  # Prioritize new words
        REDUNDANCY_WEIGHT = 0.5  # But value reinforcing covered words
        
        while self.uncovered_words and len(self.selected_sentences) < self.config.max_sentences:
            iteration += 1
            best_idx, best_coverage, best_score = None, set(), 0.0
            
            for idx, covered in enumerate(self.sentence_coverage):
                if self._is_already_selected(idx):
                    continue
                
                new_coverage = covered & self.uncovered_words
                redundant_coverage = covered - self.uncovered_words
                
                # Weighted score
                score = (len(new_coverage) * NEW_WORD_WEIGHT + 
                        len(redundant_coverage) * REDUNDANCY_WEIGHT)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
                    best_coverage = new_coverage
            
            if best_score == 0:
                print(f"  No more improvements possible at iteration {iteration}")
                break
            
            self._add_sentence(best_idx, best_coverage)
            
            if iteration % self.config.progress_interval == 0:
                self._report_progress(
                    'Optimizing (Weighted Greedy)...',
                    iteration,
                    len(self.word_list),
                    len(self.word_list) - len(self.uncovered_words),
                    len(self.selected_sentences)
                )
    
    def _optimize_beam_search(self, beam_width: int = 5, depth: int = 3):
        """
        Beam search - explores multiple paths simultaneously
        More thorough but slower
        """
        print(f"Running beam search (width={beam_width}, depth={depth})...")
        
        # Priority queue: (negative_coverage, sentence_indices_set, uncovered_words)
        beam = [(0, tuple(), self.uncovered_words.copy())]
        
        for level in range(depth):
            print(f"  Beam search level {level + 1}/{depth}...")
            next_beam = []
            
            for neg_coverage, selected_tuple, uncovered in beam:
                selected_set = set(selected_tuple)
                
                # Try adding each candidate sentence
                candidates = []
                for idx, covered in enumerate(self.sentence_coverage):
                    if idx in selected_set:
                        continue
                    
                    new_coverage = covered & uncovered
                    if not new_coverage:
                        continue
                    
                    new_uncovered = uncovered - new_coverage
                    new_selected = selected_tuple + (idx,)
                    score = -(len(self.word_list) - len(new_uncovered))  # Negative for max heap
                    
                    candidates.append((score, new_selected, new_uncovered))
                
                # Keep top beam_width candidates
                candidates.sort()
                next_beam.extend(candidates[:beam_width])
            
            # Keep overall top beam_width
            next_beam.sort()
            beam = next_beam[:beam_width]
            
            if not beam:
                break
        
        # Use best path
        if beam:
            _, best_selected, final_uncovered = beam[0]
            for sent_idx in best_selected:
                covered = self.sentence_coverage[sent_idx] & self.uncovered_words
                self._add_sentence(sent_idx, covered)
            
            print(f"✓ Beam search selected {len(best_selected)} sentences")
        
        # Continue with greedy if not complete
        if self.uncovered_words and len(self.selected_sentences) < self.config.max_sentences:
            print("  Continuing with greedy...")
            self._optimize_greedy()
    
    def _add_sentence(self, sent_idx: int, new_coverage: Set[int]):
        """Add sentence to selection"""
        self.selected_sentences.append({
            'index': sent_idx,
            'sentence': self.sentences[sent_idx],
            'words_covered': [self.word_list[w]['french'] for w in new_coverage],
            'new_words_count': len(new_coverage),
            'total_words': len(self.sentence_coverage[sent_idx])
        })
        self.uncovered_words -= new_coverage
    
    def _is_already_selected(self, sent_idx: int) -> bool:
        """Check if sentence already selected"""
        return any(s['index'] == sent_idx for s in self.selected_sentences)
    
    def _report_progress(self, stage: str, current: int, total: int, 
                        words_covered: int, sentences_selected: int):
        """Report progress via callback"""
        if self.callback:
            self.callback({
                'stage': stage,
                'current': current,
                'total': total,
                'words_covered': words_covered,
                'sentences_selected': sentences_selected
            })
    
    def _build_results(self, processing_time: float, algorithm: str) -> OptimizationResult:
        """Build structured optimization results"""
        missing_words = [self.word_list[idx] for idx in self.uncovered_words]
        words_covered = len(self.word_list) - len(self.uncovered_words)
        coverage_percent = (words_covered / len(self.word_list)) * 100
        efficiency = words_covered / len(self.selected_sentences) if self.selected_sentences else 0
        
        result = OptimizationResult(
            selected_sentences=self.selected_sentences,
            total_sentences=len(self.selected_sentences),
            words_covered=words_covered,
            total_words=len(self.word_list),
            coverage_percent=round(coverage_percent, 2),
            efficiency=round(efficiency, 2),
            missing_words=missing_words,
            processing_time=round(processing_time, 2),
            coverage_map=self._build_coverage_map(),
            algorithm_used=algorithm,
            iterations=len(self.selected_sentences)
        )
        
        self._print_summary(result)
        return result
    
    def _build_coverage_map(self) -> List[Dict]:
        """Build detailed coverage map"""
        coverage_data = []
        selected_indices = {s['index'] for s in self.selected_sentences}
        
        for idx, word in enumerate(self.word_list):
            sentence_indices = self.coverage_map.get(idx, [])
            in_selected = [i for i in sentence_indices if i in selected_indices]
            
            coverage_data.append({
                'french': word['french'],
                'english': word['english'],
                'pos': word.get('pos', ''),
                'found': idx not in self.uncovered_words,
                'sentence_count': len(in_selected),
                'sentence_indices': in_selected[:5]  # Limit for display
            })
        
        return coverage_data
    
    def _print_summary(self, result: OptimizationResult):
        """Print optimization summary"""
        print(f"\n{'='*70}")
        print(f"OPTIMIZATION COMPLETE ({result.algorithm_used.upper()})")
        print(f"{'='*70}")
        print(f"Sentences selected:  {result.total_sentences:,}")
        print(f"Words covered:       {result.words_covered:,} / {result.total_words:,} ({result.coverage_percent}%)")
        print(f"Efficiency:          {result.efficiency} words/sentence")
        print(f"Missing words:       {len(result.missing_words):,}")
        print(f"Processing time:     {result.processing_time}s")
        print(f"{'='*70}\n")
