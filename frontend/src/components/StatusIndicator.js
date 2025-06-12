import React from 'react';
import { Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';

const StatusIndicator = ({ isConnected, status }) => {
  const getStatusConfig = () => {
    if (isConnected) {
      return {
        icon: CheckCircle,
        text: '已连接',
        color: 'text-green-400',
        bgColor: 'bg-green-400/20',
        dotColor: 'bg-green-400'
      };
    } else if (status === 'connecting') {
      return {
        icon: AlertCircle,
        text: '连接中',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-400/20',
        dotColor: 'bg-yellow-400'
      };
    } else {
      return {
        icon: WifiOff,
        text: '未连接',
        color: 'text-red-400',
        bgColor: 'bg-red-400/20',
        dotColor: 'bg-red-400'
      };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full ${config.bgColor}`}>
      <div className="relative">
        <Icon className={`w-4 h-4 ${config.color}`} />
        {isConnected && (
          <div className={`absolute -top-1 -right-1 w-2 h-2 ${config.dotColor} rounded-full animate-pulse`}></div>
        )}
      </div>
      <span className={`text-sm font-medium ${config.color}`}>
        {config.text}
      </span>
    </div>
  );
};

export default StatusIndicator;
