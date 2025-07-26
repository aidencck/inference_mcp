#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器
负责模型下载、缓存管理和配置
"""

import os
import yaml
import torch
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    AutoConfig
)
from huggingface_hub import snapshot_download, login
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelManager:
    """模型管理器"""
    
    def __init__(self, config_path: str = "../config.yaml"):
        self.config = self.load_config(config_path)
        # 使用项目目录下的缓存目录
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = os.path.join(project_dir, ".cache", "models")
        self.ensure_cache_dir()
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            # 返回默认配置
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "model": {
                "name": "Qwen/Qwen2-7B-Instruct",
                "max_length": 2048,
                "device": "auto"
            },
            "training": {
                "num_epochs": 3,
                "batch_size": 4,
                "gradient_accumulation_steps": 4,
                "learning_rate": 2e-5,
                "warmup_steps": 100,
                "weight_decay": 0.01,
                "fp16": True
            },
            "data": {
                "train_file": "data/mcp_tool_calls.jsonl",
                "validation_file": "data/mcp_validation.jsonl",
                "num_train_samples": 500,
                "num_val_samples": 100
            },
            "output": {
                "model_dir": "./mcp_finetuned_model",
                "log_dir": "./logs",
                "save_steps": 500,
                "logging_steps": 10
            }
        }
    
    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"模型缓存目录: {self.cache_dir}")
    
    def check_model_availability(self, model_name: str) -> bool:
        """检查模型是否可用"""
        try:
            # 检查本地缓存
            local_path = os.path.join(self.cache_dir, model_name.replace("/", "--"))
            if os.path.exists(local_path) and os.listdir(local_path):
                logger.info(f"模型已存在于本地缓存: {local_path}")
                return True
            
            # 检查HuggingFace Hub
            config = AutoConfig.from_pretrained(model_name)
            logger.info(f"模型在HuggingFace Hub上可用: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"模型不可用: {model_name}, 错误: {e}")
            return False
    
    def download_model(self, model_name: str, force_download: bool = False) -> str:
        """下载模型到本地缓存"""
        local_path = os.path.join(self.cache_dir, model_name.replace("/", "--"))
        
        # 检查是否已存在且不强制下载
        if os.path.exists(local_path) and os.listdir(local_path) and not force_download:
            logger.info(f"模型已存在，跳过下载: {local_path}")
            return local_path
        
        try:
            logger.info(f"开始下载模型: {model_name}")
            logger.info(f"下载到: {local_path}")
            
            # 使用snapshot_download下载完整模型
            downloaded_path = snapshot_download(
                repo_id=model_name,
                cache_dir=self.cache_dir,
                local_dir=local_path,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            logger.info(f"模型下载完成: {downloaded_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"模型下载失败: {e}")
            raise
    
    def load_model_and_tokenizer(self, model_name: Optional[str] = None, local_path: Optional[str] = None):
        """加载模型和分词器"""
        if local_path:
            model_path = local_path
        elif model_name:
            # 先尝试下载到本地
            model_path = self.download_model(model_name)
        else:
            model_name = self.config["model"]["name"]
            model_path = self.download_model(model_name)
        
        logger.info(f"加载模型: {model_path}")
        
        try:
            # 加载分词器
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_fast=False
            )
            
            # 加载模型
            device_map = self.config["model"].get("device", "auto")
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch_dtype,
                device_map=device_map if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # 设置pad token
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                model.config.pad_token_id = tokenizer.eos_token_id
            
            logger.info("模型和分词器加载成功")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            config = AutoConfig.from_pretrained(model_name)
            
            info = {
                "model_name": model_name,
                "model_type": config.model_type,
                "vocab_size": getattr(config, 'vocab_size', 'Unknown'),
                "hidden_size": getattr(config, 'hidden_size', 'Unknown'),
                "num_layers": getattr(config, 'num_hidden_layers', 'Unknown'),
                "num_attention_heads": getattr(config, 'num_attention_heads', 'Unknown'),
                "max_position_embeddings": getattr(config, 'max_position_embeddings', 'Unknown')
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取模型信息失败: {e}")
            return {"error": str(e)}
    
    def setup_huggingface_token(self, token: Optional[str] = None):
        """设置HuggingFace访问令牌"""
        if token:
            login(token=token)
            logger.info("HuggingFace令牌设置成功")
        else:
            # 尝试从环境变量获取
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if hf_token:
                login(token=hf_token)
                logger.info("从环境变量获取HuggingFace令牌")
            else:
                logger.warning("未设置HuggingFace令牌，可能无法访问私有模型")
    
    def list_cached_models(self) -> list:
        """列出已缓存的模型"""
        cached_models = []
        if os.path.exists(self.cache_dir):
            for item in os.listdir(self.cache_dir):
                item_path = os.path.join(self.cache_dir, item)
                if os.path.isdir(item_path):
                    # 将文件夹名转换回模型名
                    model_name = item.replace("--", "/")
                    cached_models.append({
                        "name": model_name,
                        "path": item_path,
                        "size": self.get_dir_size(item_path)
                    })
        return cached_models
    
    def get_dir_size(self, path: str) -> str:
        """获取目录大小"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        # 转换为人类可读格式
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} PB"
    
    def clear_cache(self, model_name: Optional[str] = None):
        """清理缓存"""
        if model_name:
            # 清理特定模型
            local_path = os.path.join(self.cache_dir, model_name.replace("/", "--"))
            if os.path.exists(local_path):
                import shutil
                shutil.rmtree(local_path)
                logger.info(f"已清理模型缓存: {model_name}")
        else:
            # 清理所有缓存
            if os.path.exists(self.cache_dir):
                import shutil
                shutil.rmtree(self.cache_dir)
                self.ensure_cache_dir()
                logger.info("已清理所有模型缓存")

if __name__ == "__main__":
    # 测试模型管理器
    manager = ModelManager()
    
    # 显示配置
    print("当前配置:")
    print(yaml.dump(manager.config, default_flow_style=False, allow_unicode=True))
    
    # 检查模型可用性
    model_name = manager.config["model"]["name"]
    print(f"\n检查模型可用性: {model_name}")
    available = manager.check_model_availability(model_name)
    print(f"模型可用: {available}")
    
    # 获取模型信息
    print(f"\n模型信息:")
    info = manager.get_model_info(model_name)
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 列出缓存的模型
    print(f"\n缓存的模型:")
    cached = manager.list_cached_models()
    if cached:
        for model in cached:
            print(f"  {model['name']} ({model['size']})")
    else:
        print("  无缓存模型")