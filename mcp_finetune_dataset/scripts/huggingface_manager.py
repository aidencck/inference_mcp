#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HuggingFace模型管理器
负责训练模型和配置的统一上传、版本管理和同步
"""

import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from huggingface_hub import (
    HfApi, 
    login, 
    create_repo, 
    upload_file, 
    upload_folder,
    list_repo_files,
    hf_hub_download
)
from transformers import AutoTokenizer, AutoModelForCausalLM
import git
import shutil

logger = logging.getLogger(__name__)

class HuggingFaceManager:
    """HuggingFace模型和配置管理器"""
    
    def __init__(self, config_path: str = "../config.yaml", hf_token: Optional[str] = None):
        # 处理配置文件路径
        if not os.path.isabs(config_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            config_path = os.path.join(project_dir, config_path)
            
        self.config = self.load_config(config_path)
        self.api = HfApi()
        self.setup_authentication(hf_token)
        
        # 设置仓库信息
        self.username = self.api.whoami()["name"]
        self.model_repo_name = f"{self.username}/mcp-finetuned-model"
        self.config_repo_name = f"{self.username}/mcp-training-configs"
        
        logger.info(f"HuggingFace用户: {self.username}")
        logger.info(f"模型仓库: {self.model_repo_name}")
        logger.info(f"配置仓库: {self.config_repo_name}")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def setup_authentication(self, hf_token: Optional[str] = None):
        """设置HuggingFace认证"""
        if hf_token:
            login(token=hf_token)
            logger.info("使用提供的HuggingFace令牌")
        else:
            # 尝试从环境变量获取
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if hf_token:
                login(token=hf_token)
                logger.info("从环境变量获取HuggingFace令牌")
            else:
                logger.warning("未设置HuggingFace令牌，可能无法上传私有模型")
    
    def create_repositories(self, private: bool = True):
        """创建HuggingFace仓库"""
        try:
            # 创建模型仓库
            create_repo(
                repo_id=self.model_repo_name,
                private=private,
                exist_ok=True,
                repo_type="model"
            )
            logger.info(f"模型仓库创建成功: {self.model_repo_name}")
            
            # 创建配置仓库
            create_repo(
                repo_id=self.config_repo_name,
                private=private,
                exist_ok=True,
                repo_type="dataset"  # 使用dataset类型存储配置
            )
            logger.info(f"配置仓库创建成功: {self.config_repo_name}")
            
        except Exception as e:
            logger.error(f"仓库创建失败: {e}")
            raise
    
    def upload_model(self, model_path: str, version_tag: Optional[str] = None, 
                    commit_message: Optional[str] = None) -> str:
        """上传训练好的模型到HuggingFace"""
        if not os.path.exists(model_path):
            raise ValueError(f"模型路径不存在: {model_path}")
        
        # 生成版本标签
        if not version_tag:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_tag = f"v{timestamp}"
        
        # 生成提交信息
        if not commit_message:
            commit_message = f"Upload MCP finetuned model {version_tag}"
        
        try:
            logger.info(f"开始上传模型: {model_path} -> {self.model_repo_name}")
            
            # 准备模型元数据
            model_card = self.generate_model_card(model_path, version_tag)
            model_card_path = os.path.join(model_path, "README.md")
            with open(model_card_path, 'w', encoding='utf-8') as f:
                f.write(model_card)
            
            # 上传整个模型文件夹
            upload_folder(
                folder_path=model_path,
                repo_id=self.model_repo_name,
                commit_message=commit_message,
                revision=version_tag
            )
            
            model_url = f"https://huggingface.co/{self.model_repo_name}/tree/{version_tag}"
            logger.info(f"模型上传成功: {model_url}")
            return model_url
            
        except Exception as e:
            logger.error(f"模型上传失败: {e}")
            raise
    
    def upload_training_config(self, config_data: Dict[str, Any], 
                              experiment_name: Optional[str] = None) -> str:
        """上传训练配置到HuggingFace"""
        # 生成实验名称
        if not experiment_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment_name = f"experiment_{timestamp}"
        
        try:
            # 创建临时目录
            # 使用项目内的临时目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            temp_dir = os.path.join(project_dir, ".temp", f"mcp_config_{experiment_name}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 保存配置文件
            config_file = os.path.join(temp_dir, "config.yaml")
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            # 生成实验元数据
            metadata = {
                "experiment_name": experiment_name,
                "timestamp": datetime.now().isoformat(),
                "model_name": config_data.get("model", {}).get("name", "unknown"),
                "training_params": config_data.get("training", {}),
                "data_params": config_data.get("data", {}),
                "output_params": config_data.get("output", {})
            }
            
            metadata_file = os.path.join(temp_dir, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # 上传配置
            upload_folder(
                folder_path=temp_dir,
                repo_id=self.config_repo_name,
                path_in_repo=experiment_name,
                commit_message=f"Upload training config for {experiment_name}"
            )
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            config_url = f"https://huggingface.co/datasets/{self.config_repo_name}/tree/main/{experiment_name}"
            logger.info(f"配置上传成功: {config_url}")
            return config_url
            
        except Exception as e:
            logger.error(f"配置上传失败: {e}")
            raise
    
    def upload_training_results(self, results_dir: str, experiment_name: str) -> str:
        """上传训练结果（日志、评估结果等）"""
        if not os.path.exists(results_dir):
            raise ValueError(f"结果目录不存在: {results_dir}")
        
        try:
            logger.info(f"开始上传训练结果: {results_dir}")
            
            # 上传结果文件夹
            upload_folder(
                folder_path=results_dir,
                repo_id=self.config_repo_name,
                path_in_repo=f"{experiment_name}/results",
                commit_message=f"Upload training results for {experiment_name}"
            )
            
            results_url = f"https://huggingface.co/datasets/{self.config_repo_name}/tree/main/{experiment_name}/results"
            logger.info(f"训练结果上传成功: {results_url}")
            return results_url
            
        except Exception as e:
            logger.error(f"训练结果上传失败: {e}")
            raise
    
    def download_model(self, version_tag: str = "main", local_dir: Optional[str] = None) -> str:
        """从HuggingFace下载模型"""
        if not local_dir:
            local_dir = f"./downloaded_models/{version_tag}"
        
        try:
            logger.info(f"开始下载模型: {self.model_repo_name}@{version_tag}")
            
            # 下载模型
            from huggingface_hub import snapshot_download
            downloaded_path = snapshot_download(
                repo_id=self.model_repo_name,
                revision=version_tag,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            
            logger.info(f"模型下载完成: {downloaded_path}")
            return downloaded_path
            
        except Exception as e:
            logger.error(f"模型下载失败: {e}")
            raise
    
    def download_config(self, experiment_name: str, local_dir: Optional[str] = None) -> str:
        """从HuggingFace下载训练配置"""
        if not local_dir:
            local_dir = f"./downloaded_configs/{experiment_name}"
        
        try:
            logger.info(f"开始下载配置: {experiment_name}")
            
            # 下载配置文件
            config_file = hf_hub_download(
                repo_id=self.config_repo_name,
                filename=f"{experiment_name}/config.yaml",
                local_dir=local_dir
            )
            
            # 下载元数据
            metadata_file = hf_hub_download(
                repo_id=self.config_repo_name,
                filename=f"{experiment_name}/metadata.json",
                local_dir=local_dir
            )
            
            logger.info(f"配置下载完成: {local_dir}")
            return local_dir
            
        except Exception as e:
            logger.error(f"配置下载失败: {e}")
            raise
    
    def list_model_versions(self) -> List[str]:
        """列出所有模型版本"""
        try:
            refs = self.api.list_repo_refs(repo_id=self.model_repo_name)
            versions = [ref.name for ref in refs.branches if ref.name != "main"]
            versions.append("main")
            return versions
        except Exception as e:
            logger.error(f"获取模型版本失败: {e}")
            return []
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """列出所有训练实验"""
        try:
            files = list_repo_files(repo_id=self.config_repo_name)
            experiments = []
            
            for file in files:
                if file.endswith("/metadata.json"):
                    experiment_name = file.split("/")[0]
                    try:
                        # 下载元数据
                        metadata_content = hf_hub_download(
                            repo_id=self.config_repo_name,
                            filename=file
                        )
                        with open(metadata_content, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        experiments.append(metadata)
                    except Exception as e:
                        logger.warning(f"无法读取实验元数据: {file}, 错误: {e}")
            
            return experiments
        except Exception as e:
            logger.error(f"获取实验列表失败: {e}")
            return []
    
    def generate_model_card(self, model_path: str, version_tag: str) -> str:
        """生成模型卡片"""
        # 读取训练配置
        config_file = os.path.join(model_path, "training_config.yaml")
        training_config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                training_config = yaml.safe_load(f)
        
        # 读取评估结果
        eval_file = os.path.join(model_path, "eval_results.json")
        eval_results = {}
        if os.path.exists(eval_file):
            with open(eval_file, 'r', encoding='utf-8') as f:
                eval_results = json.load(f)
        
        model_card = f"""---
