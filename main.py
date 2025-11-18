"""
Main script for Legal Contract Analysis Pipeline
"""
import os
import json
import pandas as pd
from datetime import datetime
from utils import load_all_contracts, validate_contract_text
from llm_processor import ContractAnalyzer

def save_results(results: list, output_format: str = 'both'):
    """
    Save analysis results to CSV and/or JSON
    
    Args:
        results: List of contract analysis results
        output_format: 'csv', 'json', or 'both'
    """
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save as CSV
    if output_format in ['csv', 'both']:
        csv_path = f'outputs/contract_analysis_{timestamp}.csv'
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✓ Results saved to: {csv_path}")
    
    # Save as JSON
    if output_format in ['json', 'both']:
        json_path = f'outputs/contract_analysis_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ Results saved to: {json_path}")


def print_sample_result(result: dict):
    """
    Pretty print a single contract analysis result
    
    Args:
        result: Single contract analysis dictionary
    """
    print(f"\n{'='*80}")
    print(f"CONTRACT: {result['contract_id']}")
    print(f"{'='*80}")
    
    print(f"\n📝 SUMMARY:")
    print(f"{result['summary']}")
    
    print(f"\n⚖️ TERMINATION CLAUSE:")
    term_clause = result['termination_clause']
    if len(term_clause) > 300:
        print(f"{term_clause[:300]}...")
    else:
        print(f"{term_clause}")
    
    print(f"\n🔒 CONFIDENTIALITY CLAUSE:")
    conf_clause = result['confidentiality_clause']
    if len(conf_clause) > 300:
        print(f"{conf_clause[:300]}...")
    else:
        print(f"{conf_clause}")
    
    print(f"\n⚠️ LIABILITY CLAUSE:")
    liab_clause = result['liability_clause']
    if len(liab_clause) > 300:
        print(f"{liab_clause[:300]}...")
    else:
        print(f"{liab_clause}")
    
    print(f"\n{'='*80}\n")


def main():
    """
    Main execution function
    """
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        Legal Contract Analysis Pipeline with LLMs                ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    DATA_DIR = "data/contracts"
    MAX_CONTRACTS = 50  # Process first 50 contracts
    OUTPUT_FORMAT = 'both'  # 'csv', 'json', or 'both'
    
    # Step 1: Load contracts
    print("\n📂 Step 1: Loading contracts...")
    print("-" * 60)
    contracts = load_all_contracts(DATA_DIR)
    
    if not contracts:
        print("❌ Error: No contracts found in data/contracts/")
        print("Please run download_data.py first or add contract files manually.")
        return
    
    print(f"\n✅ Loaded {len(contracts)} contracts successfully!")
    
    # Validate contracts
    print("\n🔍 Validating contract data...")
    valid_contracts = {
        cid: text for cid, text in contracts.items() 
        if validate_contract_text(text)
    }
    
    if len(valid_contracts) < len(contracts):
        print(f"⚠️  Warning: {len(contracts) - len(valid_contracts)} contracts failed validation")
    
    print(f"✅ {len(valid_contracts)} valid contracts ready for analysis")
    
    # Step 2: Initialize LLM Analyzer
    print("\n🤖 Step 2: Initializing Claude API...")
    print("-" * 60)
    
    try:
        analyzer = ContractAnalyzer()
        print("✅ Claude API initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease ensure:")
        print("1. You have set ANTHROPIC_API_KEY in your .env file")
        print("2. Your API key is valid")
        return
    
    # Step 3: Analyze contracts
    print(f"\n⚙️  Step 3: Analyzing contracts...")
    print("-" * 60)
    print(f"Processing up to {MAX_CONTRACTS} contracts...")
    
    results = analyzer.batch_analyze(valid_contracts, max_contracts=MAX_CONTRACTS)
    
    # Step 4: Save results
    print(f"\n💾 Step 4: Saving results...")
    print("-" * 60)
    save_results(results, output_format=OUTPUT_FORMAT)
    
    # Step 5: Display sample results
    print(f"\n📊 Step 5: Sample Results")
    print("-" * 60)
    
    # Show first 2 results as examples
    for i, result in enumerate(results[:2]):
        print_sample_result(result)
        if i < 1:  # Only print separator between samples
            input("Press Enter to see next sample...")
    
    # Summary statistics
    print(f"\n📈 Analysis Summary:")
    print("-" * 60)
    print(f"Total contracts analyzed: {len(results)}")
    
    # Count successful extractions
    term_found = sum(1 for r in results if 'not found' not in r['termination_clause'].lower() 
                    and 'error' not in r['termination_clause'].lower())
    conf_found = sum(1 for r in results if 'not found' not in r['confidentiality_clause'].lower()
                    and 'error' not in r['confidentiality_clause'].lower())
    liab_found = sum(1 for r in results if 'not found' not in r['liability_clause'].lower()
                    and 'error' not in r['liability_clause'].lower())
    
    print(f"Termination clauses found: {term_found}/{len(results)}")
    print(f"Confidentiality clauses found: {conf_found}/{len(results)}")
    print(f"Liability clauses found: {liab_found}/{len(results)}")
    
    print(f"\n✅ Pipeline execution complete!")
    print(f"Check the 'outputs' folder for full results.\n")


if __name__ == "__main__":
    main()