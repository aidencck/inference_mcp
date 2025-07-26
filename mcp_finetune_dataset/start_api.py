#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP微调项目 API服务启动脚本
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="启动MCP API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    parser.add_argument("--log-level", default="info", help="日志级别")
    
    args = parser.parse_args()
    
    # 确保在正确的目录中运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"启动MCP API服务...")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"文档地址: http://{args.host}:{args.port}/docs")
    print(f"工作目录: {script_dir}")
    
    # 启动服务
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()