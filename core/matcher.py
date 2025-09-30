"""
Enhanced Word Matcher with caching and optimization
Handles gender variations, conjugations, multi-word phrases with improved performance
"""

import re
import spacy
import pickle
import hashlib
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from core.config import OptimizerConfig


class EnhancedWordMatcher:
    """Optimized word matcher with caching and parallel processing"""
    
    def __init__(self, word_list: List[Dict], config: OptimizerConfig = None):
        self.word_list = word_list
        self.config = config or OptimizerConfig()
        self.nlp = None
        self.cache_dir = Path(self.config.cache_folder)
        self.cache_dir.mkdir(exist_ok=True)
        
        self._load_spacy_model()
        self._preprocess_words()
        self._build_lookup_tables()
    
    def _load_spacy_model(self):
        """Load French spaCy model with optimizations"""
        try:
            print(f"Loading spaCy model: {self.config.spacy_model}...")
            self.nlp = spacy.load(self.config.spacy_model)
            
            # Disable unnecessary pipeline components for speed
            disable = ['parser', 'ner'] if self.config.lemma_matching else ['lemmatizer', 'parser', 'ner']
            for component in disable:
                if component in self.nlp.pipe_names:
                    self.nlp.disable_pipe(component)
            
            print(f"✓ spaCy model loaded (Active pipes: {self.nlp.pipe_names})")
        except OSError:
            print(f"ERROR: spaCy model '{self.config.spacy_model}' not found!")
            print(f"Install with: python -m spacy download {self.config.spacy_model}")
            raise
    
    def _preprocess_words(self):
        """Enhanced preprocessing with caching"""
        cache_file = self.cache_dir / self._get_word_list_hash()
        
        if self.config.cache_enabled and cache_file.exists():
            print("Loading preprocessed words from cache...")
            with open(cache_file, 'rb') as f:
                self.word_list = pickle.load(f)
            print(f"✓ Loaded {len(self.word_list)} words from cache")
            return
        
        print("Preprocessing word list...")
        
        for idx, word_data in enumerate(self.word_list):
            french = word_data['french']
            
            # Handle gender variations (Un|Une, le|la)
            if '|' in french:
                word_data['variations'] = [v.strip() for v in french.split('|')]
            else:
                word_data['variations'] = [french]
            
            # Multi-word phrase detection
            word_data['is_phrase'] = any(' ' in v for v in word_data['variations'])
            
            # Get lemmas for each variation
            word_data['lemmas'] = set()
            word_data['tokens'] = set()
            
            for variation in word_data['variations']:
                doc = self.nlp(variation.lower())
                for token in doc:
                    word_data['tokens'].add(token.text)
                    if self.config.lemma_matching:
                        word_data['lemmas'].add(token.lemma_)
            
            # Store index
            word_data['index'] = idx
            
            if (idx + 1) % 500 == 0:
                print(f"  Processed {idx + 1}/{len(self.word_list)} words...")
        
        # Save to cache
        if self.config.cache_enabled:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.word_list, f)
            print(f"✓ Saved preprocessed words to cache")
        
        print(f"✓ Preprocessed {len(self.word_list)} words")
    
    def _build_lookup_tables(self):
        """Build fast lookup tables for matching"""
        print("Building lookup tables...")
        
        self.lemma_to_word_idx = {}
        self.token_to_word_idx = {}
        self.phrase_patterns = []
        
        for word_data in self.word_list:
            idx = word_data['index']
            
            # Lemma lookup
            for lemma in word_data.get('lemmas', []):
                if lemma not in self.lemma_to_word_idx:
                    self.lemma_to_word_idx[lemma] = set()
                self.lemma_to_word_idx[lemma].add(idx)
            
            # Token lookup
            for token in word_data.get('tokens', []):
                if token not in self.token_to_word_idx:
                    self.token_to_word_idx[token] = set()
                self.token_to_word_idx[token].add(idx)
            
            # Phrase patterns
            if word_data['is_phrase']:
                for variation in word_data['variations']:
                    self.phrase_patterns.append({
                        'pattern': variation.lower(),
                        'regex': re.compile(r'\b' + re.escape(variation.lower()) + r'\b'),
                        'word_idx': idx
                    })
        
        print(f"✓ Built lookup tables: {len(self.lemma_to_word_idx)} lemmas, "
              f"{len(self.token_to_word_idx)} tokens, {len(self.phrase_patterns)} phrases")
    
    def find_words_in_sentence(self, sentence: str) -> Set[int]:
        """
        Find all words from word list in sentence (optimized)
        Returns set of word indices
        """
        if not sentence or not sentence.strip():
            return set()
        
        found_words = set()
        sentence_lower = sentence.lower()
        
        # Process with spaCy
        doc = self.nlp(sentence_lower)
        tokens = {token.text for token in doc}
        lemmas = {token.lemma_ for token in doc} if self.config.lemma_matching else set()
        
        # Method 1: Multi-word phrase matching (fastest for phrases)
        for phrase_data in self.phrase_patterns:
            if phrase_data['regex'].search(sentence_lower):
                found_words.add(phrase_data['word_idx'])
        
        # Method 2: Token-based lookup
        for token in tokens:
            if token in self.token_to_word_idx:
                found_words.update(self.token_to_word_idx[token])
        
        # Method 3: Lemma-based lookup (for conjugations)
        if self.config.lemma_matching:
            for lemma in lemmas:
                if lemma in self.lemma_to_word_idx:
                    found_words.update(self.lemma_to_word_idx[lemma])
        
        return found_words
    
    def batch_process_sentences(self, sentences: List[str]) -> List[Set[int]]:
        """Process multiple sentences in parallel"""
        if not self.config.parallel_processing or len(sentences) < 100:
            return [self.find_words_in_sentence(s) for s in sentences]
        
        print(f"Processing {len(sentences)} sentences in parallel...")
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            results = list(executor.map(self.find_words_in_sentence, sentences))
        return results
    
    def get_match_details(self, word_idx: int, sentence: str) -> Dict:
        """Get detailed matching information for debugging"""
        word_data = self.word_list[word_idx]
        doc = self.nlp(sentence.lower())
        sentence_lower = sentence.lower()
        
        details = {
            'word': word_data['french'],
            'found': False,
            'match_type': None,
            'matched_form': None,
            'position': -1
        }
        
        # Check phrase
        if word_data['is_phrase']:
            for variation in word_data['variations']:
                match = re.search(r'\b' + re.escape(variation.lower()) + r'\b', sentence_lower)
                if match:
                    details.update({
                        'found': True,
                        'match_type': 'phrase',
                        'matched_form': variation,
                        'position': match.start()
                    })
                    return details
        
        # Check exact tokens
        for token in doc:
            if token.text in word_data['tokens']:
                details.update({
                    'found': True,
                    'match_type': 'exact',
                    'matched_form': token.text,
                    'position': token.idx
                })
                return details
        
        # Check lemmas
        if self.config.lemma_matching:
            for token in doc:
                if token.lemma_ in word_data['lemmas']:
                    details.update({
                        'found': True,
                        'match_type': 'lemma',
                        'matched_form': token.text,
                        'position': token.idx
                    })
                    return details
        
        return details
    
    def _get_word_list_hash(self) -> str:
        """Generate cache key from word list"""
        word_str = ''.join([w['french'] for w in self.word_list])
        return hashlib.md5(word_str.encode()).hexdigest() + '.pkl'
