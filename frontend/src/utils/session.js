/**
 * 会话管理工具函数
 */

/**
 * 从 URL 参数或生成新的会话ID
 * @returns {string} 会话ID
 */
export const getSessionId = () => {
  // 首先尝试从 URL 参数获取
  const urlParams = new URLSearchParams(window.location.search);
  const sessionFromUrl = urlParams.get('session');
  
  if (sessionFromUrl) {
    return sessionFromUrl;
  }
  
  // 如果没有，生成新的会话ID
  const newSessionId = generateSessionId();
  
  // 更新 URL 参数（不刷新页面）
  const newUrl = new URL(window.location);
  newUrl.searchParams.set('session', newSessionId);
  window.history.replaceState({}, '', newUrl);
  
  return newSessionId;
};

/**
 * 生成唯一的会话ID
 * @returns {string} 新的会话ID
 */
export const generateSessionId = () => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return `session_${timestamp}_${random}`;
};

/**
 * 验证会话ID格式
 * @param {string} sessionId 会话ID
 * @returns {boolean} 是否有效
 */
export const isValidSessionId = (sessionId) => {
  if (!sessionId || typeof sessionId !== 'string') {
    return false;
  }
  
  // 检查基本格式
  const sessionPattern = /^session_\d+_[a-z0-9]+$/;
  return sessionPattern.test(sessionId);
};

/**
 * 从会话ID提取时间戳
 * @param {string} sessionId 会话ID
 * @returns {Date|null} 创建时间
 */
export const getSessionTimestamp = (sessionId) => {
  if (!isValidSessionId(sessionId)) {
    return null;
  }
  
  try {
    const parts = sessionId.split('_');
    const timestamp = parseInt(parts[1], 10);
    return new Date(timestamp);
  } catch (error) {
    return null;
  }
};

/**
 * 检查会话是否过期
 * @param {string} sessionId 会话ID
 * @param {number} maxAgeHours 最大年龄（小时）
 * @returns {boolean} 是否过期
 */
export const isSessionExpired = (sessionId, maxAgeHours = 24) => {
  const timestamp = getSessionTimestamp(sessionId);
  if (!timestamp) {
    return true;
  }
  
  const now = new Date();
  const ageHours = (now - timestamp) / (1000 * 60 * 60);
  return ageHours > maxAgeHours;
};

/**
 * 格式化会话ID用于显示
 * @param {string} sessionId 会话ID
 * @returns {string} 格式化的显示文本
 */
export const formatSessionId = (sessionId) => {
  if (!sessionId) {
    return '未知';
  }
  
  // 显示最后8个字符
  return sessionId.slice(-8);
};

/**
 * 获取会话的显示信息
 * @param {string} sessionId 会话ID
 * @returns {object} 会话信息
 */
export const getSessionInfo = (sessionId) => {
  const timestamp = getSessionTimestamp(sessionId);
  const isExpired = isSessionExpired(sessionId);
  const displayId = formatSessionId(sessionId);
  
  return {
    id: sessionId,
    displayId,
    timestamp,
    isExpired,
    isValid: isValidSessionId(sessionId),
    createdAt: timestamp ? timestamp.toLocaleString('zh-CN') : '未知'
  };
};
