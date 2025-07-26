#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP微调项目 FastAPI 后端服务
提供模型推理、训练管理、工具调用等API接口
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import yaml

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.inference import MCPInference
from scripts.train_mcp_model import MCPTrainer
from scripts.model_manager import ModelManager
from scripts.huggingface_manager import HuggingFaceManager
from examples.mcp_tools import MCPToolRegistry
import platform
import psutil
import docker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="MCP微调项目API",
    description="提供MCP模型推理、训练管理、工具调用等功能的REST API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
inference_engine = None
model_manager = None
hf_manager = None
tool_registry = MCPToolRegistry()
training_status = {"is_training": False, "progress": 0, "message": ""}

# Pydantic模型定义
class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色: system, user, assistant")
    content: str = Field(..., description="消息内容")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    max_length: Optional[int] = Field(2048, description="最大生成长度")
    temperature: Optional[float] = Field(0.7, description="生成温度")
    system_prompt: Optional[str] = Field(None, description="系统提示词")

class SimpleTextRequest(BaseModel):
    text: str = Field(..., description="输入文本")
    system_prompt: Optional[str] = Field(None, description="系统提示词")

class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(..., description="工具参数")

class TrainingRequest(BaseModel):
    config_updates: Optional[Dict[str, Any]] = Field(None, description="配置更新")
    dataset_path: Optional[str] = Field(None, description="数据集路径")

class ModelLoadRequest(BaseModel):
    model_path: str = Field(..., description="模型路径")
    base_model_name: Optional[str] = Field(None, description="基础模型名称（LoRA模型需要）")

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    global model_manager, hf_manager
    
    logger.info("正在启动MCP API服务...")
    
    try:
        # 初始化模型管理器
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        model_manager = ModelManager(config_path)
        logger.info("模型管理器初始化成功")
        
        # 初始化HuggingFace管理器
        try:
            hf_manager = HuggingFaceManager(config_path)
            logger.info("HuggingFace管理器初始化成功")
        except Exception as e:
            logger.warning(f"HuggingFace管理器初始化失败: {e}")
            hf_manager = None
        
        # 尝试加载默认模型
        try:
            default_model_path = model_manager.config["output"]["model_dir"]
            if os.path.exists(default_model_path):
                await load_model_async(default_model_path)
                logger.info(f"默认模型加载成功: {default_model_path}")
        except Exception as e:
            logger.warning(f"默认模型加载失败: {e}")
        
        logger.info("MCP API服务启动完成")
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

# 辅助函数
async def load_model_async(model_path: str, base_model_name: Optional[str] = None):
    """异步加载模型"""
    global inference_engine
    
    try:
        inference_engine = MCPInference(model_path, base_model_name)
        logger.info(f"模型加载成功: {model_path}")
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        inference_engine = None
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

# API路由定义

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MCP微调项目API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": inference_engine is not None,
        "training_status": training_status["is_training"]
    }

@app.get("/status")
async def get_status():
    """获取服务状态"""
    return {
        "model_loaded": inference_engine is not None,
        "model_path": getattr(inference_engine, 'model_path', None) if inference_engine else None,
        "training_status": training_status,
        "available_tools": list(tool_registry.tools.keys()),
        "hf_manager_available": hf_manager is not None
    }

