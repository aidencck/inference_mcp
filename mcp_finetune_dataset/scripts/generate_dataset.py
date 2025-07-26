#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成MCP工具调用训练数据集
"""

import json
import random
import sys
import os
from typing import List, Dict, Any

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from examples.mcp_tools import tool_registry

class MCPDatasetGenerator:
    """MCP数据集生成器"""
    
    def __init__(self):
        self.system_prompt = "你是一个能够正确调用MCP工具的AI助手。当用户需要获取信息或执行操作时，你应该选择合适的MCP工具并正确调用。"
        
        # 定义各种用户请求模板
        self.request_templates = {
            "web_search": [
                "请帮我搜索关于{topic}的信息",
                "我想了解{topic}的最新动态",
                "搜索一下{topic}相关内容",
                "查找{topic}的资料"
            ],
            "get_weather": [
                "请帮我查看{city}的天气",
                "我想知道{city}今天天气怎么样",
                "获取{city}的天气信息",
                "{city}的天气如何？"
            ],
            "list_files": [
                "请帮我查看{path}目录下的文件",
                "列出{path}中的所有文件",
                "显示{path}目录内容",
                "我想看看{path}里有什么文件"
            ],
            "write_file": [
                "请帮我创建一个名为{filename}的文件，内容是{content}",
                "写入文件{filename}，内容：{content}",
                "创建文件{filename}并写入：{content}"
            ],
            "calculate": [
                "请帮我计算{expression}",
                "计算一下{expression}的结果",
                "{expression}等于多少？",
                "帮我算算{expression}"
            ]
        }
        
        # 示例数据
        self.example_data = {
            "topics": ["Python机器学习", "人工智能发展", "区块链技术", "云计算", "大数据分析"],
            "cities": ["北京", "上海", "广州", "深圳", "杭州"],
            "paths": ["./", "./data", "./models", "./scripts", "./docs"],
            "filenames": ["test.txt", "data.json", "config.yaml", "readme.md", "script.py"],
            "contents": ["Hello World", "这是测试内容", "配置信息", "项目说明", "print('Hello')"],
            "expressions": ["125 * 37", "256 + 128", "1024 / 8", "15 * 15", "100 - 25"]
        }
    
    def generate_conversation(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个对话样本"""
        
        # 生成用户请求
        template = random.choice(self.request_templates[tool_name])
        user_message = template.format(**params)
        
        # 生成助手响应（工具调用前）
        assistant_intro = f"我来帮您{self._get_action_description(tool_name, params)}。"
        
        # 生成工具调用
        tool_call = {
            "id": f"call_{random.randint(1000, 9999)}",
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(params, ensure_ascii=False)
            }
        }
        
        # 执行工具获取结果
        tool_result = tool_registry.execute_tool(tool_name, **params)
        
        # 生成最终助手响应
        final_response = self._generate_final_response(tool_name, params, tool_result)
        
        # 构建完整对话
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                },
                {
                    "role": "assistant",
                    "content": assistant_intro,
                    "tool_calls": [tool_call]
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                },
                {
                    "role": "assistant",
                    "content": final_response
                }
            ]
        }
        
        return conversation
    
    def _get_action_description(self, tool_name: str, params: Dict[str, Any]) -> str:
        """获取动作描述"""
        descriptions = {
            "web_search": f"搜索关于{params.get('query', '')}的信息",
            "get_weather": f"获取{params.get('city', '')}的天气信息",
            "list_files": f"查看{params.get('path', '')}目录下的文件",
            "write_file": f"创建{params.get('filename', '')}文件",
            "calculate": f"计算{params.get('expression', '')}的结果"
        }
        return descriptions.get(tool_name, "处理您的请求")
    
    def _generate_final_response(self, tool_name: str, params: Dict[str, Any], tool_result: str) -> str:
        """生成最终响应"""
        if tool_name == "web_search":
            return f"根据搜索结果，我为您找到了关于{params['query']}的相关信息：\n\n{tool_result}\n\n希望这些信息对您有帮助！"
        elif tool_name == "get_weather":
            return f"{params['city']}的天气信息如下：\n\n{tool_result}\n\n请根据天气情况合理安排出行。"
        elif tool_name == "list_files":
            return f"{params['path']}目录的内容：\n\n{tool_result}\n\n您需要对哪个文件进行操作吗？"
        elif tool_name == "write_file":
            return f"✅ 文件创建成功！\n\n📄 **文件名**：{params['filename']}\n📝 **内容**：{params['content']}\n\n文件已保存在当前目录中。"
        elif tool_name == "calculate":
            return f"🧮 **计算结果**：\n\n{tool_result}\n\n计算完成！"
        else:
            return f"操作完成：\n\n{tool_result}"
    
    def generate_dataset(self, num_samples: int = 100) -> List[Dict[str, Any]]:
        """生成完整数据集"""
        dataset = []
        
        tools_and_params = [
            ("web_search", lambda: {"query": random.choice(self.example_data["topics"])}),
            ("get_weather", lambda: {"city": random.choice(self.example_data["cities"])}),
            ("list_files", lambda: {"path": random.choice(self.example_data["paths"])}),
            ("write_file", lambda: {
                "filename": random.choice(self.example_data["filenames"]),
                "content": random.choice(self.example_data["contents"])
            }),
            ("calculate", lambda: {"expression": random.choice(self.example_data["expressions"])})
        ]
        
        for i in range(num_samples):
            tool_name, param_generator = random.choice(tools_and_params)
            params = param_generator()
            
            conversation = self.generate_conversation(tool_name, params)
            dataset.append(conversation)
        
        return dataset
    
    def save_dataset(self, dataset: List[Dict[str, Any]], output_path: str):
        """保存数据集到JSONL文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"数据集已保存到: {output_path}")
        print(f"总样本数: {len(dataset)}")

if __name__ == "__main__":
    import argparse
    import yaml
    import os
    
    parser = argparse.ArgumentParser(description="生成MCP训练数据集")
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    parser.add_argument("--train_samples", type=int, help="训练样本数量（覆盖配置文件）")
    parser.add_argument("--val_samples", type=int, help="验证样本数量（覆盖配置文件）")
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # 确保配置文件路径正确
    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(project_dir, config_path)
    
    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}")
        exit(1)
    
    print(f"使用配置文件: {config_path}")
    
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 获取数据配置
    data_config = config.get('data', {})
    train_samples = args.train_samples or data_config.get('num_train_samples', 500)
    val_samples = args.val_samples or data_config.get('num_val_samples', 100)
    
    # 获取输出文件路径
    train_file = data_config.get('train_file', './data/mcp_tool_calls.jsonl')
    val_file = data_config.get('validation_file', './data/mcp_validation.jsonl')
    
    # 如果是相对路径，相对于项目根目录
    if not os.path.isabs(train_file):
        train_file = os.path.join(project_dir, train_file)
    if not os.path.isabs(val_file):
        val_file = os.path.join(project_dir, val_file)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(train_file), exist_ok=True)
    os.makedirs(os.path.dirname(val_file), exist_ok=True)
    
    # 创建数据生成器
    generator = MCPDatasetGenerator()
    
    # 生成训练数据集
    train_dataset = generator.generate_dataset(num_samples=train_samples)
    generator.save_dataset(train_dataset, train_file)
    
    # 生成验证数据集
    val_dataset = generator.generate_dataset(num_samples=val_samples)
    generator.save_dataset(val_dataset, val_file)
    
    print("数据集生成完成！")
    print(f"训练数据: {train_file}")
    print(f"验证数据: {val_file}")