#!/usr/bin/env python3
"""
合并的MCP+FastAPI服务器启动脚本
启动集成的服务器，支持MCP协议和Web界面
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
    """合并服务器管理器"""

    def __init__(self):
        self.server_process = None
        self.running = False
    
    async def build_frontend_if_needed(self):
        """如果需要，构建前端"""
        try:
            frontend_dir = Path(__file__).parent.parent / "frontend"
            build_dir = frontend_dir / "build"

            if not build_dir.exists():
                logger.info("前端未构建，开始构建...")
                # 运行构建脚本
                build_script = Path(__file__).parent / "build_and_test.py"
                result = subprocess.run(
                    [sys.executable, str(build_script)],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    logger.info("✅ 前端构建成功")
                    return True
                else:
                    logger.error(f"❌ 前端构建失败: {result.stderr}")
                    return False
            else:
                logger.info("✅ 前端已构建")
                return True

        except Exception as e:
            logger.error(f"构建前端时出错: {e}")
            return False
    
    async def start_combined_server(self):
        """启动合并的服务器"""
        try:
            logger.info("启动合并的MCP+FastAPI服务器...")
            backend_dir = Path(__file__).parent.parent / "backend"
            server_script = backend_dir / "mcp_server_fastmcp.py"

            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script), "--web-only"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(backend_dir)
            )

            # 等待一下让服务器启动
            await asyncio.sleep(5)

            if self.server_process.poll() is None:
                logger.info("✅ 合并服务器启动成功")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ 合并服务器启动失败: {stderr}")
                return False

        except Exception as e:
            logger.error(f"启动合并服务器时出错: {e}")
            return False
    
    async def start_all_servers(self):
        """启动所有服务器"""
        self.running = True

        # 构建前端（如果需要）
        if not await self.build_frontend_if_needed():
            logger.error("前端构建失败，退出")
            return False

        # 启动合并服务器
        server_ok = await self.start_combined_server()
        if not server_ok:
            logger.error("合并服务器启动失败，退出")
            return False

        logger.info("✅ 服务器启动成功!")
        logger.info("=" * 50)
        logger.info("服务器信息:")
        logger.info("  FastAPI服务器: http://localhost:8000")
        logger.info("  API文档: http://localhost:8000/docs")
        logger.info("  WebSocket端点: ws://localhost:8000/ws/{session_id}")
        logger.info("  反馈界面: http://localhost:8000/feedback_ui.html")
        logger.info("  React应用: http://localhost:8000/react")
        logger.info("  FastMCP服务器: 集成在同一进程中")
        logger.info("=" * 50)

        return True
    
    async def stop_all_servers(self):
        """停止所有服务器"""
        self.running = False

        logger.info("正在停止服务器...")

        # 停止合并服务器
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                logger.info("✅ 合并服务器已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.info("✅ 合并服务器已强制停止")

        logger.info("✅ 所有服务器已停止")
    
    async def run_forever(self):
        """持续运行服务器"""
        try:
            # 启动所有服务器
            if not await self.start_all_servers():
                return
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)

                # 检查合并服务器是否还在运行
                if self.server_process and self.server_process.poll() is not None:
                    logger.error("❌ 合并服务器意外停止")
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
