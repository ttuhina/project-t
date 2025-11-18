flowchart TD
    Start([Start Pipeline]) --> LoadData[Load Contracts from data/contracts/]
    
    LoadData --> CheckFiles{Files Found?}
    CheckFiles -->|No| Error1[Error: No contracts found]
    CheckFiles -->|Yes| ExtractText[Extract Text from PDF/TXT]
    
    ExtractText --> Normalize[Normalize & Clean Text]
    Normalize --> Validate{Valid Contract?}
    
    Validate -->|No| Skip[Skip Contract]
    Validate -->|Yes| SendClaude[Send to Claude API]
    
    SendClaude --> ExtractClauses[Extract Clauses]
    ExtractClauses --> Term[Termination Clause]
    ExtractClauses --> Conf[Confidentiality Clause]
    ExtractClauses --> Liab[Liability Clause]
    
    Term --> Summary[Generate Summary]
    Conf --> Summary
    Liab --> Summary
    
    Summary --> Store[Store Results]
    Store --> MoreContracts{More Contracts?}
    
    MoreContracts -->|Yes| SendClaude
    MoreContracts -->|No| SaveResults[Save to CSV & JSON]
    
    SaveResults --> BonusFeature{Enable Semantic Search?}
    
    BonusFeature -->|Yes| Embeddings[Generate Embeddings]
    Embeddings --> BuildIndex[Build FAISS Index]
    BuildIndex --> SearchReady[Semantic Search Ready]
    
    BonusFeature -->|No| Complete
    SearchReady --> Complete
    
    Complete([Pipeline Complete])
    
    Skip --> MoreContracts
    Error1 --> End([End])
    
    style Start fill:#90EE90
    style Complete fill:#90EE90
    style SendClaude fill:#FFD700
    style Embeddings fill:#87CEEB
    style BuildIndex fill:#87CEEB
    style Error1 fill:#FFB6C1