license: apache-2.0
language:
- zh
- en
tags:
- mcp
- tool-calling
- fine-tuning
- conversational
base_model: {training_config.get('model', {}).get('name', 'unknown')}
---

# MCP Tool-Calling Fine-tuned Model

## 模型描述

这是一个基于MCP (Model Context Protocol) 协议微调的工具调用模型，能够理解用户意图并正确调用相应的工具。

## 版本信息

- **版本**: {version_tag}
- **基础模型**: {training_config.get('model', {}).get('name', 'unknown')}
- **训练时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 训练配置

```yaml
{yaml.dump(training_config, default_flow_style=False, allow_unicode=True)}
```

## 评估结果

```json
{json.dumps(eval_results, indent=2, ensure_ascii=False)}
```

## 使用方法

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# 加载模型和分词器
tokenizer = AutoTokenizer.from_pretrained("{self.model_repo_name}")
model = AutoModelForCausalLM.from_pretrained("{self.model_repo_name}")

# 使用模型进行推理
input_text = "请帮我搜索人工智能的最新发展"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**inputs, max_length=512)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

## 支持的工具

- web_search: 网络搜索
- get_weather: 天气查询
- list_files: 文件列表
- write_file: 文件写入
- read_file: 文件读取
- calculate: 数学计算
- get_current_time: 获取当前时间

