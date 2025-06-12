#!/usr/bin/env python3
"""
FastMCP反馈收集服务器
使用FastMCP框架提供collect_feedback工具，支持实时用户反馈收集
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

import websockets
from websockets.server import WebSocketServerProtocol
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
    websocket: Optional[WebSocketServerProtocol] = None
    
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

# 全局状态管理
class ServerState:
    def __init__(self):
        self.sessions: Dict[str, FeedbackSession] = {}
        self.websocket_clients: Dict[str, WebSocketServerProtocol] = {}
        self.websocket_server = None
        self.host = "localhost"
        self.websocket_port = 8001
        self.web_port = 8000

# 全局服务器状态
server_state = ServerState()

@mcp.tool
async def collect_feedback_mcp_feedback_collector(
    work_summary: str,
    timeout: int = 300,
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
        
        # 生成反馈页面URL
        feedback_url = f"http://{server_state.host}:{server_state.web_port}/feedback_ui.html?session={session_id}"
        
        # 如果有WebSocket连接，发送消息
        if session_id in server_state.websocket_clients:
            await _send_to_websocket(session_id, {
                "type": "agent_message",
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

async def _send_to_websocket(session_id: str, message: Dict[str, Any]):
    """发送消息到WebSocket客户端"""
    if session_id in server_state.websocket_clients:
        try:
            websocket = server_state.websocket_clients[session_id]
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
            # 清理断开的连接
            if session_id in server_state.websocket_clients:
                del server_state.websocket_clients[session_id]

async def handle_websocket_connection(websocket: WebSocketServerProtocol, path: str):
    """处理WebSocket连接"""
    # 从路径中提取会话ID
    session_id = path.split('/')[-1] if '/' in path else None
    
    if not session_id:
        await websocket.close(code=4000, reason="缺少会话ID")
        return
    
    logger.info(f"WebSocket连接建立: {session_id}")
    server_state.websocket_clients[session_id] = websocket
    
    # 如果会话存在，发送初始消息
    if session_id in server_state.sessions:
        session = server_state.sessions[session_id]
        session.websocket = websocket
        await _send_to_websocket(session_id, {
            "type": "agent_message",
            "content": session.question
        })
    
    try:
        async for message in websocket:
            await _handle_websocket_message(session_id, json.loads(message))
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket连接关闭: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
    finally:
        # 清理连接
        if session_id in server_state.websocket_clients:
            del server_state.websocket_clients[session_id]

async def _handle_websocket_message(session_id: str, message: Dict[str, Any]):
    """处理WebSocket消息"""
    try:
        if message.get("type") == "user_feedback":
            data = message.get("data", {})
            
            # 更新会话
            if session_id in server_state.sessions:
                session = server_state.sessions[session_id]
                session.response = data.get("text", "")
                session.images = data.get("images", [])
                session.files = data.get("files", [])
                session.status = "completed"
                
                logger.info(f"收到用户反馈: {session_id}")
                
                # 发送确认消息
                await _send_to_websocket(session_id, {
                    "type": "feedback_received",
                    "message": "反馈已收到，谢谢！"
                })
                
                # 通知会话完成
                await _send_to_websocket(session_id, {
                    "type": "session_complete"
                })
                
    except Exception as e:
        logger.error(f"处理WebSocket消息时出错: {e}")

async def start_websocket_server():
    """启动WebSocket服务器"""
    logger.info(f"启动WebSocket服务器: ws://{server_state.host}:{server_state.websocket_port}")
    server_state.websocket_server = await websockets.serve(
        handle_websocket_connection,
        server_state.host,
        server_state.websocket_port
    )

async def stop_websocket_server():
    """停止WebSocket服务器"""
    if server_state.websocket_server:
        server_state.websocket_server.close()
        await server_state.websocket_server.wait_closed()

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

if __name__ == "__main__":
    async def main():
        """主函数"""
        # 启动WebSocket服务器
        await start_websocket_server()
        
        try:
            logger.info("FastMCP反馈收集服务器已启动")
            logger.info(f"WebSocket服务器: ws://{server_state.host}:{server_state.websocket_port}")
            logger.info(f"Web界面: http://{server_state.host}:{server_state.web_port}/feedback_ui.html")
            
            # 定期清理过期会话
            async def cleanup_task():
                while True:
                    await asyncio.sleep(3600)  # 每小时清理一次
                    cleaned = cleanup_expired_sessions()
                    if cleaned > 0:
                        logger.info(f"清理了 {cleaned} 个过期会话")
            
            # 启动清理任务
            cleanup_task_handle = asyncio.create_task(cleanup_task())
            
            try:
                # 运行FastMCP服务器
                mcp.run()
            finally:
                cleanup_task_handle.cancel()
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        finally:
            await stop_websocket_server()
            logger.info("服务器已关闭")
    
    asyncio.run(main())
