#!/usr/bin/env python3
"""
FastAPI Web服务器
提供反馈UI页面和API接口，支持静态文件服务和会话管理
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str
    question: str
    status: str
    created_at: str
    response: Optional[str] = None
    images_count: int = 0
    files_count: int = 0

class FeedbackData(BaseModel):
    """反馈数据模型"""
    text: str
    images: list = []
    files: list = []

# 创建 FastAPI 应用
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

# WebSocket 连接管理
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
                logger.error(f"发送消息失败: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

# 路由定义
@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径，返回欢迎页面"""
    return """
    <html>
        <head>
            <title>MCP 反馈收集器</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .card { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .link { color: #007bff; text-decoration: none; }
                .link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 MCP 反馈收集器</h1>
                    <p>基于 FastMCP 和 FastAPI 的现代化反馈收集系统</p>
                </div>
                
                <div class="card">
                    <h3>📱 反馈界面</h3>
                    <p>
                        <a href="/feedback_ui.html" class="link">HTML 版本</a> -
                        传统的 HTML 界面
                    </p>
                    <p>
                        <a href="/react" class="link">React 版本</a> -
                        现代化的 React 应用
                    </p>
                    <p>需要会话ID参数，例如: <code>?session=your-session-id</code></p>
                </div>
                
                <div class="card">
                    <h3>🔌 API 接口</h3>
                    <ul>
                        <li><a href="/docs" class="link">API 文档</a> - Swagger UI</li>
                        <li><a href="/redoc" class="link">ReDoc 文档</a> - 替代文档界面</li>
                    </ul>
                </div>
                
                <div class="card">
                    <h3>🔧 技术栈</h3>
                    <ul>
                        <li><strong>后端:</strong> FastAPI + FastMCP</li>
                        <li><strong>前端:</strong> HTML + JavaScript + WebSocket</li>
                        <li><strong>通信:</strong> WebSocket + HTTP API</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/feedback_ui.html", response_class=FileResponse)
async def get_feedback_ui():
    """返回反馈UI页面（HTML版本）"""
    frontend_dir = Path(__file__).parent.parent / "frontend"
    ui_file = frontend_dir / "feedback_ui.html"
    if ui_file.exists():
        return FileResponse(ui_file)
    else:
        raise HTTPException(status_code=404, detail="反馈UI页面未找到")

# 静态文件服务（用于 React 应用）
frontend_dir = Path(__file__).parent.parent / "frontend"
static_dir = frontend_dir / "build" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/react", response_class=FileResponse)
async def get_react_app():
    """返回 React 应用"""
    react_file = frontend_dir / "build" / "index.html"
    if react_file.exists():
        return FileResponse(react_file)
    else:
        raise HTTPException(status_code=404, detail="React 应用未找到，请先运行 python start.py build")

@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        # 导入服务器状态
        from mcp_server_fastmcp import get_session_info
        
        session_info = get_session_info(session_id)
        if session_info:
            return SessionInfo(**session_info)
        else:
            raise HTTPException(status_code=404, detail="会话未找到")
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@app.post("/api/session/{session_id}/feedback")
async def submit_feedback(session_id: str, feedback: FeedbackData):
    """提交反馈数据"""
    try:
        # 发送反馈到 WebSocket
        await manager.send_message(session_id, {
            "type": "user_feedback",
            "data": {
                "text": feedback.text,
                "images": feedback.images,
                "files": feedback.files
            }
        })
        
        return {"status": "success", "message": "反馈已提交"}
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail="提交反馈失败")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 端点"""
    await manager.connect(websocket, session_id)
    
    try:
        # 如果会话存在，发送初始消息
        from mcp_server_fastmcp import get_session_info
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
                from mcp_server_fastmcp import server_state
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

# 启动函数
def run_server(host: str = "localhost", port: int = 8000):
    """运行 FastAPI 服务器"""
    logger.info(f"启动 FastAPI 服务器: http://{host}:{port}")
    logger.info(f"API 文档: http://{host}:{port}/docs")
    logger.info(f"反馈界面: http://{host}:{port}/feedback_ui.html")
    
    uvicorn.run(
        "fastapi_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()
