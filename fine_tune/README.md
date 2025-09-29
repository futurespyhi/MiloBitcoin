# Milo Bitcoin Fine-tuning Module 🐱⚡

> Track B: LLM Intelligence - Fine-tuning GPT-OSS-20B for professional Bitcoin quantitative analysis

## 🏗️ Modular Architecture

This project adopts a modular design with three independent modules:

### 📊 Current Module Status
- ✅ **fine_tune/** - LLM Fine-tuning Module (Python 3.11)
  - Status: ✅ Training completed, 122MB LoRA weights saved
  - Dependencies: unsloth 2025.9.9 + pytorch 2.8.0+cu128

- ✅ **rag_test/** - RAG Knowledge System (Python 3.10)
  - Status: ✅ granite-docling integration complete, document processing pipeline ready
  - Dependencies: docling + granite + embedding models

- 🔄 **[Planned] vllm/** - Inference Service Module
  - Status: Next development target
  - Dependencies: vllm + fastapi + model deployment tools

### 🔗 Module Collaboration Flow
```
fine_tune (LoRA weights) → vllm (inference service) ← rag_test (knowledge retrieval)
                            ↓
                    Unified JSON output format
```

## 🎯 Objective

Fine-tune GPT-OSS-20B into a professional Bitcoin quantitative analyst that outputs structured JSON-formatted trading recommendations.

## 🏗️ Directory Structure

```
fine_tune/
├── pyproject.toml              # RTX 5090 environment configuration
├── README.md                   # This file
├── data_preparation/           # Data preprocessing
│   ├── download_datasets.py    # Download HuggingFace datasets
│   ├── data_formatter.py       # Unified data formatting
│   └── data_mixer.py           # 90%-7%-3% data mixing
├── training_scripts/           # Training scripts
│   ├── unsloth_trainer.py      # Main training script
│   ├── config.yaml             # Training configuration
│   └── monitor.py              # Training monitoring
├── model_export/               # Model export
│   ├── export_for_vllm.py      # Export vLLM compatible format
│   └── model_validator.py      # Model validation
├── configs/                    # Configuration files
├── logs/                       # Training logs
└── checkpoints/                # Model checkpoints
```

## 🚀 Quick Start

### 1. Install Fine-tune Module Dependencies

```bash
# Set RTX 5090 environment variables
export TORCH_CUDA_ARCH_LIST="12.0"
export CUDA_VISIBLE_DEVICES=0

# LLM fine-tuning module (this module)
cd fine_tune
source .venv/bin/activate
uv sync  # Install fine-tuning dependencies (unsloth + pytorch + transformers)
```

### 2. Install RAG Module Dependencies (Parallel Development)

```bash
# RAG knowledge system module
cd rag_test
source .venv/bin/activate
uv sync  # Install RAG dependencies (granite-docling + embedding)
```

### 3. Verify RTX 5090 Support

```bash
python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'Device Name: {torch.cuda.get_device_name()}')
print(f'Device Capability: {torch.cuda.get_device_capability()}')
print(f'Memory: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB')
"
```

Expected output:
```
CUDA Available: True
Device Name: NVIDIA GeForce RTX 5090
Device Capability: (12, 0)
Memory: 32.6GB
```

### 4. Data Preparation (✅ Completed)

```bash
# ✅ Dataset downloaded and preprocessed
# final_data/ directory contains:
# - train.jsonl: 6,239 samples (85% train split)
# - validation.jsonl: 734 samples (10% validation split)
# - test.jsonl: 368 samples (5% test split)
# - Total: 7,341 samples
```

### 5. Fine-tuning Training (✅ Completed)

```bash
# ✅ Training completed - using the following script
python training_scripts/simple_trainer.py

# ✅ Training results:
# - Training time: 1.65 hours (3 epochs)
# - LoRA weights: 122MB (checkpoints/adapter_model.safetensors)
# - Loss convergence: 1.32 → 1.25
# - WandB monitoring: Complete training process recorded
```

## 📊 Dataset Strategy

Based on session log analysis results:

### Selected Datasets
1. **bitcoin-llm-finetuning-dataset_new**: 2,301 samples (99.3% high quality)
2. **bitcoin-sllm-instruct_v2**: 4,290 samples (99.9% high quality)

### Data Mix Ratio
- **90% Bitcoin professional data**: 6,607 samples - Core professional capability
- **7% Math reasoning data**: 514 samples - Computational ability preservation
- **3% Logic reasoning data**: 220 samples - Basic reasoning capability

### Target Output Format
```json
{
  "action": "BUY|SELL|HOLD",
  "confidence": 72,
  "current_price": 109453.00,
  "stop_loss": 105200.00,
  "take_profit": 116800.00,
  "forecast_10d": [109800, 111200, ...],
  "analysis": "Technical analysis text",
  "risk_score": 0.31,
  "technical_indicators": {...}
}
```

## ⚙️ Training Configuration

### Actual Training Configuration (Verified Successful)
```yaml
# ✅ Successfully used configuration
model_name: "openai/gpt-oss-20b"  # Actual model used
max_seq_length: 2048

# LoRA parameters (actual successful configuration)
lora_r: 64                    # rank
lora_alpha: 128               # 2*r ratio
lora_dropout: 0.1
target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]

# Training parameters (actually used)
per_device_train_batch_size: 4
gradient_accumulation_steps: 8
learning_rate: 2e-4           # Successful learning rate
num_train_epochs: 3
warmup_steps: 100

# Memory optimization
gradient_checkpointing: "unsloth"  # Unsloth optimization
optim: "adamw_8bit"
fp16: true
dataloader_pin_memory: false

# Actual dependency versions
software_versions:
  unsloth: "2025.9.9"
  torch: "2.8.0+cu128"
  transformers: "4.56.2"
  peft: "0.17.1"
```

## 📈 Actual Performance Results

### ✅ Training Performance (RTX 5090)
- **Total Training Time**: 1.65 hours (3 epochs) - 7x faster than expected!
- **Training Speed**: 3.145 samples/second
- **Checkpoint Saving**: Every 200 steps (checkpoint-200, 400, 585)
- **Memory Efficiency**: Better than expected, RTX 5090 performance more than sufficient

### ✅ Model Size
- **LoRA Weights**: 122MB (vs base model ~20GB)
- **Compression Ratio**: 99.4% parameter reduction
- **Total Checkpoints Size**: 779MB (includes 3 checkpoints)
- **Deployment Files**: Only 149MB (production environment)

## 🔗 Integration with Main Framework

After training completion, the model will be integrated into:
```
Milo_Bitcoin/
├── milo_bitcoin_main.py      # Main framework - replace TODO model
├── fine_tune/                # This directory
├── rag_test/                 # RAG knowledge system (parallel development)
└── vllm/                     # Integration deployment (planned)
```

## 🚨 Troubleshooting

### Common Issues

1. **sm_120 Not Supported Error**
```bash
# Ensure using CUDA 12.8, not 13.0
pip install torch --extra-index-url https://download.pytorch.org/whl/cu128
export TORCH_CUDA_ARCH_LIST="12.0"
```

2. **Out of Memory**
```bash
# Reduce batch size
per_device_train_batch_size: 2
gradient_accumulation_steps: 16
```

3. **Unsloth Installation Issues**
```bash
# Reinstall
pip uninstall unsloth -y
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

## 📝 Project Progress

### ✅ Completed Tasks
1. ✅ Directory structure created
2. ✅ PyTorch sm_120 compatibility verified (CUDA 12.8 + RTX 5090)
3. ✅ Training environment configured (pyproject.toml fixed)
4. ✅ Dataset downloaded and preprocessed (7,341 total samples: 6,239 train + 734 val + 368 test)
5. ✅ GPT-OSS-20B LoRA fine-tuning completed (122MB weights)
6. ✅ Training monitoring and checkpoint saving
7. ✅ Model published on HuggingFace: [HugMilo/milo-bitcoin-gpt-oss-20b-lora-v1](https://huggingface.co/HugMilo/milo-bitcoin-gpt-oss-20b-lora-v1)

### 🔄 Current Tasks (Next Steps)
8. 🔄 **Model Quality Evaluation** - Inference testing and performance validation
9. ⏸️ **vLLM Deployment Configuration** - Inference server setup
10. ⏸️ **Integration with Main Framework** - Unified API interface design

### 🎯 Modular Integration Plan
- **fine_tune** (this module): ✅ Training completed
- **rag_test**: ✅ Document processing pipeline ready
- **vllm** (planned): Inference service and module integration

---

**Remember**: This is Track B (LLM Fine-tuning) of parallel development, independent from Track A (RAG System), converging at the integration layer. 🚀