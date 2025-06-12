#!/usr/bin/env python3
"""
FastMCP客户端测试脚本
用于测试新的FastMCP反馈收集服务器
"""

import asyncio
import logging
import sys
from pathlib import Path
from fastmcp import Client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_fastmcp_server():
    """测试FastMCP服务器"""
    
    # 方法1: 直接连接到服务器对象（内存中测试）
    print("=== 测试方法1: 内存中测试 ===")
    try:
        # 添加后端目录到 Python 路径
        backend_dir = Path(__file__).parent.parent / "backend"
        sys.path.insert(0, str(backend_dir))
        from mcp_server_fastmcp import mcp
        
        async with Client(mcp) as client:
            # 列出可用工具
            tools = await client.list_tools()
            print(f"可用工具: {[tool.name for tool in tools]}")
            
            # 调用反馈收集工具
            result = await client.call_tool(
                "collect_feedback_mcp_feedback_collector",
                {
                    "work_summary": "我已经完成了数据分析任务，生成了用户行为报告。请确认结果是否符合预期。",
                    "timeout": 10,  # 短超时用于测试
                    "require_response": False  # 不等待响应
                }
            )
            # 处理结果 - result 可能是列表
            if isinstance(result, list) and len(result) > 0:
                print(f"工具调用结果: {result[0].text}")
            else:
                print(f"工具调用结果: {result}")
            
    except Exception as e:
        logger.error(f"内存测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 方法2: 通过stdio连接到Python脚本
    print("=== 测试方法2: Stdio连接 ===")
    try:
        backend_script = backend_dir / "mcp_server_fastmcp.py"
        async with Client(str(backend_script)) as client:
            # 列出可用工具
            tools = await client.list_tools()
            print(f"可用工具: {[tool.name for tool in tools]}")
            
            # 调用反馈收集工具
            result = await client.call_tool(
                "collect_feedback_mcp_feedback_collector",
                {
                    "work_summary": "我已经完成了代码重构任务，优化了性能并修复了bug。请检查代码质量。",
                    "timeout": 5,  # 短超时用于测试
                    "require_response": False  # 不等待响应
                }
            )
            # 处理结果 - result 可能是列表
            if isinstance(result, list) and len(result) > 0:
                print(f"工具调用结果: {result[0].text}")
            else:
                print(f"工具调用结果: {result}")
            
    except Exception as e:
        logger.error(f"Stdio测试失败: {e}")

async def test_with_response():
    """测试需要用户响应的场景"""
    print("=== 测试用户响应场景 ===")

    try:
        # 添加后端目录到 Python 路径
        backend_dir = Path(__file__).parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from mcp_server_fastmcp import mcp
        
        async with Client(mcp) as client:
            print("发送需要用户响应的请求...")
            
            # 这个调用会等待用户响应（但会超时）
            result = await client.call_tool(
                "collect_feedback_mcp_feedback_collector",
                {
                    "work_summary": "我已经完成了系统部署，所有服务都在正常运行。请确认是否可以开始生产环境测试。",
                    "timeout": 3,  # 很短的超时用于演示
                    "require_response": True  # 等待响应
                }
            )
            # 处理结果 - result 可能是列表
            if isinstance(result, list) and len(result) > 0:
                print(f"响应结果: {result[0].text}")
            else:
                print(f"响应结果: {result}")
            
    except Exception as e:
        logger.error(f"响应测试失败: {e}")

async def main():
    """主测试函数"""
    print("开始测试FastMCP反馈收集服务器...\n")
    
    # 基本功能测试
    await test_fastmcp_server()
    
    print("\n" + "="*50 + "\n")
    
    # 用户响应测试
    await test_with_response()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
