"""
Verification Script for Sovereign Fusion Layer

This script verifies that all critical components are properly set up and can be imported.
Run this before deploying to catch any import or configuration issues.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all critical imports work"""
    print("Testing imports...")
    
    try:
        # Core imports
        from app.models.rl_models import RLEpisode, RLReward, RLPolicy
        print("✓ RL models import OK")
        
        from app.schemas.sovereign import SovereignInferRequest, SovereignInferResponse
        print("✓ Schemas import OK")
        
        from app.services.ksml_processor import annotate_with_ksml
        print("✓ KSML processor import OK")
        
        from app.services.adapter_registry import load_registry, get_adapter_for_language
        print("✓ Adapter registry import OK")
        
        from app.services.prosody_mapper import generate_prosody_hint
        print("✓ Prosody mapper import OK")
        
        from app.services.rl_loop import process_lm_output, merge_episodes
        print("✓ RL loop import OK")
        
        from app.services.reward_manager import get_unified_rewards
        print("✓ Reward manager import OK")
        
        from app.services.metrics import calculate_bleu, calculate_rouge
        print("✓ Metrics import OK")
        
        from app.services.evaluation_engine import load_eval_card
        print("✓ Evaluation engine import OK")
        
        try:
            from app.services.sovereign_lm_core import is_model_loaded
            print("✓ LM core import OK")
        except ImportError as e:
            if "peft" in str(e):
                print("⚠ LM core import failed (peft not installed - install dependencies: pip install -r requirements.txt)")
            else:
                print(f"⚠ LM core import failed: {e}")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config_files():
    """Test that configuration files exist"""
    print("\nTesting configuration files...")
    
    base_path = Path(__file__).parent
    
    files_to_check = [
        ("adapters/registry.json", "Adapter registry"),
        ("data/prosody_mappings.json", "Prosody mappings"),
        ("eval_cards/ar.json", "Arabic eval card"),
    ]
    
    all_exist = True
    for file_path, name in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {name} exists: {full_path}")
        else:
            print(f"✗ {name} missing: {full_path}")
            all_exist = False
    
    # Check checkpoint info (optional - might not exist yet)
    checkpoint_path = base_path.parent / "checkpoint_info.pkl"
    if checkpoint_path.exists():
        print(f"✓ Checkpoint info exists: {checkpoint_path}")
    else:
        print(f"⚠ Checkpoint info not found: {checkpoint_path} (this is OK if model not set up yet)")
    
    return all_exist


def test_basic_functionality():
    """Test basic functionality without requiring model or database"""
    print("\nTesting basic functionality...")
    
    try:
        # Test KSML
        from app.services.ksml_processor import annotate_with_ksml
        result = annotate_with_ksml("What is math?", "en")
        assert "ksml_labels" in result
        print("✓ KSML processor works")
        
        # Test adapter registry
        from app.services.adapter_registry import load_registry, get_adapter_for_language
        registry = load_registry()
        assert "adapters" in registry
        adapter = get_adapter_for_language("ar")
        assert adapter is not None
        print("✓ Adapter registry works")
        
        # Test prosody mapper
        from app.services.prosody_mapper import generate_prosody_hint
        prosody = generate_prosody_hint("Hello", "ar", "educational")
        assert prosody is not None
        assert "prosody_hint" in prosody
        print("✓ Prosody mapper works")
        
        # Test metrics
        from app.services.metrics import calculate_bleu
        score = calculate_bleu("Hello", "Hello")
        assert "bleu" in score or "bleu_score" in score
        print("✓ Metrics work")
        
        # Test eval card
        from app.services.evaluation_engine import load_eval_card
        card = load_eval_card("ar")
        assert "test_cases" in card
        print("✓ Evaluation engine works")
        
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """Test that database models can be instantiated"""
    print("\nTesting database models...")
    
    try:
        from app.models.rl_models import RLEpisode, RLReward, RLPolicy
        
        # Test that models have required attributes
        assert hasattr(RLEpisode, '__tablename__')
        assert hasattr(RLReward, '__tablename__')
        assert hasattr(RLPolicy, '__tablename__')
        print("✓ Database models are properly defined")
        
        return True
    except Exception as e:
        print(f"✗ Database models test failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Sovereign Fusion Layer Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config Files", test_config_files()))
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("Database Models", test_database_models()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please fix issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

