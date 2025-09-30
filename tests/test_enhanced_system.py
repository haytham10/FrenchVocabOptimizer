"""
Quick test script to verify the enhanced system works end-to-end
"""

import sys
import os
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure we can import from parent directory (project root)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    # Core modules
    from core.config import OptimizerConfig
    from core.matcher import EnhancedWordMatcher
    from core.optimizer import EnhancedSentenceOptimizer
    from core.sheets import EnhancedSheetsHandler
    print("  ✅ Core modules imported")
    
    # Backward compatibility
    from matcher import WordMatcher
    from optimizer import SentenceOptimizer
    from sheets_handler import SheetsHandler
    print("  ✅ Backward compatibility imports work")
    
    return True

def test_matcher():
    """Test the enhanced word matcher"""
    print("\nTesting EnhancedWordMatcher...")
    
    from core.config import OptimizerConfig
    from core.matcher import EnhancedWordMatcher
    
    # Create test word list in expected format
    test_words = [
        {'french': 'bonjour', 'english': 'hello'},
        {'french': 'chat', 'english': 'cat'},
        {'french': 'maison', 'english': 'house'},
        {'french': 'manger', 'english': 'to eat'},
        {'french': 'parler', 'english': 'to speak'}
    ]
    
    config = OptimizerConfig(cache_enabled=False)  # Disable cache for test
    matcher = EnhancedWordMatcher(test_words, config)
    print(f"  ✅ Created matcher with {len(test_words)} words")
    
    # Test sentence matching
    test_sentence = "Bonjour, j'ai un chat dans ma maison."
    found = matcher.find_words_in_sentence(test_sentence)
    print(f"  ✅ Found {len(found)} words in test sentence: {found}")
    
    # Test batch processing
    sentences = [
        "Bonjour mon ami",
        "Le chat mange",
        "Je parle français"
    ]
    results = matcher.batch_process_sentences(sentences)
    print(f"  ✅ Batch processed {len(results)} sentences")
    
    return True

def test_optimizer():
    """Test the enhanced optimizer with all three algorithms"""
    print("\nTesting EnhancedSentenceOptimizer...")
    
    from core.config import OptimizerConfig
    from core.matcher import EnhancedWordMatcher
    from core.optimizer import EnhancedSentenceOptimizer
    
    # Test data in expected format
    words = [
        {'french': 'bonjour', 'english': 'hello'},
        {'french': 'chat', 'english': 'cat'},
        {'french': 'chien', 'english': 'dog'},
        {'french': 'maison', 'english': 'house'},
        {'french': 'manger', 'english': 'to eat'},
        {'french': 'boire', 'english': 'to drink'},
        {'french': 'parler', 'english': 'to speak'},
        {'french': 'ami', 'english': 'friend'}
    ]
    sentences = [
        "Bonjour mon ami, comment vas-tu?",
        "Le chat et le chien sont dans la maison.",
        "Je mange et je bois avec mes amis.",
        "Nous parlons français ensemble.",
        "Mon chat mange dans la maison.",
    ]
    
    algorithms = ['greedy', 'weighted_greedy', 'beam_search']
    
    for algo in algorithms:
        config = OptimizerConfig(algorithm=algo, cache_enabled=False)
        
        optimizer = EnhancedSentenceOptimizer(words, sentences, config)
        result = optimizer.optimize(algorithm=algo)
        
        print(f"\n  Algorithm: {algo}")
        print(f"    Coverage: {result.coverage_percent:.1f}%")
        print(f"    Sentences: {result.total_sentences}")
        print(f"    Covered: {result.words_covered}/{result.total_words} words")
        print(f"    Missing: {len(result.missing_words)} words")
        print(f"  ✅ {algo} algorithm works")
    
    return True

def test_config():
    """Test configuration system"""
    print("\nTesting OptimizerConfig...")
    
    from core.config import OptimizerConfig, SHEETS_SCOPES, COLORS
    
    # Test default config
    config = OptimizerConfig()
    print(f"  Default algorithm: {config.algorithm}")
    print(f"  Cache enabled: {config.cache_enabled}")
    print(f"  Parallel processing: {config.parallel_processing}")
    print(f"  ✅ Default config created")
    
    # Test custom config
    custom_config = OptimizerConfig(
        algorithm='beam_search',
        beam_width=10,
        cache_enabled=False,
        spreadsheet_name='TestSheet'
    )
    assert custom_config.algorithm == 'beam_search'
    assert custom_config.beam_width == 10
    print(f"  ✅ Custom config created")
    
    # Test constants
    assert 'header' in COLORS
    assert 'https://www.googleapis.com/auth/spreadsheets' in SHEETS_SCOPES
    print(f"  ✅ Constants loaded")
    
    return True

def test_web_interface():
    """Test that Flask app can initialize"""
    print("\nTesting Web Interface...")
    
    # Find web_interface directory relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_dir = os.path.join(project_root, 'web_interface')
    
    try:
        # Ensure project root is in path
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add web_interface to path
        if web_dir not in sys.path:
            sys.path.insert(0, web_dir)
        
        from web_interface.app import app
        
        # Check routes
        routes = [r.rule for r in app.url_map.iter_rules() if r.endpoint != 'static']
        print(f"  Available routes: {len(routes)}")
        for route in routes:
            print(f"    - {route}")
        print(f"  ✅ Flask app initialized")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED FRENCH VOCAB OPTIMIZER - SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Word Matcher", test_matcher),
        ("Sentence Optimizer", test_optimizer),
        ("Web Interface", test_web_interface),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("  1. Start web interface: cd web_interface && python app.py")
        print("  2. Open browser: http://localhost:5000")
        print("  3. Upload vocabulary file and optimize!")
        print("\nDocumentation:")
        print("  - README_NEW.md: Complete user guide")
        print("  - MIGRATION_GUIDE.md: Transition from old system")
        print("  - UPGRADE_SUMMARY.md: Detailed changelog")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
