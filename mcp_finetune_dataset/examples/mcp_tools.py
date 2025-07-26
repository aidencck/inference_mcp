#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具定义示例
定义了各种MCP工具的接口和功能
"""

import json
import requests
import os
from typing import Dict, Any, List
from datetime import datetime

class MCPToolRegistry:
    """MCP工具注册表"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool("web_search", self.web_search)
        self.register_tool("get_weather", self.get_weather)
        self.register_tool("list_files", self.list_files)
        self.register_tool("write_file", self.write_file)
        self.register_tool("read_file", self.read_file)
        self.register_tool("calculate", self.calculate)
        self.register_tool("get_current_time", self.get_current_time)
    
    def register_tool(self, name: str, func):
        """注册工具"""
        self.tools[name] = func
    
    def get_tool_schema(self) -> List[Dict]:
        """获取所有工具的schema定义"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "搜索互联网内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询词"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "列出指定目录下的文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "目录路径"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "文件名"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容"
                            }
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "执行数学计算",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
    
    def web_search(self, query: str) -> str:
        """网络搜索工具"""
        # 这里应该调用真实的搜索API
        # 为了示例，返回模拟结果
        return f"搜索结果：关于'{query}'的相关信息...\n1. 相关文章标题1\n2. 相关文章标题2\n3. 相关文章标题3"
    
    def get_weather(self, city: str) -> str:
        """获取天气信息"""
        # 模拟天气数据
        weather_data = {
            "北京": "北京：晴，25°C",
            "上海": "上海：多云，27°C",
            "广州": "广州：小雨，23°C",
            "深圳": "深圳：晴，28°C"
        }
        return weather_data.get(city, f"{city}：天气信息未知")
    
    def list_files(self, path: str) -> str:
        """列出文件"""
        try:
            files = os.listdir(path)
            if not files:
                return f"目录 {path} 为空"
            
            result = f"目录 {path} 下的文件：\n"
            for file in files:
                file_path = os.path.join(path, file)
                if os.path.isdir(file_path):
                    result += f"📁 {file}/\n"
                else:
                    result += f"📄 {file}\n"
            return result
        except Exception as e:
            return f"无法访问目录 {path}: {str(e)}"
    
    def write_file(self, filename: str, content: str) -> str:
        """写入文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件 {filename} 写入成功"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
    
    def read_file(self, filename: str) -> str:
        """读取文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"文件 {filename} 内容：\n{content}"
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    def calculate(self, expression: str) -> str:
        """数学计算"""
        try:
            # 安全的数学计算
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return "表达式包含不允许的字符"
            
            result = eval(expression)
            return f"计算结果：{expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def get_current_time(self) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """执行工具"""
        if tool_name not in self.tools:
            return f"未知工具: {tool_name}"
        
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return f"工具执行错误: {str(e)}"

# 全局工具注册表实例
tool_registry = MCPToolRegistry()