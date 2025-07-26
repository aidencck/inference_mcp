#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具调用模型微调脚本
用于训练能够正确调用MCP工具的大语言模型
"""

import json
import os
import sys
import torch
import yaml
from pathlib import Path
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from datasets import Dataset
import logging
from typing import List, Dict, Any, Optional
from model_manager import ModelManager
from huggingface_manager import HuggingFaceManager
from peft import LoraConfig, get_peft_model, TaskType
import wandb

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPDatasetProcessor:
    """MCP数据集处理器"""
    
    def __init__(self, tokenizer, max_length: int = 2048):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def load_jsonl_data(self, file_path: str) -> List[Dict]:
        """加载JSONL格式的训练数据"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data
    
    def format_conversation(self, messages: List[Dict]) -> str:
        """将对话格式化为训练文本"""
        formatted_text = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted_text += f"<|system|>\n{content}\n\n"
            elif role == "user":
                formatted_text += f"<|user|>\n{content}\n\n"
            elif role == "assistant":
                formatted_text += f"<|assistant|>\n{content}"
                
                # 处理工具调用
                if "tool_calls" in message:
                    tool_calls = message["tool_calls"]
                    for tool_call in tool_calls:
                        function_name = tool_call["function"]["name"]
                        arguments = tool_call["function"]["arguments"]
                        formatted_text += f"\n\n<|tool_call|>\n{function_name}({arguments})"
                
                formatted_text += "\n\n"
            elif role == "tool":
                formatted_text += f"<|tool_result|>\n{content}\n\n"
        
        formatted_text += "<|end|>"
        return formatted_text
    
    def tokenize_function(self, examples):
        """数据tokenization函数"""
        texts = []
        for messages in examples["messages"]:
            formatted_text = self.format_conversation(messages)
            texts.append(formatted_text)
        
        # Tokenize
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            padding=False,
            max_length=self.max_length,
            return_tensors=None
        )
        
        # 设置labels为input_ids的副本（用于语言建模）
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    def prepare_dataset(self, data_path: str) -> Dataset:
        """准备训练数据集"""
        # 加载原始数据
        raw_data = self.load_jsonl_data(data_path)
        
        # 转换为Dataset格式
        dataset = Dataset.from_list(raw_data)
        
        # 应用tokenization
        tokenized_dataset = dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset

