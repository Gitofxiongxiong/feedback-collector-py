#!/usr/bin/env python3
"""
前端构建和连接测试脚本
1. 编译React前端
2. 测试FastAPI和Web前端的连接
"""

import asyncio
import logging
import subprocess
import sys
import time
import requests
import websockets
import json
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildAndTestManager:
    """构建和测试管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend"
        self.backend_dir = self.project_root / "backend"
        
    def check_node_installed(self):
        """检查Node.js是否安装"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js版本: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ Node.js检查失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Node.js检查出错: {e}")
            return False
    
    def check_npm_installed(self):
        """检查npm是否安装"""
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                logger.info(f"✅ npm版本: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ npm检查失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ npm检查出错: {e}")
            return False
    
    def install_frontend_dependencies(self):
        """安装前端依赖"""
        logger.info("📦 安装前端依赖...")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                logger.info("✅ 前端依赖安装成功")
                return True
            else:
                logger.error(f"❌ 前端依赖安装失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ 安装前端依赖时出错: {e}")
            return False
    
    def build_frontend(self):
        """构建前端"""
        logger.info("🔨 构建React前端...")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info("✅ 前端构建成功")
                
                # 检查构建输出
                build_dir = self.frontend_dir / "build"
                if build_dir.exists():
                    index_file = build_dir / "index.html"
                    if index_file.exists():
                        logger.info(f"✅ 构建文件已生成: {index_file}")
                        return True
                    else:
                        logger.error("❌ 构建文件index.html未找到")
                        return False
                else:
                    logger.error("❌ 构建目录未找到")
                    return False
            else:
                logger.error(f"❌ 前端构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 构建前端时出错: {e}")
            return False
    
    async def start_server_for_test(self):
        """启动服务器用于测试"""
        logger.info("🚀 启动服务器进行测试...")
        try:
            # 启动合并的服务器（仅Web模式）
            self.server_process = subprocess.Popen(
                [sys.executable, "mcp_server_fastmcp.py", "--web-only"],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            await asyncio.sleep(5)
            
            if self.server_process.poll() is None:
                logger.info("✅ 服务器启动成功")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ 服务器启动失败: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 启动服务器时出错: {e}")
            return False
    
    def stop_server(self):
        """停止测试服务器"""
        if hasattr(self, 'server_process') and self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                logger.info("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.info("✅ 服务器已强制停止")
    
    async def test_http_connection(self):
        """测试HTTP连接"""
        logger.info("🔗 测试HTTP连接...")
        try:
            # 测试根路径
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                logger.info("✅ HTTP根路径连接成功")
            else:
                logger.error(f"❌ HTTP根路径连接失败: {response.status_code}")
                return False
            
            # 测试健康检查
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ 健康检查接口正常")
            else:
                logger.error(f"❌ 健康检查接口异常: {response.status_code}")
                return False
            
            # 测试React应用
            response = requests.get("http://localhost:8000/react", timeout=10)
            if response.status_code == 200:
                logger.info("✅ React应用访问成功")
            else:
                logger.warning(f"⚠️  React应用访问失败: {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ HTTP连接测试失败: {e}")
            return False
    
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        logger.info("🔗 测试WebSocket连接...")
        try:
            # 创建测试会话ID
            test_session_id = "test_session_123"
            
            # 连接WebSocket
            uri = f"ws://localhost:8000/ws/{test_session_id}"
            async with websockets.connect(uri) as websocket:
                logger.info("✅ WebSocket连接建立成功")
                
                # 发送测试消息
                test_message = {
                    "type": "test_message",
                    "content": "测试消息"
                }
                await websocket.send(json.dumps(test_message))
                logger.info("✅ WebSocket消息发送成功")
                
                # 等待响应（可选）
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    logger.info(f"✅ 收到WebSocket响应: {response}")
                except asyncio.TimeoutError:
                    logger.info("ℹ️  WebSocket响应超时（正常，因为没有对应的会话）")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket连接测试失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("🚀 开始前端构建和连接测试")
        logger.info("=" * 60)
        
        # 1. 检查环境
        if not self.check_node_installed() or not self.check_npm_installed():
            logger.error("❌ 环境检查失败，请安装Node.js和npm")
            return False
        
        # 2. 安装依赖
        if not self.install_frontend_dependencies():
            logger.error("❌ 前端依赖安装失败")
            return False
        
        # 3. 构建前端
        if not self.build_frontend():
            logger.error("❌ 前端构建失败")
            return False
        
        # 4. 启动服务器
        if not await self.start_server_for_test():
            logger.error("❌ 服务器启动失败")
            return False
        
        try:
            # 5. 测试HTTP连接
            if not await self.test_http_connection():
                logger.error("❌ HTTP连接测试失败")
                return False
            
            # 6. 测试WebSocket连接
            if not await self.test_websocket_connection():
                logger.error("❌ WebSocket连接测试失败")
                return False
            
            logger.info("=" * 60)
            logger.info("🎉 所有测试通过！")
            logger.info("=" * 60)
            return True
            
        finally:
            # 清理：停止服务器
            self.stop_server()

async def main():
    """主函数"""
    manager = BuildAndTestManager()
    success = await manager.run_all_tests()
    
    if success:
        logger.info("✅ 构建和测试完成")
        sys.exit(0)
    else:
        logger.error("❌ 构建和测试失败")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
