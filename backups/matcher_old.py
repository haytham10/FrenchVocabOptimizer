"""
Word Matching Engine
Handles gender variations, verb conjugations, multi-word phrases, and lemmatization
"""

import re
import spacy
from typing import List, Set, Dict


class WordMatcher:
    def __init__(self, word_list: List[Dict]):
        self.word_list = word_list
        self.nlp = None
        self._load_spacy_model()
        self._preprocess_words()
    
    def _load_spacy_model(self):
        """Load French spaCy model"""
        try:
            print("Loading French spaCy model...")
            self.nlp = spacy.load('fr_core_news_lg')
            print("spaCy model loaded successfully")
        except OSError:
            print("ERROR: French spaCy model not found!")
            print("Please run: python -m spacy download fr_core_news_lg")
            raise
    
    def _preprocess_words(self):
        """Preprocess word list for efficient matching"""
        print("Preprocessing word list...")
        
        for idx, word_data in enumerate(self.word_list):
            french = word_data['french']
            
            # Handle gender variations (Un|Une)
            if '|' in french:
                word_data['variations'] = french.split('|')
            else:
                word_data['variations'] = [french]
            
            # Check if multi-word phrase
            word_data['is_phrase'] = ' ' in french.replace('|', '')
            
            # Get lemmas for each variation
            word_data['lemmas'] = []
            for variation in word_data['variations']:
                doc = self.nlp(variation.lower())
                lemmas = [token.lemma_.lower() for token in doc]
                word_data['lemmas'].extend(lemmas)
            
            # Remove duplicates
            word_data['lemmas'] = list(set(word_data['lemmas']))
            
            # Store index for quick lookup
            word_data['index'] = idx
        
        print(f"Preprocessed {len(self.word_list)} words")
    
    def find_words_in_sentence(self, sentence: str) -> Set[int]:
        """
        Find all words from word list that appear in the sentence
        Returns set of word indices
        """
        if not sentence or not sentence.strip():
            return set()
        
        found_words = set()
        
        # Process sentence with spaCy
        doc = self.nlp(sentence.lower())
        sentence_lower = sentence.lower()
        
        # Extract tokens and lemmas
        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        
        for word_data in self.word_list:
            word_idx = word_data['index']
            
            # Skip if already found
            if word_idx in found_words:
                continue
            
            # Method 1: Multi-word phrase matching (exact order)
            if word_data['is_phrase']:
                for variation in word_data['variations']:
                    variation_lower = variation.lower()
                    if variation_lower in sentence_lower:
                        found_words.add(word_idx)
                        break
                
                if word_idx in found_words:
                    continue
            
            # Method 2: Exact word matching (for variations)
            for variation in word_data['variations']:
                variation_lower = variation.lower()
                
                # Check if word appears as complete token
                if variation_lower in tokens:
                    found_words.add(word_idx)
                    break
                
                # Check with word boundaries
                pattern = r'\b' + re.escape(variation_lower) + r'\b'
                if re.search(pattern, sentence_lower):
                    found_words.add(word_idx)
                    break
            
            if word_idx in found_words:
                continue
            
            # Method 3: Lemma matching (for conjugations)
            for word_lemma in word_data['lemmas']:
                if word_lemma in lemmas:
                    found_words.add(word_idx)
                    break
        
        return found_words
    
    def match_word_in_sentence(self, word_data: Dict, sentence: str) -> bool:
        """
        Check if a specific word appears in the sentence
        More detailed version for debugging
        """
        doc = self.nlp(sentence.lower())
        sentence_lower = sentence.lower()
        
        # Multi-word phrase
        if word_data['is_phrase']:
            for variation in word_data['variations']:
                if variation.lower() in sentence_lower:
                    return True
        
        # Exact word match
        tokens = [token.text for token in doc]
        for variation in word_data['variations']:
            if variation.lower() in tokens:
                return True
            
            pattern = r'\b' + re.escape(variation.lower()) + r'\b'
            if re.search(pattern, sentence_lower):
                return True
        
        # Lemma match
        lemmas = [token.lemma_ for token in doc]
        for word_lemma in word_data['lemmas']:
            if word_lemma in lemmas:
                return True
        
        return False
    
    def get_matching_details(self, word_data: Dict, sentence: str) -> Dict:
        """
        Get detailed information about how a word matches in a sentence
        Useful for debugging and verification
        """
        doc = self.nlp(sentence.lower())
        sentence_lower = sentence.lower()
        
        details = {
            'word': word_data['french'],
            'found': False,
            'match_type': None,
            'matched_form': None,
            'position': -1
        }
        
        # Check multi-word phrase
        if word_data['is_phrase']:
            for variation in word_data['variations']:
                variation_lower = variation.lower()
                if variation_lower in sentence_lower:
                    details['found'] = True
                    details['match_type'] = 'phrase'
                    details['matched_form'] = variation
                    details['position'] = sentence_lower.find(variation_lower)
                    return details
        
        # Check exact word
        tokens = [(token.text, token.idx) for token in doc]
        for variation in word_data['variations']:
            variation_lower = variation.lower()
            for token_text, token_idx in tokens:
                if token_text == variation_lower:
                    details['found'] = True
                    details['match_type'] = 'exact'
                    details['matched_form'] = variation
                    details['position'] = token_idx
                    return details
        
        # Check lemma
        lemma_tokens = [(token.lemma_, token.text, token.idx) for token in doc]
        for word_lemma in word_data['lemmas']:
            for lemma, text, idx in lemma_tokens:
                if lemma == word_lemma:
                    details['found'] = True
                    details['match_type'] = 'lemma'
                    details['matched_form'] = text
                    details['position'] = idx
                    return details
        
        return details


def test_matcher():
    """Test the matcher with sample data"""
    print("Testing Word Matcher...")
    print("=" * 60)
    
    # Sample word list
    word_list = [
        {'french': 'être', 'english': 'to be', 'pos': 'verb'},
        {'french': 'un|une', 'english': 'a/an', 'pos': 'article'},
        {'french': 'le monde', 'english': 'the world', 'pos': 'noun'},
        {'french': 'avoir', 'english': 'to have', 'pos': 'verb'},
        {'french': 'chat', 'english': 'cat', 'pos': 'noun'}
    ]
    
    matcher = WordMatcher(word_list)
    
    # Test sentences
    test_sentences = [
        "Je suis étudiant.",  # être conjugated
        "Il est un homme.",  # être + un
        "Le monde est beau.",  # le monde phrase
        "J'ai un chat.",  # avoir + un + chat
        "Une femme a deux chats."  # une + avoir + chat (plural)
    ]
    
    for sentence in test_sentences:
        print(f"\nSentence: {sentence}")
        found_indices = matcher.find_words_in_sentence(sentence)
        print(f"Found {len(found_indices)} words:")
        for idx in found_indices:
            word = word_list[idx]
            details = matcher.get_matching_details(word, sentence)
            print(f"  - {word['french']} ({details['match_type']}): {details['matched_form']}")
    
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == '__main__':
    test_matcher()