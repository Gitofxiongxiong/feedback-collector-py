import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (sessionId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!sessionId) return;

    try {
      setConnectionStatus('connecting');
      
      // 使用当前页面的协议来决定 WebSocket 协议
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:8001/ws/${sessionId}`;
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket 连接已建立');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        console.log('收到 WebSocket 消息:', event.data);
        setLastMessage(event);
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket 连接已关闭:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        
        // 自动重连逻辑
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`${delay}ms 后尝试重连 (${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        setConnectionStatus('error');
      };

    } catch (error) {
      console.error('创建 WebSocket 连接失败:', error);
      setConnectionStatus('error');
    }
  }, [sessionId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(message));
        console.log('发送 WebSocket 消息:', message);
        return true;
      } catch (error) {
        console.error('发送 WebSocket 消息失败:', error);
        return false;
      }
    } else {
      console.warn('WebSocket 未连接，无法发送消息');
      return false;
    }
  }, []);

  // 初始连接
  useEffect(() => {
    if (sessionId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [sessionId, connect, disconnect]);

  // 页面可见性变化时重连
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected && sessionId) {
        console.log('页面变为可见，尝试重连 WebSocket');
        connect();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected, sessionId, connect]);

  // 网络状态变化时重连
  useEffect(() => {
    const handleOnline = () => {
      if (!isConnected && sessionId) {
        console.log('网络恢复，尝试重连 WebSocket');
        setTimeout(() => connect(), 1000);
      }
    };

    window.addEventListener('online', handleOnline);
    return () => {
      window.removeEventListener('online', handleOnline);
    };
  }, [isConnected, sessionId, connect]);

  return {
    isConnected,
    connectionStatus,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
};
