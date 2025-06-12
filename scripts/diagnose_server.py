#!/usr/bin/env python3
"""
服务器诊断脚本
帮助排查 HTTP 400 错误和其他常见问题
"""

import asyncio
import logging
import sys
import requests
import json
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_server_endpoints():
    """测试服务器端点"""
    base_url = "http://localhost:8000"
    
    print("🔍 开始诊断服务器...")
    print("=" * 50)
    
    # 测试基本连接
    print("1. 测试基本连接...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ 健康检查: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器")
        print("   💡 请确保服务器正在运行: python start.py start")
        return False
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return False
    
    # 测试主页
    print("\n2. 测试主页...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   ✅ 主页: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 主页访问失败: {e}")
    
    # 测试 API 文档
    print("\n3. 测试 API 文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   ✅ API 文档: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API 文档访问失败: {e}")
    
    # 测试前端界面
    print("\n4. 测试前端界面...")
    try:
        response = requests.get(f"{base_url}/feedback_ui.html", timeout=5)
        print(f"   ✅ HTML 界面: {response.status_code}")
    except Exception as e:
        print(f"   ❌ HTML 界面访问失败: {e}")
    
    try:
        response = requests.get(f"{base_url}/react", timeout=5)
        print(f"   ✅ React 界面: {response.status_code}")
    except Exception as e:
        print(f"   ❌ React 界面访问失败: {e}")
        print("   💡 请先构建 React 应用: python start.py build")
    
    # 测试会话 API
    print("\n5. 测试会话 API...")
    test_session_id = "test-session-123"
    try:
        response = requests.get(f"{base_url}/api/session/{test_session_id}", timeout=5)
        if response.status_code == 404:
            print(f"   ✅ 会话 API 正常 (404 是预期的，因为会话不存在)")
        else:
            print(f"   ✅ 会话 API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 会话 API 测试失败: {e}")
    
    # 测试反馈提交 API
    print("\n6. 测试反馈提交 API...")
    try:
        feedback_data = {
            "text": "测试反馈",
            "images": [],
            "files": []
        }
        response = requests.post(
            f"{base_url}/api/session/{test_session_id}/feedback",
            json=feedback_data,
            timeout=5
        )
        print(f"   ✅ 反馈提交 API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 反馈提交 API 测试失败: {e}")
    
    return True

def check_file_paths():
    """检查文件路径"""
    print("\n📁 检查文件路径...")
    print("=" * 30)
    
    # 检查后端文件
    backend_dir = Path(__file__).parent.parent / "backend"
    required_backend_files = ["fastapi_server.py", "mcp_server_fastmcp.py", "requirements.txt"]
    
    for file in required_backend_files:
        file_path = backend_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} 缺失")
    
    # 检查前端文件
    frontend_dir = Path(__file__).parent.parent / "frontend"
    html_file = frontend_dir / "feedback_ui.html"
    react_build = frontend_dir / "build" / "index.html"
    
    if html_file.exists():
        print(f"   ✅ HTML 界面文件")
    else:
        print(f"   ❌ HTML 界面文件缺失")
    
    if react_build.exists():
        print(f"   ✅ React 构建文件")
    else:
        print(f"   ⚠️ React 构建文件不存在 (运行 python start.py build 构建)")

def analyze_common_400_errors():
    """分析常见的 400 错误原因"""
    print("\n🔍 常见 400 错误原因分析...")
    print("=" * 40)
    
    print("400 Bad Request 通常由以下原因引起:")
    print("1. 📝 请求体格式错误")
    print("   - JSON 格式不正确")
    print("   - 缺少必需的字段")
    print("   - 数据类型不匹配")
    
    print("\n2. 🔗 URL 参数错误")
    print("   - 会话ID格式不正确")
    print("   - 特殊字符未编码")
    
    print("\n3. 📋 Content-Type 错误")
    print("   - 缺少 Content-Type 头")
    print("   - Content-Type 不匹配")
    
    print("\n4. 📏 请求大小超限")
    print("   - 上传文件过大")
    print("   - 请求体过大")
    
    print("\n💡 解决建议:")
    print("1. 检查请求的 JSON 格式")
    print("2. 确保会话ID格式正确")
    print("3. 检查 Content-Type 头")
    print("4. 查看服务器日志获取详细错误信息")

def show_correct_usage():
    """显示正确的使用方法"""
    print("\n📖 正确的使用方法...")
    print("=" * 30)
    
    print("1. 启动服务器:")
    print("   python start.py start")
    
    print("\n2. 访问界面:")
    print("   http://localhost:8000/")
    print("   http://localhost:8000/feedback_ui.html?session=your-session-id")
    print("   http://localhost:8000/react?session=your-session-id")
    
    print("\n3. API 调用示例:")
    print("   GET  /health")
    print("   GET  /api/session/{session_id}")
    print("   POST /api/session/{session_id}/feedback")
    
    print("\n4. WebSocket 连接:")
    print("   ws://localhost:8001/ws/{session_id}")

def main():
    """主函数"""
    print("🚀 FastMCP 反馈收集器诊断工具")
    print("=" * 50)
    
    # 检查文件路径
    check_file_paths()
    
    # 测试服务器端点
    server_ok = test_server_endpoints()
    
    # 分析常见错误
    analyze_common_400_errors()
    
    # 显示正确用法
    show_correct_usage()
    
    print("\n" + "=" * 50)
    if server_ok:
        print("✅ 诊断完成！服务器运行正常。")
    else:
        print("❌ 发现问题！请检查服务器状态。")
    
    print("\n如果问题仍然存在，请:")
    print("1. 检查服务器日志")
    print("2. 确保所有依赖已安装")
    print("3. 重启服务器")

if __name__ == "__main__":
    main()