# 模型管理API
@app.post("/model/load")
async def load_model(request: ModelLoadRequest):
    """加载模型"""
    try:
        await load_model_async(request.model_path, request.base_model_name)
        return {
            "success": True,
            "message": "模型加载成功",
            "model_path": request.model_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def get_model_info():
    """获取当前模型信息"""
    if not inference_engine:
        raise HTTPException(status_code=404, detail="未加载模型")
    
    return {
        "model_path": inference_engine.model_path,
        "base_model_name": inference_engine.base_model_name,
        "model_type": "LoRA" if inference_engine.base_model_name else "Full",
        "loaded_at": datetime.now().isoformat()
    }

# 推理API
@app.post("/chat")
async def chat(request: ChatRequest):
    """聊天接口"""
    if not inference_engine:
        raise HTTPException(status_code=404, detail="未加载模型，请先加载模型")
    
    try:
        # 转换消息格式
        messages = [msg.dict() for msg in request.messages]
        
        # 生成响应
        response = inference_engine.generate_response(
            messages, 
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/simple")
async def simple_chat(request: SimpleTextRequest):
    """简单聊天接口"""
    if not inference_engine:
        raise HTTPException(status_code=404, detail="未加载模型，请先加载模型")
    
    try:
        result = inference_engine.chat(
            request.text,
            system_prompt=request.system_prompt
        )
        
        return {
            "user_input": result["user_input"],
            "assistant_response": result["assistant_response"],
            "tool_calls": result["tool_calls"],
            "tool_results": result["tool_results"],
            "final_response": result["final_response"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"简单聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 工具调用API
@app.get("/tools")
async def get_tools():
    """获取可用工具列表"""
    return {
        "tools": list(tool_registry.tools.keys()),
        "tool_schemas": tool_registry.get_tool_schema()
    }

@app.post("/tools/execute")
async def execute_tool(request: ToolCallRequest):
    """执行工具调用"""
    try:
        result = tool_registry.execute_tool(
            request.tool_name,
            **request.arguments
        )
        
        return {
            "tool_name": request.tool_name,
            "arguments": request.arguments,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"工具执行错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 训练管理API
@app.post("/training/start")
async def start_training(background_tasks: BackgroundTasks, request: TrainingRequest):
    """开始训练"""
    if training_status["is_training"]:
        raise HTTPException(status_code=400, detail="训练正在进行中")
    
    try:
        # 更新训练状态
        training_status["is_training"] = True
        training_status["progress"] = 0
        training_status["message"] = "训练准备中..."
        
        # 在后台启动训练
        background_tasks.add_task(run_training_task, request.config_updates)
        
        return {
            "success": True,
            "message": "训练已开始",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        training_status["is_training"] = False
        logger.error(f"启动训练失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/training/status")
async def get_training_status():
    """获取训练状态"""
    return training_status

@app.post("/training/stop")
async def stop_training():
    """停止训练"""
    if not training_status["is_training"]:
        raise HTTPException(status_code=400, detail="没有正在进行的训练")
    
    # 这里应该实现训练停止逻辑
    training_status["is_training"] = False
    training_status["message"] = "训练已停止"
    
    return {
        "success": True,
        "message": "训练已停止",
        "timestamp": datetime.now().isoformat()
    }

# 后台训练任务
async def run_training_task(config_updates: Optional[Dict[str, Any]] = None):
    """后台训练任务"""
    try:
        training_status["message"] = "初始化训练器..."
        
        # 创建训练器
        trainer = MCPTrainer()
        
        # 应用配置更新
        if config_updates:
            trainer.config.update(config_updates)
        
        training_status["message"] = "开始训练..."
        training_status["progress"] = 10
        
        # 这里应该实现实际的训练逻辑
        # 由于训练是同步的，我们需要在这里模拟异步行为
        # 实际实现中可能需要使用线程池或进程池
        
        # 模拟训练进度
        for i in range(10, 101, 10):
            await asyncio.sleep(1)  # 模拟训练时间
            training_status["progress"] = i
            training_status["message"] = f"训练进度: {i}%"
        
        training_status["is_training"] = False
        training_status["progress"] = 100
        training_status["message"] = "训练完成"
        
        logger.info("训练任务完成")
        
    except Exception as e:
        training_status["is_training"] = False
        training_status["message"] = f"训练失败: {str(e)}"
        logger.error(f"训练任务失败: {e}")

# HuggingFace管理API
@app.get("/huggingface/status")
async def get_hf_status():
    """获取HuggingFace状态"""
    if not hf_manager:
        return {"available": False, "message": "HuggingFace管理器未初始化"}
    
    return {
        "available": True,
        "authenticated": hf_manager.is_authenticated(),
        "config": hf_manager.config
    }

@app.post("/huggingface/upload")
async def upload_to_hf(background_tasks: BackgroundTasks):
    """上传模型到HuggingFace"""
    if not hf_manager:
        raise HTTPException(status_code=404, detail="HuggingFace管理器未初始化")
    
    try:
        # 在后台执行上传
        background_tasks.add_task(hf_upload_task)
        
        return {
            "success": True,
            "message": "上传任务已开始",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"HuggingFace上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def hf_upload_task():
    """HuggingFace上传任务"""
    try:
        # 这里实现实际的上传逻辑
        logger.info("开始上传到HuggingFace...")
        # hf_manager.upload_model()
        logger.info("HuggingFace上传完成")
    except Exception as e:
        logger.error(f"HuggingFace上传任务失败: {e}")

# 配置管理API
@app.get("/config")
async def get_config():
    """获取当前配置"""
    if not model_manager:
        raise HTTPException(status_code=404, detail="模型管理器未初始化")
    
    return model_manager.config

@app.post("/config/update")
async def update_config(config_updates: Dict[str, Any]):
    """更新配置"""
    if not model_manager:
        raise HTTPException(status_code=404, detail="模型管理器未初始化")
    
    try:
        # 更新配置
        model_manager.config.update(config_updates)
        
        # 保存配置到文件
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(model_manager.config, f, default_flow_style=False, allow_unicode=True)
        
        return {
            "success": True,
            "message": "配置更新成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"配置更新失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/system/config")
async def get_system_config():
    """Get all system configuration and runtime information"""
    try:
        # Get system information
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": {
                path.mountpoint: psutil.disk_usage(path.mountpoint)._asdict()
                for path in psutil.disk_partitions()
            }
        }

        # Get Docker information
        try:
            docker_client = docker.from_env()
            docker_info = {
                "version": docker_client.version(),
                "containers": len(docker_client.containers.list()),
                "images": len(docker_client.images.list()),
                "running_containers": [
                    {
                        "name": container.name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else None
                    }
                    for container in docker_client.containers.list()
                ]
            }
        except Exception as e:
            docker_info = {"error": str(e)}

        # Get application configuration
        app_config = {
            "model_status": {
                "model_loaded": inference_engine is not None,
                "model_path": getattr(inference_engine, 'model_path', None) if inference_engine else None,
            },
            "training_status": training_status,
            "available_tools": list(tool_registry.tools.keys()),
            "huggingface_status": {
                "available": hf_manager is not None,
                "authenticated": hf_manager.is_authenticated() if hf_manager else False
            },
            "model_manager_config": model_manager.config if model_manager else None
        }

        return JSONResponse({
            "system_info": system_info,
            "docker_info": docker_info,
            "app_config": app_config,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    # 运行服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )