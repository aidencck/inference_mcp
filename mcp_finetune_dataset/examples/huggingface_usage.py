#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HuggingFace管理器使用示例
展示如何使用HuggingFace管理器进行模型和配置的版本管理
"""

import os
import sys
import logging
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from huggingface_manager import HuggingFaceManager

# 设置日志
logging.basicConfig(level=logging.INFO)
"""
日志配置说明文档:

1. 基础配置
   - 默认级别: INFO
   - 日志格式: 时间戳 - 记录器名称 - 级别 - 消息内容
   - 时间戳格式: YYYY-MM-DD HH:MM:SS
   - 输出方式: 同时输出到控制台和文件(huggingface_manager.log)

2. 组件特定日志级别
   - urllib3: WARNING (减少网络请求日志)
   - git: WARNING (减少git操作日志)
   - huggingface_hub: INFO (保留重要的hub交互信息)

3. 环境变量控制
   - DEBUG=1: 所有记录器设置为DEBUG级别
   - PRODUCTION=1: 所有记录器设置为WARNING级别

4. 日志文件位置
   - 默认路径: ./huggingface_manager.log
   - 文件编码: UTF-8

5. 日志格式示例:
   2024-03-15 10:30:45 - huggingface_manager - INFO - 开始上传模型
"""

# Configure basic logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def example_upload_model():
    """示例：上传训练好的模型"""
    print("=" * 60)
    print("示例1: 上传训练好的模型")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    # 模型路径（假设已经训练完成）
    model_path = "../mcp_finetuned_model"
    
    if not os.path.exists(model_path):
        print(f"模型路径不存在: {model_path}")
        print("请先运行训练脚本生成模型")
        return
    
    try:
        # 创建仓库
        manager.create_repositories(private=True)
        
        # 上传模型
        model_url = manager.upload_model(
            model_path=model_path,
            version_tag="v1.0.0",
            commit_message="Upload initial MCP fine-tuned model"
        )
        
        print(f"模型上传成功: {model_url}")
        
    except Exception as e:
        print(f"上传失败: {e}")

def example_upload_config():
    """示例：上传训练配置"""
    print("=" * 60)
    print("示例2: 上传训练配置")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    try:
        # 上传配置
        config_url = manager.upload_training_config(
            config_data=manager.config,
            experiment_name="baseline_experiment"
        )
        
        print(f"配置上传成功: {config_url}")
        
    except Exception as e:
        print(f"上传失败: {e}")

def example_sync_workflow():
    """示例：同步完整训练工作流"""
    print("=" * 60)
    print("示例3: 同步完整训练工作流")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    # 模型路径
    model_path = "../mcp_finetuned_model"
    
    if not os.path.exists(model_path):
        print(f"模型路径不存在: {model_path}")
        print("请先运行训练脚本生成模型")
        return
    
    try:
        # 同步完整工作流
        results = manager.sync_training_workflow(
            model_path=model_path,
            experiment_name="complete_workflow_demo",
            version_tag="v1.0.0-demo",
            private=True
        )
        
        print("同步完成:")
        for key, url in results.items():
            print(f"  {key}: {url}")
            
    except Exception as e:
        print(f"同步失败: {e}")

def example_download_model():
    """示例：下载模型"""
    print("=" * 60)
    print("示例4: 下载模型")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    try:
        # 下载模型
        downloaded_path = manager.download_model(
            version_tag="main",
            local_dir="./downloaded_model_demo"
        )
        
        print(f"模型下载完成: {downloaded_path}")
        
    except Exception as e:
        print(f"下载失败: {e}")

def example_list_versions():
    """示例：列出版本和实验"""
    print("=" * 60)
    print("示例5: 列出版本和实验")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    try:
        # 列出模型版本
        print("模型版本:")
        versions = manager.list_model_versions()
        for version in versions:
            print(f"  - {version}")
        
        # 列出实验
        print("\n训练实验:")
        experiments = manager.list_experiments()
        for exp in experiments:
            print(f"  - {exp.get('experiment_name', 'unknown')} ({exp.get('timestamp', 'unknown')})")
            print(f"    模型: {exp.get('model_name', 'unknown')}")
            print(f"    基础模型: {exp.get('base_model', 'unknown')}")
            
    except Exception as e:
        print(f"列出失败: {e}")

def example_model_card_generation():
    """示例：生成模型卡片"""
    print("=" * 60)
    print("示例6: 生成模型卡片")
    print("=" * 60)
    
    # 创建管理器
    manager = HuggingFaceManager("../config.yaml")
    
    # 模型路径
    model_path = "../mcp_finetuned_model"
    
    if not os.path.exists(model_path):
        print(f"模型路径不存在: {model_path}")
        print("请先运行训练脚本生成模型")
        return
    
    try:
        # 生成模型卡片
        model_card = manager.generate_model_card(model_path, "v1.0.0")
        
        print("生成的模型卡片:")
        print("-" * 40)
        print(model_card[:1000] + "..." if len(model_card) > 1000 else model_card)
        print("-" * 40)
        
        # 保存到文件
        with open("./demo_model_card.md", 'w', encoding='utf-8') as f:
            f.write(model_card)
        
        print("模型卡片已保存到: ./demo_model_card.md")
        
    except Exception as e:
        print(f"生成失败: {e}")

def interactive_demo():
    """交互式演示"""
    print("=" * 60)
    print("HuggingFace管理器交互式演示")
    print("=" * 60)
    
    examples = {
        "1": ("上传模型", example_upload_model),
        "2": ("上传配置", example_upload_config),
        "3": ("同步工作流", example_sync_workflow),
        "4": ("下载模型", example_download_model),
        "5": ("列出版本", example_list_versions),
        "6": ("生成模型卡片", example_model_card_generation),
    }
    
    while True:
        print("\n请选择要运行的示例:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print("  q. 退出")
        
        choice = input("\n请输入选择 (1-6 或 q): ").strip().lower()
        
        if choice == 'q':
            print("退出演示")
            break
        elif choice in examples:
            name, func = examples[choice]
            print(f"\n运行示例: {name}")
            try:
                func()
            except KeyboardInterrupt:
                print("\n示例被中断")
            except Exception as e:
                print(f"示例运行出错: {e}")
            
            input("\n按回车键继续...")
        else:
            print("无效选择，请重试")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace管理器使用示例")
    parser.add_argument("--example", type=str, choices=["1", "2", "3", "4", "5", "6"],
                       help="运行特定示例 (1-6)")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_demo()
    elif args.example:
        examples = {
            "1": example_upload_model,
            "2": example_upload_config,
            "3": example_sync_workflow,
            "4": example_download_model,
            "5": example_list_versions,
            "6": example_model_card_generation,
        }
        examples[args.example]()
    else:
        print("HuggingFace管理器使用示例")
        print("")
        print("使用方法:")
        print("  python huggingface_usage.py --interactive    # 交互式模式")
        print("  python huggingface_usage.py --example 1     # 运行特定示例")
        print("")
        print("可用示例:")
        print("  1. 上传模型")
        print("  2. 上传配置")
        print("  3. 同步工作流")
        print("  4. 下载模型")
        print("  5. 列出版本")
        print("  6. 生成模型卡片")

if __name__ == "__main__":
    main()