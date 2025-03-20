# Cyber Engine API 文档

## WebSocket 通信

Cyber Engine 使用 WebSocket 协议提供实时通信功能。客户端可以通过 WebSocket 连接发送消息并接收流式响应。

### 连接地址

```
ws://{host}:{port}/{authorization}
```

- `host`：服务器主机地址，默认为 `127.0.0.1`
- `port`：服务端口，默认为 `6898`
- `authorization`：用户授权标识，用于身份认证和会话管理

### 消息格式

#### 客户端请求

客户端发送 JSON 格式的消息：

```json
{
  "content": "用户输入的内容",
  "model": "模型名称"
}
```

其中：
- `content`：用户输入的文本内容，可以是问题或指令
- `model`：可选，指定使用的模型名称

#### 服务器响应

服务器以流式方式返回 JSON 格式的响应块：

```json
{
  "id": "chatcmpl-xxxxxxxxxxxx",
  "model": "模型名称",
  "choices": [
    {
      "delta": {
        "role": "assistant",
        "content": "部分响应内容"
      },
      "index": 0,
      "logprobs": null,
      "finish_reason": null
    }
  ],
  "created": 1234567890,
  "object": "chat.completion.chunk",
  "system_fingerprint": "系统指纹"
}
```

最后一个响应块的 `finish_reason` 字段会设置为 "stop"，表示响应结束。

## 命令系统

Cyber Engine 提供了一系列以 "/" 开头的特殊命令，用于执行特定功能。

### 基本命令

| 命令 | 描述 |
|------|------|
| `/help` | 显示帮助信息和可用命令列表 |
| `/clear` | 清除当前会话历史 |
| `/version` | 显示系统版本信息 |
| `/status` | 显示系统状态信息 |

### 任务命令

| 命令 | 描述 |
|------|------|
| `/task list` | 列出当前用户的所有任务 |
| `/task get [task_id]` | 获取指定任务的详细信息 |
| `/task run [task_id]` | 执行指定的任务 |
| `/task delete [task_id]` | 删除指定的任务 |

### 示例

#### 帮助命令示例

客户端发送：
```json
{
  "content": "/help",
  "model": "ena-test"
}
```

服务器响应（流式）：
```
可用命令列表：
/help - 显示此帮助信息
/clear - 清除当前会话历史
/version - 显示系统版本信息
/status - 显示系统状态信息
/task list - 列出所有任务
/task get [task_id] - 获取任务详情
/task run [task_id] - 执行任务
/task delete [task_id] - 删除任务
```

## 扩展客户端 API

### cyber-openai

cyber-openai 客户端提供与 OpenAI API 兼容的接口，使第三方应用能够轻松集成。

#### 聊天补全 API
```
POST /v1/chat/completions
```

请求体格式：
```json
{
  "model": "ena-test",
  "messages": [
    {
      "role": "system",
      "content": "系统提示"
    },
    {
      "role": "user",
      "content": "用户消息"
    }
  ],
  "stream": true
}
```

响应格式与标准 OpenAI API 保持一致。

### cyber-qbot

cyber-qbot 客户端将服务接入到 QQ 机器人平台，允许用户通过 QQ 消息与系统交互。

#### 消息处理流程

1. 接收来自 QQ 平台的消息
2. 将消息转换为 Cyber Engine 的请求格式
3. 通过 WebSocket 发送请求
4. 接收响应并转换为 QQ 消息格式
5. 回复用户

#### 命令支持

cyber-qbot 支持所有 Cyber Engine 的命令，并添加了 QQ 平台特定的命令：

| 命令 | 描述 |
|------|------|
| `/bind [token]` | 绑定用户账号 |
| `/unbind` | 解绑用户账号 |
| `/quota` | 查询用户配额使用情况 | 