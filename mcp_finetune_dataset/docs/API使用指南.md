# MCP微调项目 API使用指南

## 概述

本文档介绍如何使用MCP微调项目的FastAPI后端服务。该服务提供了模型推理、训练管理、工具调用等功能的REST API接口。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式1：直接运行
python start_api.py

# 方式2：指定参数
python start_api.py --host 0.0.0.0 --port 8000 --reload

# 方式3：使用uvicorn直接运行
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口详解

### 基础接口

#### 1. 健康检查

```http
GET /health
```

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00",
  "model_loaded": true,
  "training_status": false
}
```

#### 2. 服务状态

```http
GET /status
```

**响应示例：**
```json
{
  "model_loaded": true,
  "model_path": "/path/to/model",
  "training_status": {
    "is_training": false,
    "progress": 0,
    "message": ""
  },
  "available_tools": ["web_search", "get_weather", "calculate"],
  "hf_manager_available": true
}
```

### 模型管理

#### 1. 加载模型

```http
POST /model/load
Content-Type: application/json

{
  "model_path": "/path/to/model",
  "base_model_name": "Qwen/Qwen2-7B-Instruct"  // LoRA模型需要
}
```

#### 2. 获取模型信息

```http
GET /model/info
```

**响应示例：**
```json
{
  "model_path": "/path/to/model",
  "base_model_name": "Qwen/Qwen2-7B-Instruct",
  "model_type": "LoRA",
  "loaded_at": "2024-01-20T10:30:00"
}
```

### 推理接口

#### 1. 聊天接口

```http
POST /chat
Content-Type: application/json

{
  "messages": [
    {"role": "system", "content": "你是一个有用的AI助手"},
    {"role": "user", "content": "你好，请介绍一下自己"}
  ],
  "max_length": 2048,
  "temperature": 0.7,
  "system_prompt": "你是一个专业的AI助手"
}
```

**响应示例：**
```json
{
  "response": "你好！我是一个AI助手，可以帮助你解答问题...",
  "timestamp": "2024-01-20T10:30:00"
}
```

#### 2. 简单聊天接口

```http
POST /chat/simple
Content-Type: application/json

{
  "text": "今天天气怎么样？",
  "system_prompt": "你是一个天气助手"
}
```

**响应示例：**
```json
{
  "user_input": "今天天气怎么样？",
  "assistant_response": "我需要查询天气信息...",
  "tool_calls": [
    {
      "name": "get_weather",
      "arguments": {"location": "北京"}
    }
  ],
  "tool_results": [
    {"temperature": "20°C", "condition": "晴天"}
  ],
  "final_response": "今天北京天气晴朗，温度20°C",
  "timestamp": "2024-01-20T10:30:00"
}
```

### 工具调用

#### 1. 获取可用工具

```http
GET /tools
```

**响应示例：**
```json
{
  "tools": ["web_search", "get_weather", "calculate"],
  "tool_schemas": {
    "web_search": {
      "name": "web_search",
      "description": "搜索网络信息",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "搜索查询"}
        },
        "required": ["query"]
      }
    }
  }
}
```

#### 2. 执行工具

```http
POST /tools/execute
Content-Type: application/json

{
  "tool_name": "calculate",
  "arguments": {
    "expression": "2 + 3 * 4"
  }
}
```

**响应示例：**
```json
{
  "tool_name": "calculate",
  "arguments": {"expression": "2 + 3 * 4"},
  "result": 14,
  "timestamp": "2024-01-20T10:30:00"
}
```

### 训练管理

#### 1. 开始训练

```http
POST /training/start
Content-Type: application/json

{
  "config_updates": {
    "num_epochs": 5,
    "learning_rate": 1e-5
  },
  "dataset_path": "/path/to/dataset"
}
```

#### 2. 获取训练状态

```http
GET /training/status
```

**响应示例：**
```json
{
  "is_training": true,
  "progress": 45,
  "message": "训练进度: 45%"
}
```

#### 3. 停止训练

```http
POST /training/stop
```

### 配置管理

#### 1. 获取配置

```http
GET /config
```

#### 2. 更新配置

```http
POST /config/update
Content-Type: application/json

