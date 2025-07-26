#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP模型推理脚本
用于测试训练好的MCP工具调用模型
"""

import json
import torch
import yaml
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import logging
from typing import Dict, Any, List, Optional
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from examples.mcp_tools import tool_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPInference:
    """MCP模型推理器"""
    
    def __init__(self, model_path: str, base_model_name: Optional[str] = None):
        # 处理相对路径
        if not os.path.isabs(model_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            model_path = os.path.join(project_dir, model_path)
            
        self.model_path = model_path
        self.base_model_name = base_model_name
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """加载模型和分词器"""
        logger.info(f"加载模型: {self.model_path}")
        
        try:
            # 检查是否是LoRA模型
            adapter_config_path = os.path.join(self.model_path, "adapter_config.json")
            is_lora_model = os.path.exists(adapter_config_path)
            
            if is_lora_model:
                logger.info("检测到LoRA模型，加载基础模型和适配器")
                
                # 读取适配器配置获取基础模型名称
                with open(adapter_config_path, 'r') as f:
                    adapter_config = json.load(f)
                    base_model = adapter_config.get('base_model_name_or_path', self.base_model_name)
                
                if not base_model:
                    raise ValueError("无法确定基础模型名称，请提供base_model_name参数")
                
                # 加载基础模型
                self.tokenizer = AutoTokenizer.from_pretrained(base_model)
                base_model_obj = AutoModelForCausalLM.from_pretrained(
                    base_model,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                # 加载LoRA适配器
                self.model = PeftModel.from_pretrained(base_model_obj, self.model_path)
                
            else:
                logger.info("加载完整微调模型")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
            
            # 设置pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def generate_response(self, messages: List[Dict[str, str]], max_length: int = 2048, temperature: float = 0.7) -> str:
        """生成响应"""
        # 格式化输入
        formatted_input = self.format_messages(messages)
        
        # 编码输入
        inputs = self.tokenizer(
            formatted_input,
            return_tensors="pt",
            truncation=True,
            max_length=max_length
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # 生成响应
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # 解码输出
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取新生成的部分
        input_text = self.tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)
        response = generated_text[len(input_text):].strip()
        
        return response
    
    def format_messages(self, messages: List[Dict[str, str]]) -> str:
        """格式化消息"""
        formatted_text = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted_text += f"<|system|>\n{content}\n\n"
            elif role == "user":
                formatted_text += f"<|user|>\n{content}\n\n"
            elif role == "assistant":
                formatted_text += f"<|assistant|>\n{content}\n\n"
        
        # 添加助手开始标记
        if not formatted_text.endswith("<|assistant|>\n"):
            formatted_text += "<|assistant|>\n"
        
        return formatted_text
    
    def parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """解析工具调用"""
        tool_calls = []
        
        # 查找工具调用模式
        import re
        tool_call_pattern = r'<\|tool_call\|>\s*([^(]+)\(([^)]+)\)'
        matches = re.findall(tool_call_pattern, response)
        
        for match in matches:
            tool_name = match[0].strip()
            args_str = match[1].strip()
            
            try:
                # 尝试解析参数
                args = json.loads(args_str)
                tool_calls.append({
                    "name": tool_name,
                    "arguments": args
                })
            except json.JSONDecodeError:
                logger.warning(f"无法解析工具调用参数: {args_str}")
        
        return tool_calls
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """执行工具调用"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            arguments = tool_call["arguments"]
            
            try:
                result = tool_registry.execute_tool(tool_name, **arguments)
                results.append(result)
                logger.info(f"工具调用成功: {tool_name} -> {result[:100]}...")
            except Exception as e:
                error_msg = f"工具调用失败: {tool_name}, 错误: {str(e)}"
                results.append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def chat(self, user_input: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """聊天接口"""
        if system_prompt is None:
            system_prompt = "你是一个能够正确调用MCP工具的AI助手。当用户需要获取信息或执行操作时，你应该选择合适的MCP工具并正确调用。"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 生成初始响应
        response = self.generate_response(messages)
        
        # 解析工具调用
        tool_calls = self.parse_tool_calls(response)
        
        result = {
            "user_input": user_input,
            "assistant_response": response,
            "tool_calls": tool_calls,
            "tool_results": [],
            "final_response": response
        }
        
        # 如果有工具调用，执行并生成最终响应
        if tool_calls:
            tool_results = self.execute_tool_calls(tool_calls)
            result["tool_results"] = tool_results
            
            # 构建包含工具结果的消息
            messages.append({"role": "assistant", "content": response})
            
            for i, (tool_call, tool_result) in enumerate(zip(tool_calls, tool_results)):
                messages.append({
                    "role": "tool",
                    "content": tool_result
                })
            
            # 生成最终响应
            final_response = self.generate_response(messages)
            result["final_response"] = final_response
        
        return result

def test_model(model_path: str, base_model_name: Optional[str] = None):
    """测试模型"""
    logger.info("开始测试MCP模型")
    
    # 创建推理器
    inference = MCPInference(model_path, base_model_name)
    
    # 测试用例
    test_cases = [
        "请帮我搜索Python机器学习的最新信息",
        "查看北京的天气情况",
        "列出当前目录的文件",
        "创建一个hello.txt文件，内容是Hello MCP!",
        "计算125乘以37的结果",
        "获取当前时间"
    ]
    
    print("\n" + "="*50)
    print("MCP模型测试结果")
    print("="*50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case}")
        print("-" * 30)
        
        try:
            result = inference.chat(test_case)
            
            print(f"助手响应: {result['assistant_response']}")
            
            if result['tool_calls']:
                print(f"工具调用: {len(result['tool_calls'])} 个")
                for j, tool_call in enumerate(result['tool_calls']):
                    print(f"  {j+1}. {tool_call['name']}({tool_call['arguments']})")
                
                print(f"工具结果: {result['tool_results']}")
                print(f"最终响应: {result['final_response']}")
            
        except Exception as e:
            print(f"测试失败: {e}")
        
        print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP模型推理测试")
    parser.add_argument("--model_path", type=str, required=True, help="模型路径")
    parser.add_argument("--base_model", type=str, help="基础模型名称（LoRA模型需要）")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        # 交互式模式
        inference = MCPInference(args.model_path, args.base_model)
        
        print("MCP模型交互式测试")
        print("输入 'quit' 退出")
        print("-" * 30)
        
        while True:
            user_input = input("\n用户: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                break
            
            if not user_input:
                continue
            
            try:
                result = inference.chat(user_input)
                print(f"\n助手: {result['final_response']}")
                
                if result['tool_calls']:
                    print(f"\n[调用了 {len(result['tool_calls'])} 个工具]")
                
            except Exception as e:
                print(f"\n错误: {e}")
    else:
        # 批量测试模式
        test_model(args.model_path, args.base_model)