class MCPTrainer:
    """MCP模型训练器"""
    
    def __init__(self, config_path: str = "../config.yaml"):
        self.model_manager = ModelManager(config_path)
        self.config = self.model_manager.config
        self.setup_directories()
        
        # 初始化HuggingFace管理器（如果启用）
        self.hf_manager = None
        if self.config.get("huggingface", {}).get("enabled", False):
            try:
                self.hf_manager = HuggingFaceManager(config_path)
                logger.info("HuggingFace管理器初始化成功")
            except Exception as e:
                logger.warning(f"HuggingFace管理器初始化失败: {e}")
                self.hf_manager = None
        
    def setup_directories(self):
        """设置输出目录"""
        # 获取项目根目录
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 处理输出目录路径
        model_dir = self.config["output"]["model_dir"]
        if not os.path.isabs(model_dir):
            self.output_dir = os.path.join(project_dir, model_dir)
        else:
            self.output_dir = model_dir
            
        # 处理日志目录路径
        log_dir = self.config["output"]["log_dir"]
        if not os.path.isabs(log_dir):
            self.log_dir = os.path.join(project_dir, log_dir)
        else:
            self.log_dir = log_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        logger.info(f"输出目录: {self.output_dir}")
        logger.info(f"日志目录: {self.log_dir}")
    
    def setup_lora_config(self) -> LoraConfig:
        """设置LoRA配置"""
        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,  # LoRA rank
            lora_alpha=32,  # LoRA scaling parameter
            lora_dropout=0.1,  # LoRA dropout
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
    
    def prepare_datasets(self, tokenizer):
        """准备训练和验证数据集"""
        processor = MCPDatasetProcessor(tokenizer, self.config["model"]["max_length"])
        
        # 获取项目根目录
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 训练数据集
        train_path = self.config["data"]["train_file"]
        if not os.path.isabs(train_path):
            train_path = os.path.join(project_dir, train_path)
        train_dataset = processor.prepare_dataset(train_path)
        
        # 验证数据集
        val_dataset = None
        val_path = self.config["data"]["validation_file"]
        if val_path:
            if not os.path.isabs(val_path):
                val_path = os.path.join(project_dir, val_path)
            if os.path.exists(val_path):
                val_dataset = processor.prepare_dataset(val_path)
        
        logger.info(f"训练数据集大小: {len(train_dataset)}")
        if val_dataset:
            logger.info(f"验证数据集大小: {len(val_dataset)}")
        
        return train_dataset, val_dataset
    
    def train(self, use_lora: bool = True, use_wandb: bool = False):
        """开始训练"""
        logger.info("开始MCP模型微调训练")
        
        # 初始化wandb
        if use_wandb:
            wandb.init(
                project="mcp-finetune",
                config=self.config,
                dir=self.log_dir
            )
        
        # 加载模型和分词器
        model, tokenizer = self.model_manager.load_model_and_tokenizer()
        
        # 应用LoRA
        if use_lora:
            logger.info("应用LoRA配置")
            lora_config = self.setup_lora_config()
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()
        
        # 准备数据集
        train_dataset, val_dataset = self.prepare_datasets(tokenizer)
        
        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8
        )
        
        # 训练参数
        training_config = self.config["training"]
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=training_config["num_epochs"],
            per_device_train_batch_size=training_config["batch_size"],
            per_device_eval_batch_size=training_config["batch_size"],
            gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
            warmup_steps=training_config["warmup_steps"],
            learning_rate=training_config["learning_rate"],
            weight_decay=training_config["weight_decay"],
            logging_dir=self.log_dir,
            logging_steps=self.config["output"]["logging_steps"],
            save_steps=self.config["output"]["save_steps"],
            save_total_limit=3,
            evaluation_strategy="steps" if val_dataset else "no",
            eval_steps=self.config["output"]["save_steps"] if val_dataset else None,
            load_best_model_at_end=True if val_dataset else False,
            metric_for_best_model="eval_loss" if val_dataset else None,
            greater_is_better=False,
            remove_unused_columns=False,
            fp16=training_config["fp16"] and torch.cuda.is_available(),
            dataloader_num_workers=4,
            report_to="wandb" if use_wandb else None,
            run_name=f"mcp-finetune-{self.config['model']['name'].split('/')[-1]}",
            seed=42,
            data_seed=42,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            save_safetensors=True,
        )
        
        # 回调函数
        callbacks = []
        if val_dataset:
            callbacks.append(EarlyStoppingCallback(early_stopping_patience=3))
        
        # 创建Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
            callbacks=callbacks,
        )
        
        # 开始训练
        logger.info("开始训练...")
        try:
            trainer.train()
            
            # 保存最终模型
            logger.info(f"保存模型到: {self.output_dir}")
            trainer.save_model()
            tokenizer.save_pretrained(self.output_dir)
            
            # 保存训练配置
            config_save_path = os.path.join(self.output_dir, "training_config.yaml")
            with open(config_save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info("训练完成！")
            
            # 评估模型
            if val_dataset:
                logger.info("开始最终评估...")
                eval_results = trainer.evaluate()
                logger.info(f"评估结果: {eval_results}")
                
                # 保存评估结果
                eval_save_path = os.path.join(self.output_dir, "eval_results.json")
                with open(eval_save_path, 'w', encoding='utf-8') as f:
                    json.dump(eval_results, f, indent=2, ensure_ascii=False)
            
            # 自动同步到HuggingFace（如果启用）
            if self.hf_manager and self.config.get("huggingface", {}).get("auto_sync", {}).get("after_training", False):
                logger.info("开始同步到HuggingFace...")
                try:
                    sync_results = self.hf_manager.sync_training_workflow(
                        model_path=self.output_dir,
                        private=self.config.get("huggingface", {}).get("repositories", {}).get("private", True)
                    )
                    logger.info("HuggingFace同步完成:")
                    for key, url in sync_results.items():
                        logger.info(f"  {key}: {url}")
                except Exception as e:
                    logger.error(f"HuggingFace同步失败: {e}")
            elif self.hf_manager:
                logger.info("HuggingFace自动同步已禁用，可手动运行同步")
                logger.info(f"手动同步命令: python scripts/huggingface_manager.py --action sync --model_path {self.output_dir}")
            
        except Exception as e:
            logger.error(f"训练过程中出现错误: {e}")
            raise
        finally:
            if use_wandb:
                wandb.finish()

def train_mcp_model(
    config_path: str = "../config.yaml",
    use_lora: bool = True,
    use_wandb: bool = False
):
    """训练MCP工具调用模型"""
    trainer = MCPTrainer(config_path)
    trainer.train(use_lora=use_lora, use_wandb=use_wandb)

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="训练MCP工具调用模型")
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    parser.add_argument("--resume", type=str, help="从检查点恢复训练")
    parser.add_argument("--wandb_project", type=str, help="Weights & Biases项目名称")
    
    args = parser.parse_args()
    
    # 确保配置文件路径正确
    config_path = args.config
    if not os.path.isabs(config_path):
        # 如果是相对路径，相对于脚本所在目录的父目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        config_path = os.path.join(project_dir, config_path)
    
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        exit(1)
    
    logger.info(f"使用配置文件: {config_path}")
    
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建训练器
    trainer = MCPTrainer(config)
    
    # 开始训练
    trainer.train(
        resume_from_checkpoint=args.resume,
        wandb_project=args.wandb_project
    )