# Cyber-QBot

## 项目概述

Cyber-QBot 是 Cyber Engine 的 QQ 机器人客户端，用于将 Cyber Engine 的智能对话功能接入到 QQ 聊天平台，使用户可以通过 QQ 聊天与 Cyber Engine 进行交互。

## 功能特点

- 接收 QQ 消息并转发到 Cyber Engine
- 将 Cyber Engine 的响应转发回 QQ
- 支持私聊和群聊消息处理
- 支持命令系统和权限管理
- 提供用户身份绑定和配额管理

## 系统架构

```
QQ平台 <--> Cyber-QBot <--WebSocket--> Cyber Engine
```

### 核心组件

1. **消息接收器**：接收来自 QQ 平台的消息
2. **消息处理器**：解析和处理 QQ 消息
3. **WebSocket 客户端**：与 Cyber Engine 建立连接
4. **响应处理器**：处理 Cyber Engine 的响应并转发到 QQ
5. **用户管理器**：管理用户身份和权限

## 安装与配置

### 环境要求

- Python 3.8+
- 依赖库：见 `requirements.txt`

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/your-username/cyber-qbot.git
   cd cyber-qbot
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境
   - 复制 `.env.example` 到 `.env`
   - 配置 QQ 机器人账号信息
   - 配置 Cyber Engine 连接信息

4. 启动服务
   ```bash
   python main.py
   ```

## 配置说明

`.env` 文件中的主要配置项：

```ini
# QQ 机器人配置
QQ_ACCOUNT=123456789
QQ_PASSWORD=your_password
QQ_PROTOCOL=5  # QQ协议版本

# Cyber Engine 配置
CYBER_ENGINE_HOST=127.0.0.1
CYBER_ENGINE_PORT=6898
CYBER_ENGINE_TOKEN=your_token

# 权限配置
ADMIN_QQ=admin_qq_number
ALLOWED_GROUPS=group1,group2
```

## 使用方法

### 基本使用

在 QQ 私聊或已授权的群聊中，直接发送消息即可获得 Cyber Engine 的回复。

### 命令系统

Cyber-QBot 支持以下特殊命令：

| 命令 | 描述 |
|------|------|
| `/help` | 显示帮助信息 |
| `/bind [token]` | 绑定用户账号 |
| `/unbind` | 解绑用户账号 |
| `/quota` | 查询配额使用情况 |
| `/admin [command]` | 管理员命令 |

### 权限管理

Cyber-QBot 提供三级权限系统：

1. **管理员**：可以执行所有命令，包括系统管理命令
2. **绑定用户**：已绑定账号的普通用户，可以使用基本功能
3. **访客**：未绑定账号的用户，功能受限

## 开发指南

### 添加新命令

在 `commands.py` 中添加新命令处理函数：

```python
@command_handler('/new_command')
async def handle_new_command(message, args):
    # 处理命令逻辑
    return response
```

### 自定义消息处理

在 `message_handler.py` 中扩展消息处理逻辑：

```python
async def process_message(message):
    # 自定义消息处理逻辑
```

## 故障排除

- **连接问题**：检查 Cyber Engine 服务器是否运行，以及连接配置是否正确
- **QQ 登录问题**：确认 QQ 账号和密码正确，可能需要处理验证码
- **消息处理异常**：查看日志文件 `logs/runtime.log`

## 贡献指南

欢迎提交 Pull Request 或 Issue 来改进 Cyber-QBot。在提交代码前，请确保：

1. 代码符合项目的代码风格
2. 添加了必要的测试
3. 更新了相关文档 