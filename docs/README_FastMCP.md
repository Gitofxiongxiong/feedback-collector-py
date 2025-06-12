# FastMCP 反馈收集器

这是使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架重构的 MCP 反馈收集服务器。FastMCP 提供了更简洁、更现代的方式来构建 MCP 服务器。

## 主要改进

### 🚀 使用 FastMCP 框架
- 更简洁的代码结构
- 装饰器模式的工具注册
- 内置的客户端支持
- 更好的错误处理

### 🔧 保留原有功能
- 完整的反馈收集功能
- WebSocket 实时通信
- Web 界面支持
- 会话管理

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `fastmcp>=2.0.0` - FastMCP 框架
- `websockets>=12.0` - WebSocket 支持
- `pydantic>=2.0.0` - 数据验证

## 使用方法

### 1. 完整服务器模式（推荐）

启动包含 Web 界面和 MCP 服务器的完整服务：

```bash
python start_servers_fastmcp.py
```

这将启动：
- HTTP 服务器 (端口 8000) - 提供 Web 界面
- WebSocket 服务器 (端口 8001) - 实时通信
- FastMCP 服务器 - MCP 工具服务

### 2. 仅 MCP 服务器模式

如果只需要 MCP 服务器（用于 MCP 客户端连接）：

```bash
python start_servers_fastmcp.py --mcp-only
```

或者直接运行：

```bash
python mcp_server_fastmcp.py
```

### 3. 使用 FastMCP CLI

```bash
fastmcp run mcp_server_fastmcp.py
```

## 工具说明

### collect_feedback_mcp_feedback_collector

收集用户反馈的工具，参数：

- `work_summary` (必需): AI工作汇报内容，描述AI完成的工作和结果
- `timeout` (可选): 等待用户响应的超时时间（秒），默认300秒
- `session_id` (可选): 会话ID，如果不提供将自动生成
- `require_response` (可选): 是否要求用户必须响应，默认true

## 测试

### 运行测试客户端

```bash
python test_fastmcp_client.py
```

测试脚本包含：
1. 内存中测试（直接连接服务器对象）
2. Stdio 连接测试
3. 用户响应场景测试

### 手动测试

1. 启动完整服务器：
   ```bash
   python start_servers_fastmcp.py
   ```

2. 在另一个终端中运行客户端：
   ```bash
   python test_fastmcp_client.py
   ```

3. 访问 Web 界面：
   ```
   http://localhost:8000/feedback_ui.html?session=<session_id>
   ```

## 文件结构

```
├── mcp_server_fastmcp.py      # 新的 FastMCP 服务器
├── start_servers_fastmcp.py   # 集成启动脚本
├── test_fastmcp_client.py     # 测试客户端
├── requirements.txt           # 更新的依赖
├── README_FastMCP.md         # 本文档
├── mcp_server.py             # 原始 MCP 服务器（保留）
├── http_server.py            # HTTP 服务器
├── feedback_ui.html          # Web 界面
└── start_servers.py          # 原始启动脚本（保留）
```

## 与原版本的对比

| 特性 | 原版本 | FastMCP 版本 |
|------|--------|-------------|
| 框架 | 原生 MCP SDK | FastMCP 2.0 |
| 代码行数 | ~376 行 | ~300 行 |
| 工具注册 | 手动注册 | 装饰器模式 |
| 客户端支持 | 需要额外实现 | 内置客户端 |
| 测试 | 复杂 | 简单（内存测试） |
| 错误处理 | 手动 | 框架内置 |

## 开发建议

1. **优先使用 FastMCP 版本** - 更现代、更易维护
2. **保留原版本作为参考** - 了解底层 MCP 协议实现
3. **使用内存测试** - 开发时使用 `Client(mcp)` 进行快速测试
4. **生产部署** - 使用完整服务器模式

## 故障排除

### 常见问题

1. **FastMCP 导入错误**
   ```bash
   pip install fastmcp>=2.0.0
   ```

2. **端口冲突**
   - 检查端口 8000 和 8001 是否被占用
   - 修改 `server_state` 中的端口配置

3. **WebSocket 连接失败**
   - 确保 WebSocket 服务器已启动
   - 检查防火墙设置

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 下一步

1. 考虑添加认证功能
2. 实现更多的 MCP 资源和提示
3. 添加配置文件支持
4. 实现数据持久化