## 注意事项

1. 该模型专门针对MCP工具调用场景进行了优化
2. 建议在使用时配合相应的工具执行环境
3. 模型输出需要进行工具调用解析和执行

## 许可证

Apache 2.0
"""
        return model_card
    
    def sync_training_workflow(self, model_path: str, experiment_name: Optional[str] = None,
                              version_tag: Optional[str] = None, private: bool = True) -> Dict[str, str]:
        """同步完整的训练工作流到HuggingFace"""
        if not experiment_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment_name = f"mcp_experiment_{timestamp}"
        
        if not version_tag:
            version_tag = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {}
        
        try:
            # 1. 创建仓库
            self.create_repositories(private=private)
            
            # 2. 上传训练配置
            config_url = self.upload_training_config(self.config, experiment_name)
            results["config_url"] = config_url
            
            # 3. 上传模型
            model_url = self.upload_model(model_path, version_tag)
            results["model_url"] = model_url
            
            # 4. 上传训练结果（如果存在）
            log_dir = self.config.get("output", {}).get("log_dir", "./logs")
            if os.path.exists(log_dir):
                results_url = self.upload_training_results(log_dir, experiment_name)
                results["results_url"] = results_url
            
            logger.info(f"训练工作流同步完成: {experiment_name}")
            return results
            
        except Exception as e:
            logger.error(f"训练工作流同步失败: {e}")
            raise

def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace模型管理器")
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    parser.add_argument("--token", type=str, help="HuggingFace访问令牌")
    parser.add_argument("--action", type=str, required=True, 
                       choices=["upload", "download", "list", "sync"],
                       help="操作类型")
    parser.add_argument("--model_path", type=str, help="模型路径")
    parser.add_argument("--experiment_name", type=str, help="实验名称")
    parser.add_argument("--version_tag", type=str, help="版本标签")
    parser.add_argument("--private", action="store_true", help="创建私有仓库")
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = HuggingFaceManager(args.config, args.token)
    
    if args.action == "upload":
        if not args.model_path:
            print("错误: 上传模型需要指定 --model_path")
            return
        
        url = manager.upload_model(args.model_path, args.version_tag)
        print(f"模型上传成功: {url}")
        
    elif args.action == "download":
        version = args.version_tag or "main"
        path = manager.download_model(version)
        print(f"模型下载完成: {path}")
        
    elif args.action == "list":
        print("模型版本:")
        versions = manager.list_model_versions()
        for version in versions:
            print(f"  - {version}")
        
        print("\n训练实验:")
        experiments = manager.list_experiments()
        for exp in experiments:
            print(f"  - {exp.get('experiment_name', 'unknown')} ({exp.get('timestamp', 'unknown')})")
    
    elif args.action == "sync":
        if not args.model_path:
            print("错误: 同步工作流需要指定 --model_path")
            return
        
        results = manager.sync_training_workflow(
            args.model_path, 
            args.experiment_name, 
            args.version_tag,
            args.private
        )
        
        print("同步完成:")
        for key, url in results.items():
            print(f"  {key}: {url}")

if __name__ == "__main__":
    main()