#!/usr/bin/env python3
"""
合并的MCP+FastAPI反馈收集服务器
使用FastMCP框架提供collect_feedback工具，集成FastAPI提供Web服务和WebSocket支持
"""

import asyncio
import json
import logging
import uuid
import subprocess
import sys
import threading
import queue
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FeedbackSession:
    """反馈会话数据结构"""
    session_id: str
    question: str
    created_at: datetime
    status: str = "waiting"  # waiting, completed, expired
    response: Optional[str] = None
    images: List[Dict] = None
    files: List[Dict] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.files is None:
            self.files = []

class FeedbackRequest(BaseModel):
    """反馈请求模型"""
    work_summary: str  # 改名以匹配工具描述
    timeout: int = 300  # 默认5分钟超时
    session_id: Optional[str] = None
    require_response: bool = True

class FeedbackResponse(BaseModel):
    """反馈响应模型"""
    session_id: str
    text: str
    images: List[Dict] = []
    files: List[Dict] = []
    timestamp: str

# 创建FastMCP服务器实例
mcp = FastMCP("feedback-collector")

# 创建FastAPI应用
app = FastAPI(
    title="MCP 反馈收集器",
    description="基于 FastMCP 和 FastAPI 的现代化反馈收集系统",
    version="2.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 消息队列用于MCP和FastAPI之间的通信
message_queue = queue.Queue()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

# 全局状态管理
class ServerState:
    def __init__(self):
        self.sessions: Dict[str, FeedbackSession] = {}
        self.host = "localhost"
        self.web_port = 8000

# 全局服务器状态
server_state = ServerState()

@mcp.tool
async def collect_feedback_mcp_feedback_collector(
    work_summary: str,
    timeout: int = 3600,  # 默认60分钟
    session_id: Optional[str] = None,
    require_response: bool = True
) -> str:
    """
    收集用户反馈的工具。当需要向用户提问或确认时使用此工具。
    
    Args:
        work_summary: AI工作汇报内容，描述AI完成的工作和结果
        timeout: 等待用户响应的超时时间（秒），默认300秒
        session_id: 可选的会话ID，如果不提供将自动生成
        require_response: 是否要求用户必须响应，默认true
        ctx: FastMCP上下文对象
    
    Returns:
        用户反馈结果或超时信息
    """
    try:
        # 生成会话ID
        session_id = session_id or str(uuid.uuid4())
        
        # 创建会话
        session = FeedbackSession(
            session_id=session_id,
            question=work_summary,
            created_at=datetime.now()
        )
        
        server_state.sessions[session_id] = session
        logger.info(f"创建反馈会话: {session_id}")
        
        # 生成反馈页面URL（现在直接使用React应用）
        feedback_url = f"http://{server_state.host}:{server_state.web_port}/?session={session_id}"

        # 通过消息队列发送消息到FastAPI
        message_queue.put({
            "type": "agent_message",
            "session_id": session_id,
            "content": work_summary
        })
        
        # 等待用户响应
        if require_response:
            response = await _wait_for_response(session_id, timeout)
            
            if response:
                return f"用户反馈已收到:\n\n**文本内容:**\n{response.text}\n\n**图片数量:** {len(response.images)}\n**文件数量:** {len(response.files)}\n\n**会话ID:** {session_id}"
            else:
                return f"等待用户响应超时。请访问以下链接提供反馈:\n{feedback_url}\n\n**会话ID:** {session_id}"
        else:
            return f"反馈收集已启动。用户可以通过以下链接提供反馈:\n{feedback_url}\n\n**会话ID:** {session_id}"
            
    except Exception as e:
        logger.error(f"处理反馈收集请求时出错: {e}")
        return f"反馈收集失败: {str(e)}"

async def _wait_for_response(session_id: str, timeout: int) -> Optional[FeedbackResponse]:
    """等待用户响应"""
    try:
        # 等待指定时间
        for _ in range(timeout):
            await asyncio.sleep(1)
            session = server_state.sessions.get(session_id)
            if session and session.status == "completed":
                return FeedbackResponse(
                    session_id=session_id,
                    text=session.response or "",
                    images=session.images,
                    files=session.files,
                    timestamp=datetime.now().isoformat()
                )
        
        # 超时
        if session_id in server_state.sessions:
            server_state.sessions[session_id].status = "expired"
        
        return None
        
    except Exception as e:
        logger.error(f"等待响应时出错: {e}")
        return None

# FastAPI路由定义
@app.get("/", response_class=FileResponse)
async def root():
    """根路径，返回 React 应用"""
    react_file = build_dir / "index.html"
    if react_file.exists():
        return FileResponse(react_file)
    else:
        # 如果React应用不存在，返回简单的欢迎页面
        return HTMLResponse("""
        <html>
            <head>
                <title>MCP 反馈收集器</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .error { color: #dc3545; background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .link { color: #007bff; text-decoration: none; }
                    .link:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 MCP 反馈收集器</h1>
                    <div class="error">
                        <h3>⚠️ React 应用未找到</h3>
                        <p>请先构建前端应用：</p>
                        <code>cd frontend && npm run build</code>
                    </div>
                    <p>
                        <a href="/docs" class="link">API 文档</a> |
                        <a href="/health" class="link">健康检查</a>
                    </p>
                </div>
            </body>
        </html>
        """)


# 静态文件服务（用于 React 应用）
frontend_dir = Path(__file__).parent.parent / "frontend"
build_dir = frontend_dir / "build"
static_dir = build_dir / "static"

# 挂载静态资源到 /static 路径
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 挂载其他前端资源（如 favicon.ico, manifest.json 等）
if build_dir.exists():
    # 为前端的公共文件创建路由
    @app.get("/favicon.ico", response_class=FileResponse)
    async def get_favicon():
        favicon_path = build_dir / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404, detail="Favicon not found")

    # 可选的前端资源文件
    optional_files = [
        ("manifest.json", "manifest.json"),
        ("logo192.png", "logo192.png"),
        ("logo512.png", "logo512.png"),
        ("robots.txt", "robots.txt")
    ]

    for route_path, file_name in optional_files:
        file_path = build_dir / file_name
        if file_path.exists():
            # 动态创建路由
            def create_file_handler(path):
                async def handler():
                    return FileResponse(path)
                return handler

            app.get(f"/{route_path}", response_class=FileResponse)(
                create_file_handler(file_path)
            )

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 端点"""
    await manager.connect(websocket, session_id)

    try:
        # 如果会话存在，发送初始消息
        session_info = get_session_info(session_id)

        if session_info:
            await manager.send_message(session_id, {
                "type": "agent_message",
                "content": session_info["question"]
            })

        # 保持连接并处理消息
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "user_feedback":
                # 更新会话状态
                if session_id in server_state.sessions:
                    session = server_state.sessions[session_id]
                    feedback_data = data.get("data", {})
                    session.response = feedback_data.get("text", "")
                    session.images = feedback_data.get("images", [])
                    session.files = feedback_data.get("files", [])
                    session.status = "completed"

                    logger.info(f"收到用户反馈: {session_id}")

                    # 发送确认消息
                    await manager.send_message(session_id, {
                        "type": "feedback_received",
                        "message": "反馈已收到，谢谢！"
                    })

                    # 通知会话完成
                    await manager.send_message(session_id, {
                        "type": "session_complete"
                    })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(session_id)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "mcp-feedback-collector"}

# SPA路由支持 - 这个路由必须放在最后，作为fallback
@app.get("/{full_path:path}", response_class=FileResponse)
async def spa_fallback(full_path: str):
    """
    SPA fallback路由 - 对于所有未匹配的路径，返回React应用的index.html
    这样React Router就能处理前端路由了
    """
    # 排除API路径和静态资源路径
    if (full_path.startswith("api/") or
        full_path.startswith("docs") or
        full_path.startswith("redoc") or
        full_path.startswith("openapi.json") or
        full_path.startswith("ws/") or
        full_path.startswith("static/") or
        full_path.endswith(".ico") or
        full_path.endswith(".json") or
        full_path.endswith(".png") or
        full_path.endswith(".jpg") or
        full_path.endswith(".svg")):
        raise HTTPException(status_code=404, detail="Not found")

    # 返回React应用的index.html
    react_file = build_dir / "index.html"
    if react_file.exists():
        return FileResponse(react_file)
    else:
        raise HTTPException(status_code=404, detail="React 应用未找到，请先运行构建")

async def process_message_queue():
    """处理消息队列，将MCP消息转发到WebSocket客户端"""
    while True:
        try:
            # 非阻塞地检查队列
            try:
                message = message_queue.get_nowait()
                session_id = message.get("session_id")

                if session_id and session_id in manager.active_connections:
                    await manager.send_message(session_id, {
                        "type": message.get("type"),
                        "content": message.get("content")
                    })

            except queue.Empty:
                pass

            await asyncio.sleep(0.1)  # 避免CPU占用过高

        except Exception as e:
            logger.error(f"处理消息队列时出错: {e}")
            await asyncio.sleep(1)

def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """获取会话信息"""
    session = server_state.sessions.get(session_id)
    if session:
        return {
            "session_id": session.session_id,
            "question": session.question,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "response": session.response,
            "images_count": len(session.images),
            "files_count": len(session.files)
        }
    return None

def cleanup_expired_sessions(max_age_hours: int = 24):
    """清理过期会话"""
    now = datetime.now()
    expired_sessions = []
    
    for session_id, session in server_state.sessions.items():
        age = (now - session.created_at).total_seconds() / 3600
        if age > max_age_hours:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del server_state.sessions[session_id]
        logger.info(f"清理过期会话: {session_id}")
    
    return len(expired_sessions)

async def run_fastapi_server():
    """运行FastAPI服务器"""
    config = uvicorn.Config(
        app,
        host=server_state.host,
        port=server_state.web_port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

def run_mcp_only():
    """仅运行FastMCP服务器（用于MCP客户端连接）"""
    logger.info("启动FastMCP服务器（仅MCP模式）...")
    logger.info("使用 stdio 传输协议")
    logger.info("可以通过MCP客户端连接此服务器")

    # 运行FastMCP服务器
    mcp.run()

async def run_combined_server():
    """运行合并的服务器（MCP + FastAPI + WebSocket）"""
    logger.info("启动合并的MCP+FastAPI服务器...")

    # 启动消息队列处理任务
    queue_task = asyncio.create_task(process_message_queue())

    # 定期清理过期会话
    async def cleanup_task():
        while True:
            await asyncio.sleep(3600)  # 每小时清理一次
            cleaned = cleanup_expired_sessions()
            if cleaned > 0:
                logger.info(f"清理了 {cleaned} 个过期会话")

    cleanup_task_handle = asyncio.create_task(cleanup_task())

    # 移除测试任务，让服务器专注于处理真实的MCP客户端请求
    # test_task_handle = None

    try:
        logger.info("=" * 50)
        logger.info("服务器信息:")
        logger.info(f"  FastAPI服务器: http://{server_state.host}:{server_state.web_port}")
        logger.info(f"  React应用: http://{server_state.host}:{server_state.web_port}")
        logger.info(f"  API文档: http://{server_state.host}:{server_state.web_port}/docs")
        logger.info(f"  FastMCP服务器: stdio (通过当前进程)")
        logger.info("=" * 50)

        # 在后台启动FastAPI服务器
        fastapi_task = asyncio.create_task(run_fastapi_server())

        # 运行FastMCP服务器（阻塞）
        try:
            await asyncio.get_event_loop().run_in_executor(None, mcp.run)
        finally:
            # 确保FastAPI任务也被取消
            fastapi_task.cancel()
            try:
                await fastapi_task
            except asyncio.CancelledError:
                pass

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    finally:
        queue_task.cancel()
        cleanup_task_handle.cancel()
        # test_task_handle.cancel()  # 已移除测试任务
        logger.info("服务器已关闭")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-only":
        # 仅运行MCP服务器
        run_mcp_only()
    elif len(sys.argv) > 1 and sys.argv[1] == "--web-only":
        # 仅运行FastAPI服务器
        asyncio.run(run_fastapi_server())
    else:
        # 运行合并的服务器
        asyncio.run(run_combined_server())
