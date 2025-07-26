#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker容器健康检查脚本
用于检查MCP微调项目容器的健康状态
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    try:
        import torch
        import transformers
        import datasets
        print(f"✓ Python环境正常")
        print(f"  - Python版本: {sys.version.split()[0]}")
        print(f"  - PyTorch版本: {torch.__version__}")
        print(f"  - Transformers版本: {transformers.__version__}")
        print(f"  - Datasets版本: {datasets.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Python环境异常: {e}")
        return False

def check_gpu_availability():
    """检查GPU可用性"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            print(f"✓ GPU可用 ({gpu_count}个设备)")
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  - GPU {i}: {gpu_name} ({gpu_memory:.1f}GB)")
            return True
        else:
            print("⚠ GPU不可用，将使用CPU")
            return True  # CPU模式也算正常
    except Exception as e:
        print(f"✗ GPU检查失败: {e}")
        return False

def check_disk_space():
    """检查磁盘空间"""
    try:
        # 检查关键目录的磁盘空间
        critical_paths = [
            '/app',
            '/app/models',
            '/app/.cache',
            '/app/outputs'
        ]
        
        for path in critical_paths:
            if os.path.exists(path):
                stat = os.statvfs(path)
                free_space = stat.f_bavail * stat.f_frsize / 1024**3  # GB
                total_space = stat.f_blocks * stat.f_frsize / 1024**3  # GB
                used_percent = (1 - stat.f_bavail / stat.f_blocks) * 100
                
                if free_space < 1:  # 少于1GB
                    print(f"⚠ {path}: 磁盘空间不足 ({free_space:.1f}GB可用)")
                    return False
                else:
                    print(f"✓ {path}: {free_space:.1f}GB可用 ({used_percent:.1f}%已用)")
        
        return True
    except Exception as e:
        print(f"✗ 磁盘空间检查失败: {e}")
        return False

def check_memory_usage():
    """检查内存使用情况"""
    try:
        import psutil
        
        # 系统内存
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / 1024**3  # GB
        
        if memory_percent > 90:
            print(f"⚠ 系统内存使用率过高: {memory_percent:.1f}% ({memory_available:.1f}GB可用)")
            return False
        else:
            print(f"✓ 系统内存正常: {memory_percent:.1f}%已用 ({memory_available:.1f}GB可用)")
        
        # GPU内存（如果有GPU）
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    gpu_memory_used = torch.cuda.memory_allocated(i) / 1024**3
                    gpu_memory_total = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    gpu_memory_percent = (gpu_memory_used / gpu_memory_total) * 100
                    print(f"✓ GPU {i}内存: {gpu_memory_percent:.1f}%已用 ({gpu_memory_used:.1f}/{gpu_memory_total:.1f}GB)")
        except:
            pass
        
        return True
    except Exception as e:
        print(f"✗ 内存检查失败: {e}")
        return False

def check_network_connectivity():
    """检查网络连接"""
    try:
        import requests
        
        # 检查HuggingFace连接
        try:
            response = requests.get('https://huggingface.co', timeout=10)
            if response.status_code == 200:
                print("✓ HuggingFace网络连接正常")
            else:
                print(f"⚠ HuggingFace连接异常: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠ HuggingFace网络连接失败: {e}")
        
        # 检查PyPI连接
        try:
            response = requests.get('https://pypi.org', timeout=10)
            if response.status_code == 200:
                print("✓ PyPI网络连接正常")
            else:
                print(f"⚠ PyPI连接异常: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠ PyPI网络连接失败: {e}")
        
        return True
    except Exception as e:
        print(f"✗ 网络检查失败: {e}")
        return False

def check_file_permissions():
    """检查文件权限"""
    try:
        # 检查关键目录的读写权限
        critical_dirs = [
            '/app/models',
            '/app/.cache',
            '/app/outputs',
            '/app/logs'
        ]
        
        for dir_path in critical_dirs:
            if os.path.exists(dir_path):
                if os.access(dir_path, os.R_OK | os.W_OK):
                    print(f"✓ {dir_path}: 读写权限正常")
                else:
                    print(f"✗ {dir_path}: 权限不足")
                    return False
            else:
                # 尝试创建目录
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"✓ {dir_path}: 目录已创建")
                except OSError as e:
                    print(f"✗ {dir_path}: 无法创建目录 - {e}")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ 文件权限检查失败: {e}")
        return False

def check_configuration_files():
    """检查配置文件"""
    try:
        config_files = [
            '/app/config.yaml',
            '/app/configs/config.yaml'
        ]
        
        config_found = False
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"✓ 配置文件存在: {config_file}")
                config_found = True
                
                # 尝试解析配置文件
                try:
                    import yaml
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    print(f"✓ 配置文件格式正确")
                except Exception as e:
                    print(f"⚠ 配置文件格式错误: {e}")
                break
        
        if not config_found:
            print("⚠ 未找到配置文件")
        
        return True
    except Exception as e:
        print(f"✗ 配置文件检查失败: {e}")
        return False

def check_process_status():
    """检查关键进程状态"""
    try:
        import psutil
        
        # 检查Python进程
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"✓ 发现 {len(python_processes)} 个Python进程")
        
        return True
    except Exception as e:
        print(f"✗ 进程状态检查失败: {e}")
        return False

def main():
    """主健康检查函数"""
    print("=" * 60)
    print("MCP微调项目容器健康检查")
    print("=" * 60)
    print(f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Python环境", check_python_environment),
        ("GPU可用性", check_gpu_availability),
        ("磁盘空间", check_disk_space),
        ("内存使用", check_memory_usage),
        ("网络连接", check_network_connectivity),
        ("文件权限", check_file_permissions),
        ("配置文件", check_configuration_files),
        ("进程状态", check_process_status)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ {check_name}检查异常: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有检查通过，容器状态健康")
        sys.exit(0)
    else:
        print("✗ 部分检查失败，容器状态异常")
        sys.exit(1)

if __name__ == "__main__":
    main()