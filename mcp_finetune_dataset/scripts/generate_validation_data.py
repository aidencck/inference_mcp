#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成验证数据集
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_dataset import MCPDatasetGenerator

if __name__ == "__main__":
    generator = MCPDatasetGenerator()
    
    # 生成验证数据集
    val_dataset = generator.generate_dataset(num_samples=100)
    generator.save_dataset(val_dataset, "../data/mcp_validation.jsonl")
    
    print("验证数据集生成完成！")