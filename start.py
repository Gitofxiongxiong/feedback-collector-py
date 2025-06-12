#!/usr/bin/env python3
"""
MCP 反馈收集器主启动脚本
统一管理前端和后端服务的启动
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# 添加脚本目录到 Python 路径
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

def main():
    parser = argparse.ArgumentParser(description="MCP 反馈收集器启动脚本")
    parser.add_argument(
        "command",
        choices=["start", "build", "demo", "test"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--mcp-only",
        action="store_true",
        help="仅启动 MCP 服务器"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
        # 启动服务器
        script_path = script_dir / "start_servers_fastmcp.py"
        cmd = [sys.executable, str(script_path)]
        if args.mcp_only:
            cmd.append("--mcp-only")
        subprocess.run(cmd)
        
    elif args.command == "build":
        # 构建 React 前端
        script_path = script_dir / "build_react.py"
        # 切换到前端目录
        os.chdir("frontend")
        subprocess.run([sys.executable, str(script_path.resolve())])
        
    elif args.command == "demo":
        # 运行演示
        script_path = script_dir / "demo_fastmcp.py"
        subprocess.run([sys.executable, str(script_path)])
        
    elif args.command == "test":
        # 运行测试
        test_dir = Path(__file__).parent / "tests"
        test_script = test_dir / "test_fastmcp_client.py"
        subprocess.run([sys.executable, str(test_script)])

if __name__ == "__main__":
    main()
