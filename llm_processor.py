"""
LLM-based contract processing using Claude API
"""
import os
import json
import time
from anthropic import Anthropic
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContractAnalyzer:
    """
    Handles LLM-based contract analysis using Claude
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the analyzer with Claude API
        
        Args:
            api_key: Anthropic API key (if None, reads from env)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
    def extract_clauses(self, contract_text: str) -> Dict[str, str]:
        """
        Extract specific clauses from contract using Claude
        
        Args:
            contract_text: Full text of the contract
            
        Returns:
            Dictionary with extracted clauses
        """
        prompt = f"""You are a legal contract analysis expert. Analyze the following contract and extract ONLY the following specific clauses:

1. **Termination Clause**: Any provisions about how and when the contract can be terminated, including notice periods, termination conditions, and termination rights.

2. **Confidentiality Clause**: Provisions regarding confidential information, non-disclosure obligations, and protection of proprietary information.

3. **Liability Clause**: Provisions regarding limitations of liability, indemnification, liability caps, and allocation of risk between parties.

For each clause type:
- If found, extract the EXACT relevant text from the contract (you may extract multiple sections if the clause appears in different parts)
- If NOT found, respond with "Not found in contract"
- Be precise and only extract text that directly relates to the clause type

Contract Text:
{contract_text}

Respond in the following JSON format:
{{
    "termination_clause": "extracted text or 'Not found in contract'",
    "confidentiality_clause": "extracted text or 'Not found in contract'",
    "liability_clause": "extracted text or 'Not found in contract'"
}}

Only return valid JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0,  # Deterministic for clause extraction
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Try to parse JSON from response
            # Sometimes Claude adds markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text.strip())
            
            return result
            
        except Exception as e:
            print(f"Error extracting clauses: {e}")
            return {
                "termination_clause": f"Error: {str(e)}",
                "confidentiality_clause": f"Error: {str(e)}",
                "liability_clause": f"Error: {str(e)}"
            }
    
    def generate_summary(self, contract_text: str) -> str:
        """
        Generate a concise summary of the contract
        
        Args:
            contract_text: Full text of the contract
            
        Returns:
            Summary string (100-150 words)
        """
        prompt = f"""You are a legal contract analysis expert. Provide a concise summary of this contract in exactly 100-150 words.

Your summary MUST include:
1. Purpose of the agreement
2. Key obligations of each party
3. Notable risks or penalties

Be specific and focus on the most important terms. Write in clear, professional language.

Contract Text:
{contract_text}

Summary (100-150 words):"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,  # Slightly creative for summarization
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = response.content[0].text.strip()
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def analyze_contract(self, contract_id: str, contract_text: str) -> Dict:
        """
        Complete analysis: extract clauses and generate summary
        
        Args:
            contract_id: Identifier for the contract
            contract_text: Full contract text
            
        Returns:
            Dictionary with all analysis results
        """
        print(f"\n{'='*60}")
        print(f"Analyzing contract: {contract_id}")
        print(f"{'='*60}")
        
        # Extract clauses
        print("Extracting clauses...")
        clauses = self.extract_clauses(contract_text)
        
        # Small delay to respect rate limits
        time.sleep(1)
        
        # Generate summary
        print("Generating summary...")
        summary = self.generate_summary(contract_text)
        
        # Small delay
        time.sleep(1)
        
        result = {
            'contract_id': contract_id,
            'summary': summary,
            'termination_clause': clauses.get('termination_clause', 'Not found'),
            'confidentiality_clause': clauses.get('confidentiality_clause', 'Not found'),
            'liability_clause': clauses.get('liability_clause', 'Not found')
        }
        
        print(f"✓ Analysis complete for {contract_id}")
        
        return result
    
    def batch_analyze(self, contracts: Dict[str, str], 
                     max_contracts: Optional[int] = None) -> list:
        """
        Analyze multiple contracts in batch
        
        Args:
            contracts: Dictionary mapping contract_id to contract_text
            max_contracts: Maximum number of contracts to process (None = all)
            
        Returns:
            List of analysis results
        """
        results = []
        
        # Limit number of contracts if specified
        contract_items = list(contracts.items())
        if max_contracts:
            contract_items = contract_items[:max_contracts]
        
        total = len(contract_items)
        print(f"\nStarting batch analysis of {total} contracts...")
        print("="*60)
        
        for idx, (contract_id, contract_text) in enumerate(contract_items, 1):
            print(f"\n[{idx}/{total}] Processing {contract_id}...")
            
            try:
                result = self.analyze_contract(contract_id, contract_text)
                results.append(result)
                
            except Exception as e:
                print(f"✗ Error analyzing {contract_id}: {e}")
                results.append({
                    'contract_id': contract_id,
                    'summary': f'Error: {str(e)}',
                    'termination_clause': 'Error',
                    'confidentiality_clause': 'Error',
                    'liability_clause': 'Error'
                })
        
        print(f"\n{'='*60}")
        print(f"✅ Batch analysis complete! Processed {len(results)} contracts")
        print(f"{'='*60}\n")
        
        return results