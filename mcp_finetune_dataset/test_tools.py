#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP工具功能
"""

from examples.mcp_tools import tool_registry

def test_all_tools():
    """测试所有工具"""
    print("🧪 测试MCP工具功能...\n")
    
    # 测试用例
    test_cases = [
        ("web_search", {"query": "Python机器学习"}),
        ("get_weather", {"city": "北京"}),
        ("list_files", {"path": "./"}),
        ("write_file", {"filename": "test.txt", "content": "Hello MCP!"}),
        ("calculate", {"expression": "125 * 37"}),
        ("get_current_time", {})
    ]
    
    for tool_name, params in test_cases:
        print(f"📋 测试工具: {tool_name}")
        print(f"📥 参数: {params}")
        
        result = tool_registry.execute_tool(tool_name, **params)
        print(f"📤 结果: {result}")
        print("-" * 50)

if __name__ == "__main__":
    test_all_tools()