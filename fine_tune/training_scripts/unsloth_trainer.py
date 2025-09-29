#!/usr/bin/env python3
"""
Milo Bitcoin - Unsloth Trainer
RTX 5090优化的GPT-OSS-20B微调脚本

配置说明:
- 模型: microsoft/DialoGPT-medium (作为GPT-OSS-20B替代)
- LoRA: rank=64, alpha=128 (2*r配比)
- 批次大小: 4 (RTX 5090 32GB优化)
- 梯度累积: 8步 (有效批次32)
- 学习率: 2e-4 (Unsloth支持更高LR)
"""

import os
import sys
import json
import torch
import wandb
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer
import logging
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# 环境检查
console.print("🔧 检查Unsloth和GPU环境...")
try:
    from unsloth import FastLanguageModel
    from unsloth import is_bfloat16_supported
    console.print("✅ Unsloth导入成功")
except ImportError as e:
    console.print(f"❌ Unsloth导入失败: {e}")
    sys.exit(1)

# GPU检查
if not torch.cuda.is_available():
    console.print("❌ CUDA不可用")
    sys.exit(1)

gpu_name = torch.cuda.get_device_name()
gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
console.print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f}GB)")

class BitcoinUnslothTrainer:
    """Bitcoin专业微调训练器 - RTX 5090优化"""

    def __init__(self,
                 data_dir: str = "final_data",
                 output_dir: str = "checkpoints",
                 config_file: Optional[str] = None):

        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 训练配置 - RTX 5090优化
        self.config = {
            # 模型配置
            "model_name": "openai/gpt-oss-20b",  # 真正的GPT-OSS-20B (21B参数)
            "max_seq_length": 2048,  # 考虑到长input
            "dtype": None,  # 自动选择最佳类型
            "load_in_4bit": True,  # 4-bit量化节省内存

            # LoRA配置 (32GB VRAM可以更激进)
            "lora_r": 64,  # rank
            "lora_alpha": 128,  # 2*r配比
            "lora_dropout": 0.1,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],  # GPT-OSS-20B attention模块
            "lora_bias": "none",
            "task_type": "CAUSAL_LM",

            # 训练参数
            "per_device_train_batch_size": 4,
            "per_device_eval_batch_size": 4,
            "gradient_accumulation_steps": 8,  # 有效批次大小: 4*8=32
            "learning_rate": 2e-4,  # Unsloth支持更高学习率
            "num_train_epochs": 3,
            "max_steps": -1,  # 使用epochs而非steps
            "warmup_steps": 100,
            "weight_decay": 0.01,

            # 内存优化
            "gradient_checkpointing": True,
            "optim": "adamw_8bit",
            "fp16": not is_bfloat16_supported(),
            "bf16": is_bfloat16_supported(),
            "dataloader_pin_memory": False,
            "dataloader_num_workers": 4,

            # 监控和保存
            "eval_steps": 100,
            "save_steps": 200,
            "logging_steps": 10,
            "evaluation_strategy": "steps",
            "save_strategy": "steps",
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "save_total_limit": 3,

            # wandb配置
            "report_to": "wandb",
            "run_name": f"milo-bitcoin-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}",
        }

        # 加载自定义配置
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
                console.print(f"✅ 加载自定义配置: {config_file}")

    def load_datasets(self) -> Dict[str, Dataset]:
        """加载训练数据集"""
        console.print("📁 加载训练数据集...")

        datasets = {}

        # 训练集
        train_file = self.data_dir / "train.jsonl"
        if not train_file.exists():
            raise FileNotFoundError(f"训练文件不存在: {train_file}")

        train_data = []
        with open(train_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    train_data.append(json.loads(line.strip()))

        datasets["train"] = Dataset.from_pandas(pd.DataFrame(train_data))
        console.print(f"  ✅ 训练集: {len(train_data):,} 样本")

        # 验证集
        val_file = self.data_dir / "validation.jsonl"
        if val_file.exists():
            val_data = []
            with open(val_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        val_data.append(json.loads(line.strip()))

            datasets["validation"] = Dataset.from_pandas(pd.DataFrame(val_data))
            console.print(f"  ✅ 验证集: {len(val_data):,} 样本")

        return datasets

    def setup_model_and_tokenizer(self):
        """设置模型和分词器"""
        console.print(f"🤖 加载模型: {self.config['model_name']}")

        # 使用Unsloth快速加载
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.config["model_name"],
            max_seq_length=self.config["max_seq_length"],
            dtype=self.config["dtype"],
            load_in_4bit=self.config["load_in_4bit"]
        )

        # 配置LoRA
        model = FastLanguageModel.get_peft_model(
            model,
            r=self.config["lora_r"],
            alpha=self.config["lora_alpha"],
            target_modules=self.config["target_modules"],
            lora_dropout=self.config["lora_dropout"],
            bias=self.config["lora_bias"],
            use_gradient_checkpointing=self.config["gradient_checkpointing"],
            random_state=42,
        )

        # 配置分词器
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        console.print("✅ 模型和LoRA配置完成")

        # 显示可训练参数
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        console.print(f"📊 可训练参数: {trainable_params:,} / {total_params:,} ({trainable_params/total_params*100:.2f}%)")

        return model, tokenizer

    def format_prompt(self, sample: Dict) -> str:
        """格式化训练样本为GPT-OSS-20B的harmony格式"""
        instruction = sample["instruction"]
        input_text = sample["input"]
        output = sample["output"]

        # 使用GPT-OSS-20B的harmony response格式
        if input_text.strip():
            prompt = f"<|user|>\n{instruction}\n\n{input_text}<|end|>\n<|assistant|>\n{output}<|end|>"
        else:
            prompt = f"<|user|>\n{instruction}<|end|>\n<|assistant|>\n{output}<|end|>"

        return prompt

    def setup_trainer(self, model, tokenizer, datasets):
        """设置SFT训练器"""
        console.print("🏋️ 设置SFT训练器...")

        # 训练参数
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            per_device_train_batch_size=self.config["per_device_train_batch_size"],
            per_device_eval_batch_size=self.config["per_device_eval_batch_size"],
            gradient_accumulation_steps=self.config["gradient_accumulation_steps"],
            learning_rate=self.config["learning_rate"],
            num_train_epochs=self.config["num_train_epochs"],
            max_steps=self.config["max_steps"],
            warmup_steps=self.config["warmup_steps"],
            weight_decay=self.config["weight_decay"],
            optim=self.config["optim"],
            fp16=self.config["fp16"],
            bf16=self.config["bf16"],
            gradient_checkpointing=self.config["gradient_checkpointing"],
            dataloader_pin_memory=self.config["dataloader_pin_memory"],
            dataloader_num_workers=self.config["dataloader_num_workers"],
            eval_steps=self.config["eval_steps"],
            save_steps=self.config["save_steps"],
            logging_steps=self.config["logging_steps"],
            eval_strategy=self.config["evaluation_strategy"],  # 新版本使用eval_strategy
            save_strategy=self.config["save_strategy"],
            load_best_model_at_end=self.config["load_best_model_at_end"],
            metric_for_best_model=self.config["metric_for_best_model"],
            greater_is_better=self.config["greater_is_better"],
            save_total_limit=self.config["save_total_limit"],
            report_to=self.config["report_to"],
            run_name=self.config["run_name"],
            remove_unused_columns=False,
            max_length=self.config["max_seq_length"],  # 在TrainingArguments中设置max_length
        )

        # SFT训练器 - 新版本TRL兼容
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=datasets["train"],
            eval_dataset=datasets.get("validation"),
            processing_class=tokenizer,  # 新版本使用processing_class
            formatting_func=self.format_prompt,
            packing=False,  # 对于长序列，关闭packing
        )

        console.print("✅ SFT训练器配置完成")
        return trainer

    def monitor_training(self, trainer):
        """训练过程监控"""
        console.print("📊 开始训练监控...")

        # 显示训练配置摘要
        config_table = Table(title="🎯 训练配置摘要")
        config_table.add_column("参数", style="cyan")
        config_table.add_column("值", style="yellow")

        key_configs = [
            ("模型", self.config["model_name"]),
            ("最大序列长度", self.config["max_seq_length"]),
            ("LoRA Rank", self.config["lora_r"]),
            ("LoRA Alpha", self.config["lora_alpha"]),
            ("批次大小", f"{self.config['per_device_train_batch_size']} x {self.config['gradient_accumulation_steps']} = {self.config['per_device_train_batch_size'] * self.config['gradient_accumulation_steps']}"),
            ("学习率", self.config["learning_rate"]),
            ("训练轮数", self.config["num_train_epochs"]),
            ("优化器", self.config["optim"]),
            ("精度", "BF16" if self.config["bf16"] else "FP16"),
        ]

        for param, value in key_configs:
            config_table.add_row(param, str(value))

        console.print(config_table)

    def save_training_metadata(self):
        """保存训练元数据"""
        metadata = {
            "config": self.config,
            "gpu_info": {
                "name": torch.cuda.get_device_name(),
                "memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "compute_capability": torch.cuda.get_device_capability()
            },
            "training_start": pd.Timestamp.now().isoformat(),
            "unsloth_version": "2025.6.0+",  # 假设版本
            "pytorch_version": torch.__version__,
        }

        metadata_file = self.output_dir / "training_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        console.print(f"✅ 训练元数据已保存: {metadata_file}")

    def run_training(self):
        """执行完整训练流程"""
        console.clear()
        console.print("🚀 [bold cyan]Milo Bitcoin - Unsloth Trainer[/bold cyan]")
        console.print("RTX 5090优化的Bitcoin量化分析师微调\n")

        try:
            # 1. 加载数据集
            datasets = self.load_datasets()

            # 2. 设置模型和分词器
            model, tokenizer = self.setup_model_and_tokenizer()

            # 3. 设置训练器
            trainer = self.setup_trainer(model, tokenizer, datasets)

            # 4. 训练监控
            self.monitor_training(trainer)

            # 5. 保存元数据
            self.save_training_metadata()

            # 6. 初始化wandb (如果配置)
            if self.config["report_to"] == "wandb":
                console.print("🔗 初始化Wandb监控...")
                wandb.init(
                    project="milo-bitcoin-finetuning",
                    name=self.config["run_name"],
                    config=self.config
                )

            # 7. 开始训练
            console.print("\n🏋️ 开始训练...")
            train_result = trainer.train()

            # 8. 保存最终模型
            console.print("💾 保存最终模型...")
            trainer.save_model()

            # 9. 训练总结
            console.print("\n🎉 训练完成!")

            summary_table = Table(title="📈 训练总结")
            summary_table.add_column("指标", style="cyan")
            summary_table.add_column("值", style="yellow")

            summary_table.add_row("最终损失", f"{train_result.training_loss:.6f}")
            summary_table.add_row("训练步数", f"{train_result.global_step:,}")
            summary_table.add_row("模型保存位置", str(self.output_dir))

            console.print(summary_table)

            # 下一步指导
            next_steps = Text()
            next_steps.append("🎯 下一步操作:\n\n", style="bold green")
            next_steps.append("1. 导出模型: python model_export/export_for_vllm.py\n", style="white")
            next_steps.append("2. 测试模型: python model_export/model_validator.py\n", style="white")
            next_steps.append("3. 集成到Milo: 替换主框架模型路径\n", style="white")

            console.print(Panel(next_steps, title="✨ 微调完成", border_style="green"))

            return True

        except Exception as e:
            logger.error(f"训练失败: {e}")
            console.print(f"❌ 训练失败: {e}")
            return False

        finally:
            if wandb.run:
                wandb.finish()

if __name__ == "__main__":
    # 设置CUDA环境
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # 创建训练器并执行
    trainer = BitcoinUnslothTrainer()
    success = trainer.run_training()

    if success:
        console.print("\n🎉 Bitcoin量化分析师微调成功完成!")
    else:
        console.print("\n❌ 微调失败，请检查错误信息。")
        sys.exit(1)