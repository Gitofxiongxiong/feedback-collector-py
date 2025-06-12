#!/usr/bin/env python3
"""
FastMCP反馈收集器演示脚本
展示如何使用新的FastMCP反馈收集服务器
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

async def demo_feedback_collection():
    """演示反馈收集功能"""
    
    print("🚀 FastMCP 反馈收集器演示")
    print("=" * 50)
    
    # 添加后端目录到 Python 路径并导入服务器对象
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.insert(0, str(backend_dir))
    from mcp_server_fastmcp import mcp
    
    async with Client(mcp) as client:
        print("✅ 已连接到 FastMCP 服务器")
        
        # 1. 列出可用工具
        print("\n📋 可用工具:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # 2. 演示不需要响应的反馈收集
        print("\n🔄 演示1: 不需要用户响应的反馈收集")
        result = await client.call_tool(
            "collect_feedback_mcp_feedback_collector",
            {
                "work_summary": "我已经完成了数据库优化任务，查询性能提升了40%。相关的索引已经创建，慢查询日志显示显著改善。",
                "require_response": False
            }
        )
        
        if isinstance(result, list) and len(result) > 0:
            print(f"📝 结果: {result[0].text}")
        
        # 3. 演示需要响应但会超时的场景
        print("\n⏱️ 演示2: 需要用户响应但会超时的场景")
        result = await client.call_tool(
            "collect_feedback_mcp_feedback_collector",
            {
                "work_summary": "我已经完成了新功能的开发和测试，代码已经通过了所有单元测试和集成测试。请确认是否可以部署到生产环境。",
                "timeout": 5,  # 5秒超时
                "require_response": True
            }
        )
        
        if isinstance(result, list) and len(result) > 0:
            print(f"📝 结果: {result[0].text}")
        
        # 4. 演示自定义会话ID
        print("\n🆔 演示3: 使用自定义会话ID")
        custom_session_id = "demo-session-2025"
        result = await client.call_tool(
            "collect_feedback_mcp_feedback_collector",
            {
                "work_summary": "我已经完成了系统监控仪表板的开发，包含了CPU、内存、磁盘和网络的实时监控图表。",
                "session_id": custom_session_id,
                "require_response": False
            }
        )
        
        if isinstance(result, list) and len(result) > 0:
            print(f"📝 结果: {result[0].text}")
        
        print("\n✨ 演示完成!")
        print("\n💡 提示:")
        print("  - 在实际使用中，用户可以通过Web界面提供反馈")
        print("  - WebSocket连接支持实时通信")
        print("  - 会话会自动清理过期数据")

async def demo_fastapi_interface():
    """演示FastAPI界面功能"""

    print("\n🌐 FastAPI Web界面演示")
    print("=" * 35)

    # 检查服务器是否运行
    try:
        import requests
        response = requests.get("http://localhost:8000", timeout=2)
        print("✅ FastAPI服务器正在运行")
        print("📱 反馈界面: http://localhost:8000/feedback_ui.html")
        print("📚 API文档: http://localhost:8000/docs")
        print("📖 ReDoc文档: http://localhost:8000/redoc")
        print("🔌 WebSocket服务器: ws://localhost:8001")

        # 测试健康检查端点
        health_response = requests.get("http://localhost:8000/health", timeout=2)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"💚 健康检查: {health_data}")

        # 创建一个会话用于演示
        # 确保后端模块在路径中
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from mcp_server_fastmcp import mcp
        async with Client(mcp) as client:
            result = await client.call_tool(
                "collect_feedback_mcp_feedback_collector",
                {
                    "work_summary": "演示会话：我已经完成了用户认证系统的重构，新增了双因子认证和密码强度检查功能。现在系统支持FastAPI后端，提供了现代化的API接口。",
                    "require_response": False
                }
            )

            if isinstance(result, list) and len(result) > 0:
                # 从结果中提取会话ID
                result_text = result[0].text
                if "会话ID:" in result_text:
                    session_id = result_text.split("会话ID:")[-1].strip()
                    demo_url = f"http://localhost:8000/feedback_ui.html?session={session_id}"
                    print(f"🔗 演示链接: {demo_url}")
                    print("   (复制此链接到浏览器中查看反馈界面)")

                    # 测试会话API
                    try:
                        session_response = requests.get(f"http://localhost:8000/api/session/{session_id}", timeout=2)
                        if session_response.status_code == 200:
                            session_data = session_response.json()
                            print(f"📊 会话信息API: {session_data}")
                    except Exception as api_e:
                        print(f"⚠️ 会话API测试失败: {api_e}")

    except Exception as e:
        print("❌ FastAPI服务器未运行")
        print("💡 请先运行: python start_servers_fastmcp.py")

async def main():
    """主演示函数"""
    try:
        # 基本功能演示
        await demo_feedback_collection()
        
        # FastAPI Web界面演示
        await demo_fastapi_interface()
        
        print("\n🎉 所有演示完成!")
        print("\n📚 更多信息请查看 README_FastMCP.md")
        
    except Exception as e:
        logger.error(f"演示过程中出错: {e}")
        print(f"\n❌ 演示失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
