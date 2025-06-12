# FastMCP 反馈收集器

[![CI/CD Pipeline](https://github.com/Gitofxiongxiong/feedback-collector-py/actions/workflows/ci.yml/badge.svg)](https://github.com/Gitofxiongxiong/feedback-collector-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org/)

一个用于AI助手与用户实时交互的反馈收集工具，基于 [FastMCP](https://github.com/jlowin/fastmcp) 框架实现。

## 🚀 特性

- 🤖 **现代化 MCP 框架**：使用 FastMCP 2.0，更简洁的代码和更好的开发体验
- ⚡ **FastAPI 后端**：现代化的 Web 框架，自动生成 API 文档
- ⚛️ **React 前端**：基于 React + Tailwind CSS 的现代化用户界面
- 🌐 **实时 WebSocket 通信**：支持即时反馈和双向通信
- 📝 **Markdown 支持**：支持富文本格式的消息显示和语法高亮
- 🖼️ **多媒体支持**：支持图片上传、预览和复制
- 📎 **文件管理**：支持拖拽上传和文件管理
- 🔄 **智能会话管理**：自动清理过期会话和资源
- 🎨 **美观界面**：现代化的玻璃态设计和动画效果
- 🧪 **内置测试**：支持内存测试，开发更高效
- 📚 **自动文档**：Swagger UI 和 ReDoc 自动生成 API 文档
- 📱 **响应式设计**：完美适配桌面和移动设备

## 📋 快速开始

### 环境要求

- Python 3.10+
- FastMCP 2.0+
- FastAPI + Uvicorn
- Node.js 16+ (用于 React 前端)
- WebSockets 支持

### 安装

```bash
# 克隆仓库
git clone https://github.com/Gitofxiongxiong/feedback-collector-py.git
cd feedback-collector-py

# 安装 Python 依赖
pip install -r backend/requirements.txt

# 构建 React 前端（可选）
python start.py build
```

### 启动服务器

**方式1：完整服务器（推荐）**
```bash
python start.py start
```

**方式2：仅 MCP 服务器**
```bash
python start.py start --mcp-only
```

**方式3：使用 FastMCP CLI**
```bash
fastmcp run backend/mcp_server_fastmcp.py
```

## 🔧 使用方法

### 基本用法

```python
import sys
from pathlib import Path
from fastmcp import Client

# 添加后端路径
backend_dir = Path("backend")
sys.path.insert(0, str(backend_dir))
from mcp_server_fastmcp import mcp

# 内存测试（开发推荐）
async with Client(mcp) as client:
    result = await client.call_tool(
        "collect_feedback_mcp_feedback_collector",
        {
            "work_summary": "我已经完成了数据分析任务，请确认结果。",
            "require_response": False
        }
    )
    print(result[0].text)
```

### 工具参数

- `work_summary` (必需): AI工作汇报内容
- `timeout` (可选): 超时时间（秒），默认300
- `session_id` (可选): 会话ID，自动生成
- `require_response` (可选): 是否等待响应，默认true

## 🧪 测试

```bash
# 运行演示
python start.py demo

# 运行测试
python start.py test
```

## 📁 项目结构

```
├── start.py                 # 主启动脚本
├── README.md               # 项目文档
├── backend/                # 后端代码
│   ├── mcp_server_fastmcp.py      # FastMCP 服务器
│   ├── fastapi_server.py          # FastAPI Web 服务器
│   └── requirements.txt           # Python 依赖
├── frontend/               # 前端代码
│   ├── src/                       # React 源代码
│   │   ├── components/            # React 组件
│   │   ├── hooks/                 # 自定义 Hooks
│   │   ├── utils/                 # 工具函数
│   │   └── styles/                # 样式文件
│   ├── public/                    # 公共资源
│   ├── build/                     # React 构建输出
│   ├── package.json               # Node.js 依赖
│   ├── tailwind.config.js         # Tailwind 配置
│   ├── postcss.config.js          # PostCSS 配置
│   └── feedback_ui.html           # HTML 界面（传统版本）
├── scripts/                # 脚本文件
│   ├── start_servers_fastmcp.py   # 服务器启动脚本
│   ├── build_react.py            # React 构建脚本
│   └── demo_fastmcp.py           # 演示脚本
├── tests/                  # 测试文件
│   └── test_fastmcp_client.py    # 测试客户端
└── docs/                   # 文档
    ├── README_FastMCP.md          # 详细文档
    └── 迁移总结.md                # 迁移报告
```

## 🌐 API 接口

启动服务器后，可以访问以下接口：

- **主页**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **ReDoc 文档**: http://localhost:8000/redoc
- **React 界面**: http://localhost:8000/react (现代化版本)
- **HTML 界面**: http://localhost:8000/feedback_ui.html (传统版本)
- **健康检查**: http://localhost:8000/health
- **会话信息**: http://localhost:8000/api/session/{session_id}
- **WebSocket**: ws://localhost:8001/{session_id}

## ⚛️ React 前端特性

- **现代化设计**: 玻璃态效果和渐变背景
- **响应式布局**: 完美适配各种屏幕尺寸
- **实时连接状态**: 可视化 WebSocket 连接状态
- **拖拽上传**: 支持图片和文件拖拽上传
- **Markdown 渲染**: 实时渲染 Markdown 内容
- **语法高亮**: 代码块自动语法高亮
- **动画效果**: 流畅的过渡和加载动画
- **类型安全**: 完整的 TypeScript 支持（可选）

## 📚 文档

- [详细使用指南](README_FastMCP.md)
- [迁移报告](迁移总结.md)
- [FastMCP 官方文档](https://gofastmcp.com)

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## � 问题报告

如果发现 bug 或有功能建议，请在 [Issues](https://github.com/Gitofxiongxiong/feedback-collector-py/issues) 页面提交。

## �🔒 安全注意事项

- 默认仅允许本地访问
- 生产环境请配置适当的安全措施
- 考虑添加认证机制

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastMCP](https://github.com/jlowin/fastmcp) - 现代化的 MCP 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [React](https://reactjs.org/) - 用户界面库
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架

## 📞 联系

- GitHub: [@Gitofxiongxiong](https://github.com/Gitofxiongxiong)
- 项目链接: [https://github.com/Gitofxiongxiong/feedback-collector-py](https://github.com/Gitofxiongxiong/feedback-collector-py)