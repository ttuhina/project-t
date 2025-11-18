"""
Script to download CUAD dataset from Hugging Face
"""
import os
from datasets import load_dataset
import shutil

def download_cuad_dataset():
    """Download CUAD dataset and save contracts locally"""
    
    print("Downloading CUAD dataset from Hugging Face...")
    
    # Load dataset
    dataset = load_dataset("theatticusproject/cuad")
    
    # Create output directory
    os.makedirs("data/contracts", exist_ok=True)
    
    # We'll work with the train split and take first 50 contracts
    train_data = dataset['train']
    
    print(f"Total contracts available: {len(train_data)}")
    print("Extracting first 50 contracts...")
    
    # Extract and save 50 contracts
    for i, item in enumerate(train_data):
        if i >= 50:
            break
        
        # Get contract text
        contract_text = item['context']
        contract_id = item['id']
        
        # Save as text file
        filename = f"data/contracts/contract_{i+1:03d}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(contract_text)
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1} contracts...")
    
    print(f"\n✅ Successfully downloaded 50 contracts to data/contracts/")
    print("You can now run the main processing script!")

if __name__ == "__main__":
    download_cuad_dataset()