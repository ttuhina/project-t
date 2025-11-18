"""
Semantic search over contract clauses using embeddings
BONUS FEATURE
"""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Tuple
import pickle
import os

class SemanticClauseSearch:
    """
    Enables semantic search over extracted contract clauses
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize semantic search with embedding model
        
        Args:
            model_name: HuggingFace model for embeddings
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.clauses = []
        self.metadata = []
        
    def build_index(self, analysis_results: List[Dict]):
        """
        Build FAISS index from contract analysis results
        
        Args:
            analysis_results: List of contract analysis dictionaries
        """
        print("\nBuilding semantic search index...")
        
        # Extract all clauses with metadata
        all_clauses = []
        all_metadata = []
        
        for result in analysis_results:
            contract_id = result['contract_id']
            
            # Add termination clause
            if result['termination_clause'] and 'not found' not in result['termination_clause'].lower():
                all_clauses.append(result['termination_clause'])
                all_metadata.append({
                    'contract_id': contract_id,
                    'clause_type': 'termination',
                    'text': result['termination_clause']
                })
            
            # Add confidentiality clause
            if result['confidentiality_clause'] and 'not found' not in result['confidentiality_clause'].lower():
                all_clauses.append(result['confidentiality_clause'])
                all_metadata.append({
                    'contract_id': contract_id,
                    'clause_type': 'confidentiality',
                    'text': result['confidentiality_clause']
                })
            
            # Add liability clause
            if result['liability_clause'] and 'not found' not in result['liability_clause'].lower():
                all_clauses.append(result['liability_clause'])
                all_metadata.append({
                    'contract_id': contract_id,
                    'clause_type': 'liability',
                    'text': result['liability_clause']
                })
        
        if not all_clauses:
            print("⚠️  No clauses found to index!")
            return
        
        self.clauses = all_clauses
        self.metadata = all_metadata
        
        # Generate embeddings
        print(f"Generating embeddings for {len(all_clauses)} clauses...")
        embeddings = self.model.encode(all_clauses, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ Index built with {len(all_clauses)} clauses!")
        
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar clauses using semantic similarity
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search in index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))
        
        return results
    
    def save_index(self, path: str = "outputs/semantic_index"):
        """
        Save the index and metadata to disk
        
        Args:
            path: Base path for saving files
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save metadata
        with open(f"{path}_metadata.pkl", 'wb') as f:
            pickle.dump({
                'clauses': self.clauses,
                'metadata': self.metadata
            }, f)
        
        print(f"✅ Index saved to {path}")
    
    def load_index(self, path: str = "outputs/semantic_index"):
        """
        Load the index and metadata from disk
        
        Args:
            path: Base path for loading files
        """
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.faiss")
        
        # Load metadata
        with open(f"{path}_metadata.pkl", 'rb') as f:
            data = pickle.load(f)
            self.clauses = data['clauses']
            self.metadata = data['metadata']
        
        print(f"✅ Index loaded from {path}")


def demo_semantic_search(results_path: str):
    """
    Demo function to show semantic search capabilities
    
    Args:
        results_path: Path to JSON results file
    """
    import json
    
    print("\n" + "="*60)
    print("SEMANTIC SEARCH DEMO")
    print("="*60)
    
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Initialize and build index
    search_engine = SemanticClauseSearch()
    search_engine.build_index(results)
    
    # Save index for future use
    search_engine.save_index()
    
    # Example searches
    example_queries = [
        "contract cancellation and notice period",
        "protection of confidential information",
        "limitation of damages and liability cap"
    ]
    
    print("\n" + "="*60)
    print("EXAMPLE SEARCHES")
    print("="*60)
    
    for query in example_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 60)
        
        results = search_engine.search(query, top_k=3)
        
        for i, (metadata, score) in enumerate(results, 1):
            print(f"\n{i}. Contract: {metadata['contract_id']}")
            print(f"   Type: {metadata['clause_type']}")
            print(f"   Similarity Score: {score:.4f}")
            print(f"   Text: {metadata['text'][:200]}...")
        
        input("\nPress Enter for next query...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        demo_semantic_search(results_file)
    else:
        print("Usage: python semantic_search.py <path_to_results.json>")
        print("\nExample:")
        print("python semantic_search.py outputs/contract_analysis_20240101_120000.json")