# RAG Test Environment

## 📁 Directory Structure

```
rag_test/
├── test_scripts/           # Test scripts for Granite Docling
├── test_inputs/           # Symbolic links to test documents
│   ├── bitcoin.pdf        # → Bitcoin whitepaper
│   └── lightning_network.pdf # → Lightning Network paper
├── test_outputs/          # Test results storage
│   ├── docling_results/   # DocTags format outputs
│   ├── markdown_results/  # Markdown format outputs
│   └── quality_analysis/  # Quality evaluation reports
├── benchmarks/           # Performance benchmark data
├── test_reports/         # Test summary reports
└── README.md            # This file
```

## 🎯 Testing Phases

### Phase 1: Environment Verification
- Import tests and GPU validation
- Model loading verification

### Phase 2: Bitcoin Whitepaper Testing
- Formula extraction accuracy
- Structure preservation
- Chapter hierarchy maintenance

### Phase 3: Lightning Network Paper Testing
- Complex diagram parsing
- Table structure extraction
- Multi-column layout handling

### Phase 4: Output Format Comparison
- DocTags vs Markdown quality
- Information retention analysis
- LLM readability assessment

### Phase 5: RAG Integration Readiness
- Semantic chunking preparation
- Vector embedding readiness
- Pipeline optimization recommendations

## 🚀 Usage

Run tests from the `test_scripts/` directory. All outputs will be organized in `test_outputs/` for easy analysis and comparison.