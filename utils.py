"""
Utility functions for contract processing
"""
import os
import re
import PyPDF2
import pdfplumber
from typing import List, Dict, Optional

def load_pdf_text(pdf_path: str) -> str:
    """
    Extract text from PDF file using multiple methods for robustness
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    text = ""
    
    # Try pdfplumber first (better for complex PDFs)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed for {pdf_path}: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e2:
            print(f"PyPDF2 also failed for {pdf_path}: {e2}")
            return ""
    
    return text


def load_text_file(txt_path: str) -> str:
    """
    Load text from a .txt file
    
    Args:
        txt_path: Path to text file
        
    Returns:
        File contents as string
    """
    try:
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {txt_path}: {e}")
        return ""


def normalize_text(text: str) -> str:
    """
    Normalize and clean contract text
    
    Args:
        text: Raw text from contract
        
    Returns:
        Cleaned and normalized text
    """
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove multiple newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')
    text = text.replace('\r', '\n')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def chunk_text(text: str, max_chunk_size: int = 100000) -> List[str]:
    """
    Split long text into smaller chunks for LLM processing
    Claude has a large context window, but we chunk for very long contracts
    
    Args:
        text: Full contract text
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    # If text is short enough, return as single chunk
    if len(text) <= max_chunk_size:
        return [text]
    
    # Split by paragraphs
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph would exceed limit, start new chunk
        if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def load_all_contracts(data_dir: str = "data/contracts") -> Dict[str, str]:
    """
    Load all contracts from the data directory
    
    Args:
        data_dir: Directory containing contract files
        
    Returns:
        Dictionary mapping contract_id to contract text
    """
    contracts = {}
    
    # Get all files in directory
    files = os.listdir(data_dir)
    
    for filename in sorted(files):
        filepath = os.path.join(data_dir, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        # Extract contract ID from filename
        contract_id = os.path.splitext(filename)[0]
        
        # Load based on file type
        if filename.endswith('.pdf'):
            text = load_pdf_text(filepath)
        elif filename.endswith('.txt'):
            text = load_text_file(filepath)
        else:
            print(f"Skipping unsupported file type: {filename}")
            continue
        
        # Normalize text
        if text:
            contracts[contract_id] = normalize_text(text)
            print(f"✓ Loaded {contract_id}: {len(text)} characters")
        else:
            print(f"✗ Failed to load {contract_id}")
    
    return contracts


def validate_contract_text(text: str, min_length: int = 100) -> bool:
    """
    Check if contract text is valid and meaningful
    
    Args:
        text: Contract text to validate
        min_length: Minimum acceptable length
        
    Returns:
        True if valid, False otherwise
    """
    if not text or len(text) < min_length:
        return False
    
    # Check if text has enough actual words (not just symbols)
    words = re.findall(r'\b\w+\b', text)
    if len(words) < 50:
        return False
    
    return True