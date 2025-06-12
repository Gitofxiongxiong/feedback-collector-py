import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, Clock, Image as ImageIcon, FileText } from 'lucide-react';

const MessagePanel = ({ agentMessage, userMessages, isConnected }) => {
  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderMarkdown = (content) => {
    return (
      <ReactMarkdown
        className="prose prose-sm max-w-none"
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                className="rounded-lg"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            );
          },
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-gray-800 mb-3">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-gray-700 mb-2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-medium text-gray-600 mb-2">{children}</h3>
          ),
          p: ({ children }) => (
            <p className="text-gray-700 mb-2 leading-relaxed">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside text-gray-700 mb-2 space-y-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside text-gray-700 mb-2 space-y-1">{children}</ol>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-2">
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <div className="glass-effect rounded-2xl p-6 card-shadow h-[600px] flex flex-col">
      <div className="flex items-center space-x-2 mb-4">
        <Bot className="w-5 h-5 text-blue-500" />
        <h2 className="text-lg font-semibold text-white">对话记录</h2>
        {!isConnected && (
          <span className="text-red-400 text-sm">(未连接)</span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {/* Agent Message */}
        {agentMessage && (
          <div className="message-bubble message-agent">
            <div className="flex items-center space-x-2 mb-2">
              <Bot className="w-4 h-4 text-blue-500" />
              <span className="font-medium text-blue-700">AI 助手</span>
              <Clock className="w-3 h-3 text-gray-400" />
              <span className="text-xs text-gray-500">刚刚</span>
            </div>
            <div className="text-gray-700">
              {renderMarkdown(agentMessage)}
            </div>
          </div>
        )}

        {/* User Messages */}
        {userMessages.map((message, index) => (
          <div key={index} className={`message-bubble ${
            message.type === 'user' ? 'message-user' : 'bg-yellow-50 border-l-4 border-yellow-500'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              {message.type === 'user' ? (
                <>
                  <User className="w-4 h-4 text-green-500" />
                  <span className="font-medium text-green-700">您</span>
                </>
              ) : (
                <>
                  <Bot className="w-4 h-4 text-yellow-500" />
                  <span className="font-medium text-yellow-700">系统</span>
                </>
              )}
              <Clock className="w-3 h-3 text-gray-400" />
              <span className="text-xs text-gray-500">
                {formatTime(message.timestamp)}
              </span>
            </div>
            
            <div className="text-gray-700">
              {message.content && renderMarkdown(message.content)}
              
              {/* Images */}
              {message.images && message.images.length > 0 && (
                <div className="mt-3">
                  <div className="flex items-center space-x-1 mb-2">
                    <ImageIcon className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      图片 ({message.images.length})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {message.images.map((image, imgIndex) => (
                      <img
                        key={imgIndex}
                        src={image.url}
                        alt={image.name}
                        className="rounded-lg max-h-32 object-cover"
                      />
                    ))}
                  </div>
                </div>
              )}
              
              {/* Files */}
              {message.files && message.files.length > 0 && (
                <div className="mt-3">
                  <div className="flex items-center space-x-1 mb-2">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      文件 ({message.files.length})
                    </span>
                  </div>
                  <div className="space-y-1">
                    {message.files.map((file, fileIndex) => (
                      <div
                        key={fileIndex}
                        className="flex items-center space-x-2 p-2 bg-gray-100 rounded"
                      >
                        <FileText className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <span className="text-xs text-gray-500">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Empty State */}
        {!agentMessage && userMessages.length === 0 && (
          <div className="flex-1 flex items-center justify-center text-white/60">
            <div className="text-center">
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>等待 AI 助手消息...</p>
              <p className="text-sm mt-1">连接建立后将显示对话内容</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessagePanel;
