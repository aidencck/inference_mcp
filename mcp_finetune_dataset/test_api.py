#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP API 测试脚本
用于测试FastAPI服务的各个功能
"""

import requests
import json
import time
from typing import Dict, Any

class MCPAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ API连接成功")
                print(f"   响应: {response.json()}")
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API连接异常: {e}")
            return False
    
    def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ 健康检查通过")
                print(f"   状态: {data['status']}")
                print(f"   模型已加载: {data['model_loaded']}")
                print(f"   训练状态: {data['training_status']}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_get_status(self) -> Dict[str, Any]:
        """测试获取状态"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ 状态获取成功")
                print(f"   模型已加载: {data['model_loaded']}")
                print(f"   可用工具: {data['available_tools']}")
                print(f"   HF管理器: {data['hf_manager_available']}")
                return data
            else:
                print(f"❌ 状态获取失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 状态获取异常: {e}")
            return {}
    
    def test_get_tools(self) -> bool:
        """测试获取工具列表"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            if response.status_code == 200:
                data = response.json()
                print("✅ 工具列表获取成功")
                print(f"   可用工具: {data['tools']}")
                print(f"   工具数量: {len(data['tools'])}")
                return True
            else:
                print(f"❌ 工具列表获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 工具列表获取异常: {e}")
            return False
    
    def test_execute_tool(self, tool_name: str = "calculate", arguments: Dict[str, Any] = None) -> bool:
        """测试工具执行"""
        if arguments is None:
            arguments = {"expression": "2 + 3 * 4"}
        
        try:
            data = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            response = self.session.post(f"{self.base_url}/tools/execute", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 工具 '{tool_name}' 执行成功")
                print(f"   参数: {result['arguments']}")
                print(f"   结果: {result['result']}")
                return True
            else:
                print(f"❌ 工具执行失败: {response.status_code}")
                if response.content:
                    print(f"   错误: {response.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 工具执行异常: {e}")
            return False
    
    def test_load_model(self, model_path: str, base_model_name: str = None) -> bool:
        """测试模型加载"""
        try:
            data = {"model_path": model_path}
            if base_model_name:
                data["base_model_name"] = base_model_name
            
            response = self.session.post(f"{self.base_url}/model/load", json=data)
            if response.status_code == 200:
                result = response.json()
                print("✅ 模型加载成功")
                print(f"   消息: {result['message']}")
                print(f"   模型路径: {result['model_path']}")
                return True
            else:
                print(f"❌ 模型加载失败: {response.status_code}")
                if response.content:
                    print(f"   错误: {response.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 模型加载异常: {e}")
            return False
    
    def test_get_model_info(self) -> bool:
        """测试获取模型信息"""
        try:
            response = self.session.get(f"{self.base_url}/model/info")
            if response.status_code == 200:
                data = response.json()
                print("✅ 模型信息获取成功")
                print(f"   模型路径: {data['model_path']}")
                print(f"   基础模型: {data.get('base_model_name', 'N/A')}")
                print(f"   模型类型: {data['model_type']}")
                return True
            elif response.status_code == 404:
                print("⚠️  未加载模型")
                return False
            else:
                print(f"❌ 模型信息获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 模型信息获取异常: {e}")
            return False
    
    def test_simple_chat(self, text: str = "你好，请介绍一下自己") -> bool:
        """测试简单聊天"""
        try:
            data = {
                "text": text,
                "system_prompt": "你是一个有用的AI助手"
            }
            response = self.session.post(f"{self.base_url}/chat/simple", json=data)
            if response.status_code == 200:
                result = response.json()
                print("✅ 简单聊天测试成功")
                print(f"   用户输入: {result['user_input']}")
                print(f"   助手回复: {result['assistant_response'][:100]}...")
                print(f"   工具调用: {len(result.get('tool_calls', []))} 个")
                return True
            elif response.status_code == 404:
                print("⚠️  模型未加载，无法进行聊天")
                return False
            else:
                print(f"❌ 简单聊天失败: {response.status_code}")
                if response.content:
                    print(f"   错误: {response.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 简单聊天异常: {e}")
            return False
    
    def test_chat(self) -> bool:
        """测试聊天接口"""
        try:
            messages = [
                {"role": "system", "content": "你是一个数学助手"},
                {"role": "user", "content": "请计算 15 * 23 的结果"}
            ]
            data = {
                "messages": messages,
                "max_length": 1024,
                "temperature": 0.7
            }
            response = self.session.post(f"{self.base_url}/chat", json=data)
            if response.status_code == 200:
                result = response.json()
                print("✅ 聊天接口测试成功")
                print(f"   回复: {result['response'][:100]}...")
                return True
            elif response.status_code == 404:
                print("⚠️  模型未加载，无法进行聊天")
                return False
            else:
                print(f"❌ 聊天接口失败: {response.status_code}")
                if response.content:
                    print(f"   错误: {response.json().get('detail', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ 聊天接口异常: {e}")
            return False
    
    def test_get_config(self) -> bool:
        """测试获取配置"""
        try:
            response = self.session.get(f"{self.base_url}/config")
            if response.status_code == 200:
                data = response.json()
                print("✅ 配置获取成功")
                print(f"   模型配置: {data.get('model', {}).get('name', 'N/A')}")
                print(f"   训练配置: batch_size={data.get('training', {}).get('batch_size', 'N/A')}")
                return True
            else:
                print(f"❌ 配置获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 配置获取异常: {e}")
            return False
    
    def test_training_status(self) -> bool:
        """测试训练状态"""
        try:
            response = self.session.get(f"{self.base_url}/training/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ 训练状态获取成功")
                print(f"   正在训练: {data['is_training']}")
                print(f"   进度: {data['progress']}%")
                print(f"   消息: {data['message']}")
                return True
            else:
                print(f"❌ 训练状态获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 训练状态获取异常: {e}")
            return False
    
    def test_hf_status(self) -> bool:
        """测试HuggingFace状态"""
        try:
            response = self.session.get(f"{self.base_url}/huggingface/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ HuggingFace状态获取成功")
                print(f"   可用: {data['available']}")
                if data['available']:
                    print(f"   已认证: {data.get('authenticated', False)}")
                else:
                    print(f"   消息: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ HuggingFace状态获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ HuggingFace状态获取异常: {e}")
            return False
    
    def run_all_tests(self, model_path: str = None) -> Dict[str, bool]:
        """运行所有测试"""
        print("🚀 开始运行MCP API测试套件\n")
        
        results = {}
        
        # 基础连接测试
        print("=== 基础连接测试 ===")
        results['connection'] = self.test_connection()
        results['health'] = self.test_health_check()
        results['status'] = bool(self.test_get_status())
        print()
        
        # 工具测试
        print("=== 工具功能测试 ===")
        results['tools_list'] = self.test_get_tools()
        results['tool_execute'] = self.test_execute_tool()
        print()
        
        # 配置测试
        print("=== 配置管理测试 ===")
        results['config'] = self.test_get_config()
        results['training_status'] = self.test_training_status()
        results['hf_status'] = self.test_hf_status()
        print()
        
        # 模型测试
        print("=== 模型管理测试 ===")
        if model_path:
            results['model_load'] = self.test_load_model(model_path)
            time.sleep(1)  # 等待模型加载
        
        results['model_info'] = self.test_get_model_info()
        print()
        
        # 推理测试（需要模型已加载）
        print("=== 推理功能测试 ===")
        results['simple_chat'] = self.test_simple_chat()
        results['chat'] = self.test_chat()
        print()
        
        # 测试结果汇总
        print("=== 测试结果汇总 ===")
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
        
        print(f"\n📊 测试完成: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查服务状态")
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP API测试工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--model-path", help="测试用模型路径")
    parser.add_argument("--test", choices=[
        'connection', 'health', 'status', 'tools', 'config', 
        'model', 'chat', 'all'
    ], default='all', help="指定测试类型")
    
    args = parser.parse_args()
    
    tester = MCPAPITester(args.url)
    
    if args.test == 'all':
        tester.run_all_tests(args.model_path)
    elif args.test == 'connection':
        tester.test_connection()
    elif args.test == 'health':
        tester.test_health_check()
    elif args.test == 'status':
        tester.test_get_status()
    elif args.test == 'tools':
        tester.test_get_tools()
        tester.test_execute_tool()
    elif args.test == 'config':
        tester.test_get_config()
    elif args.test == 'model':
        if args.model_path:
            tester.test_load_model(args.model_path)
        tester.test_get_model_info()
    elif args.test == 'chat':
        tester.test_simple_chat()
        tester.test_chat()

if __name__ == "__main__":
    main()