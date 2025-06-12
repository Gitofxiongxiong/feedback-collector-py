#!/usr/bin/env python3
"""
FastMCP集成启动脚本
同时启动HTTP服务器（用于Web界面）和FastMCP服务器
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServerManager:
    """服务器管理器"""
    
    def __init__(self):
        self.http_process = None
        self.mcp_process = None
        self.running = False
    
    async def start_fastapi_server(self):
        """启动FastAPI服务器"""
        try:
            logger.info("启动FastAPI服务器...")
            backend_dir = Path(__file__).parent.parent / "backend"
            fastapi_script = backend_dir / "fastapi_server.py"
            self.http_process = subprocess.Popen(
                [sys.executable, str(fastapi_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(backend_dir)
            )

            # 等待一下让服务器启动
            await asyncio.sleep(3)

            if self.http_process.poll() is None:
                logger.info("FastAPI服务器启动成功")
                return True
            else:
                stdout, stderr = self.http_process.communicate()
                logger.error(f"FastAPI服务器启动失败: {stderr}")
                return False

        except Exception as e:
            logger.error(f"启动FastAPI服务器时出错: {e}")
            return False
    
    async def start_mcp_server(self):
        """启动FastMCP服务器"""
        try:
            logger.info("启动FastMCP服务器...")

            # 添加后端目录到 Python 路径
            backend_dir = Path(__file__).parent.parent / "backend"
            sys.path.insert(0, str(backend_dir))

            # 导入并启动WebSocket服务器
            from mcp_server_fastmcp import start_websocket_server, server_state, cleanup_expired_sessions
            await start_websocket_server()
            
            logger.info(f"WebSocket服务器已启动: ws://{server_state.host}:{server_state.websocket_port}")
            
            # 启动清理任务
            async def cleanup_task():
                while self.running:
                    await asyncio.sleep(3600)  # 每小时清理一次
                    if self.running:
                        cleaned = cleanup_expired_sessions()
                        if cleaned > 0:
                            logger.info(f"清理了 {cleaned} 个过期会话")
            
            # 在后台运行清理任务
            asyncio.create_task(cleanup_task())
            
            return True
            
        except Exception as e:
            logger.error(f"启动FastMCP服务器时出错: {e}")
            return False
    
    async def start_all_servers(self):
        """启动所有服务器"""
        self.running = True

        # 启动FastAPI服务器
        fastapi_ok = await self.start_fastapi_server()
        if not fastapi_ok:
            logger.error("FastAPI服务器启动失败，退出")
            return False
        
        # 启动MCP服务器
        mcp_ok = await self.start_mcp_server()
        if not mcp_ok:
            logger.error("FastMCP服务器启动失败，退出")
            await self.stop_all_servers()
            return False
        
        logger.info("所有服务器启动成功!")
        logger.info("=" * 50)
        logger.info("服务器信息:")
        logger.info("  FastAPI服务器: http://localhost:8000")
        logger.info("  API文档: http://localhost:8000/docs")
        logger.info("  WebSocket服务器: ws://localhost:8001")
        logger.info("  反馈界面: http://localhost:8000/feedback_ui.html")
        logger.info("  FastMCP服务器: stdio (通过 mcp_server_fastmcp.py)")
        logger.info("=" * 50)
        
        return True
    
    async def stop_all_servers(self):
        """停止所有服务器"""
        self.running = False
        
        logger.info("正在停止服务器...")
        
        # 停止FastAPI服务器
        if self.http_process and self.http_process.poll() is None:
            self.http_process.terminate()
            try:
                self.http_process.wait(timeout=5)
                logger.info("FastAPI服务器已停止")
            except subprocess.TimeoutExpired:
                self.http_process.kill()
                logger.info("FastAPI服务器已强制停止")
        
        # 停止WebSocket服务器
        try:
            # 确保后端模块在路径中
            backend_dir = Path(__file__).parent.parent / "backend"
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))
            from mcp_server_fastmcp import stop_websocket_server
            await stop_websocket_server()
            logger.info("WebSocket服务器已停止")
        except Exception as e:
            logger.error(f"停止WebSocket服务器时出错: {e}")
        
        logger.info("所有服务器已停止")
    
    async def run_forever(self):
        """持续运行服务器"""
        try:
            # 启动所有服务器
            if not await self.start_all_servers():
                return
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
                # 检查FastAPI服务器是否还在运行
                if self.http_process and self.http_process.poll() is not None:
                    logger.error("FastAPI服务器意外停止")
                    break
                    
        except KeyboardInterrupt:
            logger.info("收到中断信号...")
        except Exception as e:
            logger.error(f"服务器运行时出错: {e}")
        finally:
            await self.stop_all_servers()

async def main():
    """主函数"""
    # 检查必要文件是否存在
    backend_dir = Path(__file__).parent.parent / "backend"
    required_files = ["fastapi_server.py", "mcp_server_fastmcp.py"]
    missing_files = [f for f in required_files if not (backend_dir / f).exists()]

    if missing_files:
        logger.error(f"缺少必要文件: {missing_files}")
        return

    # 检查前端文件
    frontend_dir = Path(__file__).parent.parent / "frontend"
    html_ui = frontend_dir / "feedback_ui.html"
    react_build = frontend_dir / "build" / "index.html"

    if not html_ui.exists() and not react_build.exists():
        logger.warning("没有找到前端界面文件")
        logger.info("HTML 版本: feedback_ui.html")
        logger.info("React 版本: build/index.html (运行 python build_react.py 构建)")
    else:
        if html_ui.exists():
            logger.info("✅ HTML 版本可用")
        if react_build.exists():
            logger.info("✅ React 版本可用")
    
    # 创建服务器管理器并运行
    manager = ServerManager()
    await manager.run_forever()

def run_mcp_only():
    """仅运行FastMCP服务器（用于MCP客户端连接）"""
    # 添加后端目录到 Python 路径
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.insert(0, str(backend_dir))
    from mcp_server_fastmcp import mcp
    
    logger.info("启动FastMCP服务器（仅MCP模式）...")
    logger.info("使用 stdio 传输协议")
    logger.info("可以通过MCP客户端连接此服务器")
    
    # 运行FastMCP服务器
    mcp.run()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-only":
        # 仅运行MCP服务器
        run_mcp_only()
    else:
        # 运行完整的服务器套件
        asyncio.run(main())
