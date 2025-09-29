#!/usr/bin/env python3
"""
Milo Bitcoin - Simple Unsloth Trainer
简化版训练脚本，避开版本兼容性问题
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path
from datasets import Dataset
from transformers import TrainingArguments
from rich.console import Console

console = Console()

# 导入Unsloth
try:
    from unsloth import FastLanguageModel
    from unsloth import is_bfloat16_supported
    from unsloth.chat_templates import get_chat_template
    console.print("✅ Unsloth导入成功")
except ImportError as e:
    console.print(f"❌ Unsloth导入失败: {e}")
    exit(1)

def load_training_data():
    """加载训练数据"""
    console.print("📁 加载训练数据...")

    train_file = Path("final_data/train.jsonl")
    val_file = Path("final_data/validation.jsonl")

    # 加载训练数据
    train_data = []
    with open(train_file, 'r') as f:
        for line in f:
            if line.strip():
                train_data.append(json.loads(line))

    # 加载验证数据
    val_data = []
    if val_file.exists():
        with open(val_file, 'r') as f:
            for line in f:
                if line.strip():
                    val_data.append(json.loads(line))

    console.print(f"✅ 训练集: {len(train_data)} 样本")
    console.print(f"✅ 验证集: {len(val_data)} 样本")

    return train_data, val_data

def format_prompts(examples):
    """格式化训练样本"""
    texts = []
    for instruction, input_text, output in zip(examples["instruction"], examples["input"], examples["output"]):
        # 使用GPT-OSS-20B的格式
        if input_text.strip():
            text = f"<|user|>\n{instruction}\n\n{input_text}<|end|>\n<|assistant|>\n{output}<|end|>"
        else:
            text = f"<|user|>\n{instruction}<|end|>\n<|assistant|>\n{output}<|end|>"
        texts.append(text)
    return {"text": texts}

def main():
    console.clear()
    console.print("🚀 [bold cyan]Milo Bitcoin - Simple Trainer[/bold cyan]")
    console.print("GPT-OSS-20B微调 (简化版)\n")

    # 1. 加载数据
    train_data, val_data = load_training_data()

    # 2. 加载模型
    console.print("🤖 加载GPT-OSS-20B模型...")
    max_seq_length = 2048
    dtype = None
    load_in_4bit = True

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="openai/gpt-oss-20b",
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )

    # 3. 配置LoRA
    console.print("⚙️ 配置LoRA...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=64,
        alpha=128,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.1,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    # 显示可训练参数
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    console.print(f"📊 可训练参数: {trainable_params:,} / {total_params:,} ({trainable_params/total_params*100:.2f}%)")

    # 4. 准备数据集
    console.print("📋 准备数据集...")
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data) if val_data else None

    train_dataset = train_dataset.map(format_prompts, batched=True)
    if val_dataset:
        val_dataset = val_dataset.map(format_prompts, batched=True)

    # 5. 使用Unsloth的SFTTrainer
    console.print("🏋️ 设置训练器...")
    from trl import SFTTrainer
    from transformers import DataCollatorForSeq2Seq

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=4,
            gradient_accumulation_steps=8,
            warmup_steps=100,
            num_train_epochs=3,
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=42,
            output_dir="checkpoints",
            save_steps=200,
            eval_steps=100,
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            report_to="wandb",
            run_name=f"milo-bitcoin-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}",
        ),
    )

    # 6. 开始训练
    console.print("🚀 开始训练...")
    console.print("📊 训练监控: https://wandb.ai/zgu17/huggingface")

    # 初始化wandb
    import wandb
    wandb.init(
        project="milo-bitcoin-finetuning",
        name=f"simple-trainer-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}",
        config={
            "model": "openai/gpt-oss-20b",
            "lora_r": 64,
            "lora_alpha": 128,
            "batch_size": 4,
            "grad_accum": 8,
            "learning_rate": 2e-4,
            "epochs": 3,
        }
    )

    # 训练
    trainer_stats = trainer.train()

    # 7. 保存模型
    console.print("💾 保存模型...")
    trainer.save_model()

    # 8. 保存统计
    stats = {
        "training_loss": trainer_stats.training_loss,
        "global_step": trainer_stats.global_step,
        "metrics": trainer_stats.metrics,
    }

    with open("checkpoints/training_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    console.print("🎉 训练完成!")
    console.print(f"📊 最终损失: {trainer_stats.training_loss:.6f}")
    console.print(f"🔢 全局步数: {trainer_stats.global_step}")
    console.print(f"💾 模型保存在: checkpoints/")

    wandb.finish()

if __name__ == "__main__":
    main()