{
  "model": {
    "max_length": 4096
  },
  "training": {
    "batch_size": 8
  }
}
```

### HuggingFace管理

#### 1. 获取HF状态

```http
GET /huggingface/status
```

#### 2. 上传模型到HF

```http
POST /huggingface/upload
```

## Python客户端示例

### 基础使用

```python
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 1. 检查服务状态
response = requests.get(f"{BASE_URL}/health")
print("服务状态:", response.json())

# 2. 加载模型
load_data = {
    "model_path": "/path/to/your/model",
    "base_model_name": "Qwen/Qwen2-7B-Instruct"
}
response = requests.post(f"{BASE_URL}/model/load", json=load_data)
print("模型加载:", response.json())

# 3. 简单聊天
chat_data = {
    "text": "你好，请介绍一下自己",
    "system_prompt": "你是一个有用的AI助手"
}
response = requests.post(f"{BASE_URL}/chat/simple", json=chat_data)
print("聊天响应:", response.json())
```

### 完整对话示例

```python
import requests

class MCPAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def chat(self, messages, max_length=2048, temperature=0.7):
        """聊天接口"""
        data = {
            "messages": messages,
            "max_length": max_length,
            "temperature": temperature
        }
        response = requests.post(f"{self.base_url}/chat", json=data)
        return response.json()
    
    def simple_chat(self, text, system_prompt=None):
        """简单聊天接口"""
        data = {"text": text}
        if system_prompt:
            data["system_prompt"] = system_prompt
        response = requests.post(f"{self.base_url}/chat/simple", json=data)
        return response.json()
    
    def execute_tool(self, tool_name, **arguments):
        """执行工具"""
        data = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        response = requests.post(f"{self.base_url}/tools/execute", json=data)
        return response.json()
    
    def get_status(self):
        """获取状态"""
        response = requests.get(f"{self.base_url}/status")
        return response.json()

# 使用示例
client = MCPAPIClient()

# 检查状态
status = client.get_status()
print(f"模型已加载: {status['model_loaded']}")

# 简单对话
result = client.simple_chat("计算 15 * 23 的结果")
print(f"用户输入: {result['user_input']}")
print(f"最终回复: {result['final_response']}")

# 多轮对话
messages = [
    {"role": "system", "content": "你是一个数学助手"},
    {"role": "user", "content": "请解释什么是斐波那契数列"}
]
response = client.chat(messages)
print(f"回复: {response['response']}")
```

## 错误处理

### 常见错误码

- `404`: 资源未找到（如模型未加载）
- `400`: 请求参数错误
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### Python错误处理示例

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, method="GET", **kwargs):
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
        if hasattr(e.response, 'json'):
            error_detail = e.response.json().get('detail', '未知错误')
            print(f"错误详情: {error_detail}")
    except RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    
    return None

# 使用示例
result = safe_api_call("http://localhost:8000/model/info")
if result:
    print("模型信息:", result)
else:
    print("获取模型信息失败")
```

## 部署建议

### 生产环境部署

```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用Docker部署
docker build -t mcp-api .
docker run -p 8000:8000 mcp-api
```

### 性能优化

1. **模型预加载**: 在服务启动时预加载常用模型
2. **缓存机制**: 对频繁请求的结果进行缓存
3. **异步处理**: 对耗时操作使用后台任务
4. **负载均衡**: 使用多个工作进程处理请求

### 安全考虑

1. **API认证**: 添加API密钥或JWT认证
2. **请求限制**: 实现请求频率限制
3. **输入验证**: 严格验证所有输入参数
4. **HTTPS**: 在生产环境中使用HTTPS

## 常见问题

### Q: 模型加载失败怎么办？
A: 检查模型路径是否正确，确保有足够的内存和GPU资源。

### Q: 训练过程中出现错误？
A: 查看日志信息，检查数据集格式和配置参数。

### Q: API响应很慢？
A: 考虑使用更小的模型，或者增加服务器资源。

### Q: 如何添加自定义工具？
A: 在`mcp_tools.py`中注册新工具，然后重启服务。

## 更多资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Uvicorn部署指南](https://www.uvicorn.org/deployment/)
- [项目GitHub仓库](https://github.com/aidencck/inference_mcp)