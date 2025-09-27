# Milo_Bitcoin 🐱₿

> A conversational Bitcoin analysis assistant powered by RAG + Fine-tuned LLM - Featuring Milo, the smartest crypto cat on the internet!

**Author**: Norton Gu | University of Rochester '25
**Status**: 🔨 In Development (Milo is studying the blockchain!)
**Tech Stack**: Python, ChromaDB, GPT-OSS-20B, vLLM, LoRA, Real-time APIs

## 🎯 Project Vision

Building the world's first **conversational Bitcoin assistant** that combines:
- **Real-time Bitcoin data**: Price, on-chain metrics, sentiment analysis
- **Educational AI**: Explains complex Bitcoin concepts in simple terms
- **RAG system**: Retrieval-augmented generation with Bitcoin knowledge base
- **Fine-tuned LLM**: Specialized for Bitcoin analysis and education
- **Milo's personality**: Friendly cat who happens to understand blockchain! 🐾

## ✨ Key Features

- 🤖 **Conversational Interface**: Chat naturally about Bitcoin topics
- 📊 **Real-time Analysis**: Live market data and on-chain metrics
- 📚 **Educational Focus**: Explains concepts from basics to advanced
- ⚠️ **Risk Awareness**: Always emphasizes education over speculation
- 🔍 **Smart Context**: RAG-powered responses with current data
- 😸 **Milo's Wisdom**: Surprisingly insightful for a cat!

## 🛠️ Technical Architecture

### 🏗️ Parallel Development Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│   Track A: RAG      │    │   Track B: LLM      │
│   Knowledge System  │    │   Intelligence      │
│                     │    │                     │
│ Data Sources:       │    │ Data Sources:       │
│ • Bitcoin PDFs ✅   │    │ • HuggingFace       │
│ • Academic Papers ✅│    │   Datasets          │
│ • Bitcoin.org       │    │ • News Analysis     │
│ • Wiki Content      │    │ • Market Data       │
│                     │    │ • Expert Dialogue   │
│ Processing:         │    │                     │
│ • Granite Docling ✅│    │ Training:           │
│ • Document Chunking │    │ • GPT-OSS-20B      │
│ • ChromaDB          │    │ • LoRA Fine-tuning │
│ • Embeddings        │    │ • vLLM Serving     │
└─────────────────────┘    └─────────────────────┘
            │                          │
            └──────────┬─────────────────┘
                       ▼
         ┌─────────────────────────┐
         │    Integration Layer    │
         │                         │
         │ • Context Fusion        │
         │ • Response Generation   │
         │ • Real-time Data        │
         │ • Milo Personality      │
         └─────────────────────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   User Interface    │
            │                     │
            │ • Gradio Frontend   │
            │ • Chat Interface    │
            │ • Visualizations    │
            └─────────────────────┘
```

### 🎯 Independent Development Benefits

**Parallel Processing Pipeline:**
```
PDF Documents ────────────┐
                          ├──► Document Processing ──► RAG Database
Bitcoin.org/Wiki ─────────┘

HuggingFace Datasets ─────────► Model Training ──► Fine-tuned LLM

                     ┌── RAG Knowledge
Integration Layer ───┤
                     └── LLM Analysis ──► Enhanced Responses
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/futurespyhi/Milo_Bitcoin.git
cd Milo_Bitcoin

# Install dependencies
conda env create -f environment.yml
conda activate milo_bitcoin

# OR using pip directly
# pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_key"  # for embeddings (optional)
# Note: Most functionality works without API keys for local inference

# Wake up Milo and start chatting!
python milo_bitcoin_main.py
```

## 💬 Example Conversations

```
🙋 User: "What's Bitcoin's current price?"
🐱 Milo: "Current Bitcoin price is $112,148! The market sentiment
         is showing 43/100 on Fear & Greed (fearful territory).
         Network activity is strong with 481k transactions today! 🐾"

🙋 User: "Should I buy Bitcoin?"
🐱 Milo: "I can't give investment advice, but I can help you understand
         Bitcoin better! Remember: only invest what you can afford to
         lose completely. Want me to explain dollar-cost averaging? 🐾"

🙋 User: "Explain Bitcoin halving"
🐱 Milo: "Bitcoin halving is like reducing the treat supply! Every ~4 years
         (precisely every 210,000 blocks), mining rewards are cut in half.

         📚 From Satoshi's design: This controls Bitcoin's inflation rate
         📊 Historical halvings: 2012 (50→25), 2016 (25→12.5), 2020 (12.5→6.25), 2024 (6.25→3.125)
         📈 Market impact: Reduced supply often creates upward price pressure

         Current network shows strong fundamentals with high transaction volume! 🐾"
