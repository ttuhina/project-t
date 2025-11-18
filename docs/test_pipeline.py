"""
Testing and validation script for the contract analysis pipeline
"""
import os
import json
from utils import load_text_file, normalize_text, validate_contract_text
from llm_processor import ContractAnalyzer

def test_text_processing():
    """Test text processing utilities"""
    print("\n" + "="*60)
    print("TEST 1: Text Processing Utilities")
    print("="*60)
    
    # Test normalization
    test_text = "This   is   a    test\n\n\n\nwith multiple    spaces"
    normalized = normalize_text(test_text)
    
    assert "  " not in normalized, "Failed: Multiple spaces not removed"
    assert "\n\n\n" not in normalized, "Failed: Multiple newlines not removed"
    print("✅ Text normalization working correctly")
    
    # Test validation
    assert validate_contract_text("a" * 200), "Failed: Valid text rejected"
    assert not validate_contract_text("short"), "Failed: Invalid text accepted"
    print("✅ Text validation working correctly")
    
    print("\n✅ All text processing tests passed!")


def test_llm_connection():
    """Test Claude API connection"""
    print("\n" + "="*60)
    print("TEST 2: LLM API Connection")
    print("="*60)
    
    try:
        analyzer = ContractAnalyzer()
        print("✅ API key loaded successfully")
        
        # Test with a simple contract
        test_contract = """
        MASTER SERVICE AGREEMENT
        
        This agreement may be terminated by either party with 30 days written notice.
        
        All confidential information shared under this agreement shall remain confidential
        for a period of 5 years.
        
        Neither party shall be liable for indirect or consequential damages exceeding
        the total fees paid under this agreement.
        """
        
        print("\nTesting clause extraction...")
        result = analyzer.extract_clauses(test_contract)
        
        assert 'termination_clause' in result, "Missing termination clause"
        assert 'confidentiality_clause' in result, "Missing confidentiality clause"
        assert 'liability_clause' in result, "Missing liability clause"
        
        print("✅ Clause extraction working")
        print(f"   - Termination: {'Found' if 'not found' not in result['termination_clause'].lower() else 'Not found'}")
        print(f"   - Confidentiality: {'Found' if 'not found' not in result['confidentiality_clause'].lower() else 'Not found'}")
        print(f"   - Liability: {'Found' if 'not found' not in result['liability_clause'].lower() else 'Not found'}")
        
        print("\nTesting summary generation...")
        summary = analyzer.generate_summary(test_contract)
        
        assert len(summary) > 50, "Summary too short"
        print("✅ Summary generation working")
        print(f"   Summary length: {len(summary)} characters")
        
        print("\n✅ All LLM tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def test_output_format():
    """Test output file generation"""
    print("\n" + "="*60)
    print("TEST 3: Output Format Validation")
    print("="*60)
    
    # Check if outputs directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        print("✅ Created outputs directory")
    
    # Create sample result
    sample_result = {
        'contract_id': 'test_contract',
        'summary': 'This is a test summary of the contract.',
        'termination_clause': 'Test termination clause',
        'confidentiality_clause': 'Test confidentiality clause',
        'liability_clause': 'Test liability clause'
    }
    
    # Test JSON output
    test_json_path = 'outputs/test_output.json'
    with open(test_json_path, 'w') as f:
        json.dump([sample_result], f, indent=2)
    
    # Verify file was created
    assert os.path.exists(test_json_path), "JSON file not created"
    print("✅ JSON output format working")
    
    # Clean up
    os.remove(test_json_path)
    
    print("\n✅ All output format tests passed!")


def test_data_directory():
    """Test data directory structure"""
    print("\n" + "="*60)
    print("TEST 4: Data Directory Structure")
    print("="*60)
    
    # Check directory structure
    required_dirs = ['data/contracts', 'outputs']
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            print(f"⚠️  {dir_path} missing - creating it")
            os.makedirs(dir_path, exist_ok=True)
    
    # Check for contracts
    contract_files = [f for f in os.listdir('data/contracts') 
                     if f.endswith(('.pdf', '.txt'))]
    
    if contract_files:
        print(f"✅ Found {len(contract_files)} contract files")
        print(f"   Sample files: {contract_files[:3]}")
    else:
        print("⚠️  No contract files found in data/contracts/")
        print("   Run 'python download_data.py' to download CUAD dataset")
    
    print("\n✅ Data directory structure validated!")


def run_all_tests():
    """Run all validation tests"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║          Contract Analysis Pipeline - Test Suite                 ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Data Directory", test_data_directory),
        ("Text Processing", test_text_processing),
        ("Output Format", test_output_format),
        ("LLM Connection", test_llm_connection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} test failed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your pipeline is ready to run.")
        print("Execute: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running the pipeline.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()