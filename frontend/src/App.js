import React, { useState, useEffect } from 'react';
import { MessageSquare, Bot, User, Wifi, WifiOff } from 'lucide-react';
import FeedbackForm from './components/FeedbackForm';
import MessagePanel from './components/MessagePanel';
import StatusIndicator from './components/StatusIndicator';
import { useWebSocket } from './hooks/useWebSocket';
import { getSessionId } from './utils/session';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [agentMessage, setAgentMessage] = useState('');
  const [userMessages, setUserMessages] = useState([]);
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const { 
    isConnected, 
    connectionStatus, 
    sendMessage, 
    lastMessage 
  } = useWebSocket(sessionId);

  useEffect(() => {
    // 初始化会话ID
    const id = getSessionId();
    setSessionId(id);
  }, []);

  useEffect(() => {
    // 处理WebSocket消息
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      
      if (data.type === 'agent_message') {
        setAgentMessage(data.content);
      } else if (data.type === 'feedback_received') {
        setUserMessages(prev => [...prev, {
          type: 'system',
          content: data.message,
          timestamp: new Date()
        }]);
      } else if (data.type === 'session_complete') {
        setIsSubmitted(true);
      }
    }
  }, [lastMessage]);

  const handleFeedbackSubmit = (feedbackData) => {
    // 添加用户消息到界面
    setUserMessages(prev => [...prev, {
      type: 'user',
      content: feedbackData.text,
      images: feedbackData.images,
      files: feedbackData.files,
      timestamp: new Date()
    }]);

    // 发送到WebSocket
    sendMessage({
      type: 'user_feedback',
      data: feedbackData
    });
  };

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>正在初始化会话...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="glass-effect rounded-2xl p-6 mb-6 card-shadow">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  🤖 MCP 反馈收集器
                </h1>
                <p className="text-white/80">
                  基于 FastMCP + React 的智能反馈系统
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <StatusIndicator 
                isConnected={isConnected} 
                status={connectionStatus} 
              />
              <div className="text-white/60 text-sm">
                会话: {sessionId.slice(-8)}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Messages Panel */}
          <div className="lg:col-span-2">
            <MessagePanel 
              agentMessage={agentMessage}
              userMessages={userMessages}
              isConnected={isConnected}
            />
          </div>

          {/* Feedback Form */}
          <div className="lg:col-span-1">
            <FeedbackForm 
              onSubmit={handleFeedbackSubmit}
              isDisabled={isSubmitted || !isConnected}
              isSubmitted={isSubmitted}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-white/60 text-sm">
          <p>
            Powered by{' '}
            <span className="font-semibold text-white/80">FastMCP</span>
            {' + '}
            <span className="font-semibold text-white/80">React</span>
            {' + '}
            <span className="font-semibold text-white/80">FastAPI</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