```

## 📊 Data Strategy

### RAG Knowledge Base (Authoritative Sources)
- **Bitcoin Whitepaper**: Satoshi Nakamoto's foundational paper - core concepts and principles
- **Bitcoin.org Documentation**: Official technical specifications and developer guides
- **Bitcoin Wiki**: Comprehensive terminology, explanations, and historical context
- **Academic Research**: Peer-reviewed papers on Bitcoin technology and economics

### Real-time Data Sources
- **Price Data**: CoinGecko API (real-time pricing and market cap)
- **On-chain Metrics**: Blockchain.info (hash rate, transactions, fees)
- **Market Sentiment**: Alternative.me Fear & Greed Index
- **News Analysis**: NewsAPI (Bitcoin-related articles)

### Fine-tuning Datasets (HuggingFace - tahamajs)
- **News Analysis**: 49.2k Bitcoin news sentiment analysis samples
- **Technical Predictions**: 2.46k market analysis and forecasting data
- **Professional Dialogue**: 2.3k expert-level conversation patterns

**Key Principle**: RAG provides authoritative knowledge foundation, fine-tuning enables professional analysis capabilities.

## 🧠 AI Architecture

### Fine-tuning Strategy
- **Base Model**: GPT-OSS-20B (OpenAI's 20B parameter open-source model)
- **Method**: LoRA fine-tuning for efficient training on dual RTX 5090 setup
- **Training Data**: HuggingFace Bitcoin datasets (separate from RAG knowledge)
- **Deployment**: vLLM for optimized inference and API serving
- **Focus**: Professional analysis, market insights, and conversational ability

### RAG Implementation
- **Vector Database**: ChromaDB for local, efficient Bitcoin knowledge storage
- **Embeddings**: sentence-transformers for privacy-friendly local inference
- **Knowledge Sources**: Authoritative Bitcoin documentation and research
- **Retrieval Strategy**: Semantic search with real-time data integration
- **Context Fusion**: Combines retrieved knowledge with live market data

### Data Separation Philosophy
```
RAG Knowledge Base ──────┐
                         ├──► Enhanced Context ──┐
Real-time Data ──────────┘                       │
                                                  ├──► Milo's Response
Fine-tuned Model ────────────► Professional Analysis ──┘
```

## 📈 Development Roadmap

### ✅ Current Progress (2025-09-27)
- [x] Project architecture design and technical planning
- [x] PDF document processing pipeline (granite_docling integration)
- [x] Single-GPU batch processing system for sequential PDF processing
- [x] Document quality assessment framework with automatic scoring
- [x] Bitcoin whitepaper and Lightning Network paper processing (86.8/100 & 88.5/100 quality scores)
- [x] Production-ready scripts architecture with proper error handling

### 🔄 Parallel Development Tracks

#### Track A: RAG Foundation 🏗️
- [x] Document processing pipeline (PDF → Markdown) ✅
- [ ] Document chunking and semantic segmentation
- [ ] ChromaDB vector database implementation
- [ ] Sentence-transformers embedding system
- [ ] RAG retrieval and context fusion
- [ ] Bitcoin.org and Wiki content collection
- [ ] Basic Gradio frontend for RAG validation

#### Track B: Model Intelligence 🧠
- [ ] HuggingFace Bitcoin datasets collection (tahamajs)
- [ ] Dataset preprocessing and quality validation
- [ ] GPT-OSS-20B LoRA fine-tuning preparation
- [ ] Training pipeline setup for dual RTX 5090
- [ ] vLLM deployment configuration and optimization

### Stage 3: System Integration 🔗
- [ ] RAG + Fine-tuned model integration testing
- [ ] Multi-modal response generation (Knowledge + Analysis)
- [ ] Performance optimization and response time improvement
- [ ] Enhanced Gradio interface with chat history and visualizations

### Stage 4: Production & Growth 🚀
- [ ] Docker containerization for consistent deployment
- [ ] Cloud deployment with scalable infrastructure
- [ ] Open-source community engagement
- [ ] Educational content creation and tutorials
- [ ] User feedback integration and feature expansion
- [ ] Academic collaboration and research publication

## ⚠️ Important Disclaimers

**Milo provides educational analysis only - NOT financial advice!**

- 🚨 Cryptocurrency investments are extremely high-risk
- 📚 Always do your own research (DYOR)
- 💰 Only invest what you can afford to lose completely
- 🏦 Consult qualified financial advisors for investment decisions
- 📖 This tool is for educational and informational purposes only

## 🤝 Contributing

This project is part of my journey to become an ML Engineer specializing in AI applications. Contributions, feedback, and suggestions are welcome!

### Ways to Contribute:
- 🐛 Report bugs or suggest improvements
- 📝 Add Bitcoin educational content
- 🔧 Improve code efficiency
- 📊 Enhance data analysis features
- 🎨 UI/UX improvements

## 🌟 Why This Project Matters

1. **Education First**: Demystifies Bitcoin for newcomers
2. **Risk Awareness**: Promotes responsible cryptocurrency understanding
3. **AI Innovation**: Combines LLM fine-tuning with real-time data
4. **Open Source**: Contributes to the AI and crypto communities
5. **Practical Application**: Solves real-world information needs

## 📝 License

MIT License - feel free to use this for learning and educational purposes!

## 🔗 Connect & Follow

**⭐ Star this repo if Milo helps you understand Bitcoin better!**
**🐱 Follow Milo's journey**: [LinkedIn](https://www.linkedin.com/in/norton-gu-322737278/) | [Twitter](https://x.com/bridge_cro_hi)

---

*Building the future of AI-powered crypto education, one meow at a time* 🐾₿

## 🏷️ Tags

`#Bitcoin` `#AI` `#LLM` `#RAG` `#FinTech` `#Education` `#Cryptocurrency` `#MachineLearning` `#OpenSource` `#BuildInPublic`