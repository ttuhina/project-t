"""
Few-shot learning examples for improved clause extraction
BONUS FEATURE
"""

# Example contracts and their correct clause extractions
# These help Claude understand exactly what we're looking for

FEW_SHOT_EXAMPLES = """
## Example 1:

Contract Text:
"This Agreement may be terminated by either party upon thirty (30) days written notice to the other party. Upon termination, all confidential information must be returned. Either party may terminate immediately for material breach."

Extracted Clauses:
{
    "termination_clause": "This Agreement may be terminated by either party upon thirty (30) days written notice to the other party. Either party may terminate immediately for material breach.",
    "confidentiality_clause": "Upon termination, all confidential information must be returned.",
    "liability_clause": "Not found in contract"
}

---

## Example 2:

Contract Text:
"The Receiving Party agrees to hold in confidence all Confidential Information and not to disclose such information to any third party without prior written consent. Neither party shall be liable for indirect, incidental, or consequential damages, and total liability under this agreement shall not exceed $100,000."

Extracted Clauses:
{
    "termination_clause": "Not found in contract",
    "confidentiality_clause": "The Receiving Party agrees to hold in confidence all Confidential Information and not to disclose such information to any third party without prior written consent.",
    "liability_clause": "Neither party shall be liable for indirect, incidental, or consequential damages, and total liability under this agreement shall not exceed $100,000."
}

---

## Example 3:

Contract Text:
"This Agreement shall remain in effect for one year and may be terminated by either party with 60 days notice. Company shall indemnify Client against any claims arising from Company's negligence. All proprietary information disclosed hereunder shall remain confidential for a period of 5 years."

Extracted Clauses:
{
    "termination_clause": "This Agreement shall remain in effect for one year and may be terminated by either party with 60 days notice.",
    "confidentiality_clause": "All proprietary information disclosed hereunder shall remain confidential for a period of 5 years.",
    "liability_clause": "Company shall indemnify Client against any claims arising from Company's negligence."
}
"""


def get_few_shot_clause_extraction_prompt(contract_text: str) -> str:
    """
    Create an enhanced prompt with few-shot examples
    
    Args:
        contract_text: The contract to analyze
        
    Returns:
        Complete prompt with examples
    """
    prompt = f"""You are a legal contract analysis expert. I will show you examples of how to extract specific clauses, then you will do the same for a new contract.

# EXAMPLES OF CORRECT EXTRACTION:

{FEW_SHOT_EXAMPLES}

# NOW EXTRACT CLAUSES FROM THIS NEW CONTRACT:

Your task is to extract these three clause types from the contract below:

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
    
    return prompt


# Summary examples for better performance
SUMMARY_EXAMPLES = """
## Example 1:

Contract: Software License Agreement between TechCorp (Licensor) and StartupCo (Licensee)

Summary:
"This Software License Agreement grants StartupCo a non-exclusive license to use TechCorp's analytics platform for $50,000 annually. StartupCo must maintain confidentiality of the software and cannot reverse-engineer it. TechCorp limits liability to the amount paid by StartupCo and excludes consequential damages. Either party may terminate with 30 days notice. Key risks include potential liability for unauthorized use and loss of access upon termination. StartupCo is prohibited from sublicensing the software to third parties."

---

## Example 2:

Contract: Master Services Agreement between Acme Consulting (Provider) and GlobalRetail (Client)

Summary:
"Acme Consulting agrees to provide strategic consulting services to GlobalRetail for a fee of $200/hour, with a minimum engagement of 100 hours monthly. GlobalRetail must provide necessary information and access to personnel. Acme may terminate for non-payment after 15 days notice. Both parties must protect each other's confidential information for three years post-termination. Liability is capped at fees paid in the prior six months. Risks include potential disputes over deliverable quality and payment obligations even if GlobalRetail cancels early without cause."
"""


def get_few_shot_summary_prompt(contract_text: str) -> str:
    """
    Create an enhanced prompt with few-shot examples for summarization
    
    Args:
        contract_text: The contract to summarize
        
    Returns:
        Complete prompt with examples
    """
    prompt = f"""You are a legal contract analysis expert. I will show you examples of high-quality contract summaries, then you will create one for a new contract.

# EXAMPLES OF EXCELLENT SUMMARIES:

{SUMMARY_EXAMPLES}

# NOW SUMMARIZE THIS NEW CONTRACT:

Provide a concise summary of this contract in exactly 100-150 words.

Your summary MUST include:
1. Purpose of the agreement (what is being provided/purchased)
2. Key obligations of each party (what each side must do)
3. Notable risks or penalties (what could go wrong, financial implications)

Be specific with names, numbers, and concrete terms. Write in clear, professional language.

Contract Text:
{contract_text}

Summary (100-150 words):"""
    
    return prompt