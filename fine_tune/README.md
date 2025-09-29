# Milo Bitcoin Fine-tuning Module 🐱⚡

> Track B: LLM Intelligence - Fine-tuning GPT-OSS-20B for professional Bitcoin quantitative analysis

## 🏗️ 模块化架构

本项目采用模块化设计，分为三个独立模块：

### 📊 当前模块状态
- ✅ **fine_tune/** - LLM微调模块 (Python 3.11)
  - 状态：✅ 训练完成，122MB LoRA权重已保存
  - 依赖：unsloth 2025.9.9 + pytorch 2.8.0+cu128

- ✅ **rag_test/** - RAG知识系统 (Python 3.10)
  - 状态：✅ granite-docling集成完成，文档处理pipeline就绪
  - 依赖：docling + granite + embedding模型

- 🔄 **[计划] vllm/** - 推理服务模块
  - 状态：下一步开发目标
  - 依赖：vllm + fastapi + 模型部署工具

### 🔗 模块协作流程
```
fine_tune (LoRA权重) → vllm (推理服务) ← rag_test (知识检索)
                            ↓
                    统一JSON格式输出
```

## 🎯 目标

将GPT-OSS-20B微调为专业的Bitcoin量化分析师，输出结构化的JSON格式交易建议。

## 🏗️ 目录结构

```
fine_tune/
├── pyproject.toml              # RTX 5090专用环境配置
├── README.md                   # 本文件
├── data_preparation/           # 数据预处理
│   ├── download_datasets.py    # 下载HuggingFace数据集
│   ├── data_formatter.py       # 统一数据格式
│   └── data_mixer.py           # 85%-10%-5%数据混合
├── training_scripts/           # 训练脚本
│   ├── unsloth_trainer.py      # 主训练脚本
│   ├── config.yaml             # 训练配置
│   └── monitor.py              # 训练监控
├── model_export/               # 模型导出
│   ├── export_for_vllm.py      # 导出vLLM兼容格式
│   └── model_validator.py      # 模型验证
├── configs/                    # 配置文件
├── logs/                       # 训练日志
└── checkpoints/                # 模型检查点
```

## 🚀 快速开始

### 1. 安装Fine-tune模块依赖

```bash
# 设置RTX 5090环境变量
export TORCH_CUDA_ARCH_LIST="12.0"
export CUDA_VISIBLE_DEVICES=0

# LLM微调模块 (本模块)
cd fine_tune
source .venv/bin/activate
uv sync  # 安装微调相关依赖 (unsloth + pytorch + transformers)
```

### 2. 安装RAG模块依赖 (并行开发)

```bash
# RAG知识系统模块
cd rag_test
source .venv/bin/activate
uv sync  # 安装RAG相关依赖 (granite-docling + embedding)
```

### 3. 验证RTX 5090支持

```bash
python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'Device Name: {torch.cuda.get_device_name()}')
print(f'Device Capability: {torch.cuda.get_device_capability()}')
print(f'Memory: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB')
"
```

预期输出：
```
CUDA Available: True
Device Name: NVIDIA GeForce RTX 5090
Device Capability: (12, 0)
Memory: 32.6GB
```

### 4. 数据准备 (✅ 已完成)

```bash
# ✅ 数据集已下载并预处理完成
# final_data/ 目录包含:
# - train.jsonl: 18,719样本 (72.8MB)
# - validation.jsonl: 2,335样本 (9.1MB)
# - test.jsonl: 1,095样本 (4.1MB)
```

### 5. 微调训练 (✅ 已完成)

```bash
# ✅ 训练已完成 - 使用以下脚本进行的训练
python training_scripts/simple_trainer.py

# ✅ 训练结果:
# - 训练时间: 1.65小时 (3 epochs)
# - LoRA权重: 122MB (checkpoints/adapter_model.safetensors)
# - 损失收敛: 1.32 → 1.25
# - WandB监控: 已记录完整训练过程
```

## 📊 数据集策略

基于session log的分析结果：

### 选定数据集
1. **bitcoin-llm-finetuning-dataset_new**: 2,301样本 (99.3%高质量)
2. **bitcoin-sllm-instruct_v2**: 4,290样本 (99.9%高质量)

### 数据混合比例
- **85% Bitcoin专业数据**: 5,610样本 - 核心专业能力
- **10% 数学推理数据**: 660样本 - 计算能力保持
- **5% 逻辑推理数据**: 330样本 - 基础推理能力

### 目标输出格式
```json
{
  "action": "BUY|SELL|HOLD",
  "confidence": 72,
  "current_price": 109453.00,
  "stop_loss": 105200.00,
  "take_profit": 116800.00,
  "forecast_10d": [109800, 111200, ...],
  "analysis": "技术面分析文本",
  "risk_score": 0.31,
  "technical_indicators": {...}
}
```

## ⚙️ 训练配置

### 实际训练配置 (已验证成功)
```yaml
# ✅ 成功使用的配置
model_name: "openai/gpt-oss-20b"  # 实际使用模型
max_seq_length: 2048

# LoRA参数 (实际成功配置)
lora_r: 64                    # rank
lora_alpha: 128               # 2*r配比
lora_dropout: 0.1
target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]

# 训练参数 (实际使用)
per_device_train_batch_size: 4
gradient_accumulation_steps: 8
learning_rate: 2e-4           # 成功的学习率
num_train_epochs: 3
warmup_steps: 100

# 内存优化
gradient_checkpointing: "unsloth"  # Unsloth优化
optim: "adamw_8bit"
fp16: true
dataloader_pin_memory: false

# 实际依赖版本
software_versions:
  unsloth: "2025.9.9"
  torch: "2.8.0+cu128"
  transformers: "4.56.2"
  peft: "0.17.1"
```

## 📈 实际性能结果

### ✅ 训练性能 (RTX 5090)
- **总训练时间**: 1.65小时 (3 epochs) - 比预期快7倍！
- **训练速度**: 3.145 samples/second
- **检查点保存**: 每200步 (checkpoint-200, 400, 585)
- **内存效率**: 优于预期，RTX 5090性能充足

### ✅ 模型规模
- **LoRA权重**: 122MB (vs 基础模型~20GB)
- **压缩比**: 99.4% 参数减少
- **checkpoints总大小**: 779MB (包含3个检查点)
- **部署文件**: 仅需149MB (生产环境)

## 🔗 与主框架集成

训练完成后，模型将集成到：
```
ZJ_Volume/
├── milo_bitcoin_main.py      # 主框架 - 替换TODO模型
├── fine_tune/                # 本目录
├── rag_system/               # RAG知识系统 (并行开发)
└── integration/              # 集成部署
```

## 🚨 故障排除

### 常见问题

1. **sm_120不支持错误**
```bash
# 确保使用CUDA 12.8，不是13.0
pip install torch --extra-index-url https://download.pytorch.org/whl/cu128
export TORCH_CUDA_ARCH_LIST="12.0"
```

2. **内存不足**
```bash
# 减少批次大小
per_device_train_batch_size: 2
gradient_accumulation_steps: 16
```

3. **Unsloth安装问题**
```bash
# 重新安装
pip uninstall unsloth -y
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

## 📝 项目进度

### ✅ 已完成任务
1. ✅ 目录结构创建完成
2. ✅ PyTorch sm_120兼容性验证 (CUDA 12.8 + RTX 5090)
3. ✅ 训练环境配置完成 (pyproject.toml修复)
4. ✅ 数据集下载和预处理 (18,719训练样本)
5. ✅ GPT-OSS-20B LoRA微调训练 (122MB权重)
6. ✅ 训练监控和检查点保存

### 🔄 当前任务 (下一步)
7. 🔄 **模型质量评估** - 推理测试和性能验证
8. ⏸️ **vLLM部署配置** - 推理服务器搭建
9. ⏸️ **与主框架集成** - 统一API接口设计

### 🎯 模块化集成规划
- **fine_tune** (本模块): ✅ 训练完成
- **rag_test**: ✅ 文档处理pipeline就绪
- **vllm** (计划): 推理服务和两模块整合

---

**记住**: 这是并行开发的Track B (LLM微调)，与Track A (RAG系统)独立进行，最终在integration层汇合。🚀