"""
Quick test script to verify the matcher is working correctly
Run this after setup to ensure everything is configured properly
"""

from matcher import WordMatcher

def test_basic_matching():
    """Test basic word matching functionality"""
    print("=" * 60)
    print("Testing Word Matcher")
    print("=" * 60)
    print()
    
    # Sample word list
    word_list = [
        {'french': 'être', 'english': 'to be', 'pos': 'verb'},
        {'french': 'un|une', 'english': 'a/an', 'pos': 'article'},
        {'french': 'le monde', 'english': 'the world', 'pos': 'noun'},
        {'french': 'avoir', 'english': 'to have', 'pos': 'verb'},
        {'french': 'chat', 'english': 'cat', 'pos': 'noun'},
        {'french': 'maison', 'english': 'house', 'pos': 'noun'},
        {'french': 'aller', 'english': 'to go', 'pos': 'verb'},
        {'french': 'faire', 'english': 'to do/make', 'pos': 'verb'},
    ]
    
    print(f"Testing with {len(word_list)} sample words...")
    print()
    
    # Initialize matcher
    try:
        matcher = WordMatcher(word_list)
        print("✓ Matcher initialized successfully")
        print()
    except Exception as e:
        print(f"✗ Error initializing matcher: {e}")
        return False
    
    # Test sentences
    test_cases = [
        {
            'sentence': "Je suis un étudiant.",
            'expected': ['être', 'un|une'],
            'description': 'Verb conjugation + gender variation'
        },
        {
            'sentence': "Le monde est beau.",
            'expected': ['le monde', 'être'],
            'description': 'Multi-word phrase + verb'
        },
        {
            'sentence': "J'ai une maison et un chat.",
            'expected': ['avoir', 'un|une', 'maison', 'chat'],
            'description': 'Multiple matches'
        },
        {
            'sentence': "Nous allons faire quelque chose.",
            'expected': ['aller', 'faire'],
            'description': 'Multiple verb conjugations'
        },
        {
            'sentence': "Les chats sont dans la maison.",
            'expected': ['être', 'chat', 'maison'],
            'description': 'Plural forms'
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Sentence: {test['sentence']}")
        
        # Find matches
        found_indices = matcher.find_words_in_sentence(test['sentence'])
        found_words = [word_list[idx]['french'] for idx in found_indices]
        
        print(f"Expected: {test['expected']}")
        print(f"Found: {found_words}")
        
        # Check if all expected words were found
        all_found = all(word in found_words for word in test['expected'])
        
        if all_found:
            print("✓ PASS")
        else:
            print("✗ FAIL")
            all_passed = False
            
            # Show details for failed test
            for expected_word in test['expected']:
                if expected_word not in found_words:
                    print(f"  Missing: {expected_word}")
                    # Get matching details
                    word_data = next((w for w in word_list if w['french'] == expected_word), None)
                    if word_data:
                        details = matcher.get_matching_details(word_data, test['sentence'])
                        print(f"  Details: {details}")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("The matcher is working correctly.")
    else:
        print("✗ Some tests failed")
        print("Please check the spaCy model installation")
    print("=" * 60)
    
    return all_passed


def test_performance():
    """Test matching performance with larger dataset"""
    print()
    print("=" * 60)
    print("Performance Test")
    print("=" * 60)
    print()
    
    import time
    
    # Create larger word list
    word_list = [
        {'french': f'word{i}', 'english': f'word{i}', 'pos': 'noun'}
        for i in range(100)
    ]
    
    # Add some real French words
    word_list.extend([
        {'french': 'être', 'english': 'to be', 'pos': 'verb'},
        {'french': 'avoir', 'english': 'to have', 'pos': 'verb'},
        {'french': 'faire', 'english': 'to do', 'pos': 'verb'},
        {'french': 'aller', 'english': 'to go', 'pos': 'verb'},
    ])
    
    matcher = WordMatcher(word_list)
    
    # Test sentences
    sentences = [
        "Je suis un étudiant qui va faire quelque chose.",
        "Il a une maison dans le monde.",
        "Nous allons avoir un problème.",
    ] * 100  # 300 sentences total
    
    print(f"Testing {len(sentences)} sentences against {len(word_list)} words...")
    
    start_time = time.time()
    
    total_matches = 0
    for sentence in sentences:
        matches = matcher.find_words_in_sentence(sentence)
        total_matches += len(matches)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"✓ Processed {len(sentences)} sentences in {elapsed:.2f} seconds")
    print(f"  Average: {elapsed/len(sentences)*1000:.2f}ms per sentence")
    print(f"  Total matches found: {total_matches}")
    print()
    
    return True


if __name__ == '__main__':
    try:
        # Run basic tests
        success = test_basic_matching()
        
        if success:
            # Run performance test
            test_performance()
            
            print()
            print("=" * 60)
            print("✓ All tests completed successfully!")
            print("The system is ready to use.")
            print("=" * 60)
        else:
            print()
            print("Please ensure spaCy French model is installed:")
            print("python -m spacy download fr_core_news_lg")
    
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error running tests: {e}")
        print("=" * 60)
        print()
        print("Please run setup.bat to install all dependencies")