# Cyber-OpenAI

## 项目概述

Cyber-OpenAI 是 Cyber Engine 的 OpenAI 兼容 API 客户端，提供与 OpenAI API 格式兼容的接口，使第三方应用能够通过标准的 OpenAI 调用方式接入 Cyber Engine 的服务。

## 功能特点

- 提供与 OpenAI API 兼容的 HTTP 接口
- 支持流式和非流式响应
- 将请求转换为 Cyber Engine WebSocket 消息
- 用户认证和密钥管理
- 操作日志和使用统计

## 系统架构

```
第三方应用 <--HTTP--> Cyber-OpenAI <--WebSocket--> Cyber Engine
```

### 核心组件

1. **HTTP 服务器**：处理 OpenAI 兼容的 HTTP 请求
2. **WebSocket 客户端**：与 Cyber Engine 建立连接
3. **请求转换器**：将 OpenAI 格式请求转换为 Cyber Engine 格式
4. **响应转换器**：将 Cyber Engine 响应转换为 OpenAI 格式
5. **认证管理器**：管理 API 密钥和用户认证

## 安装与配置

### 环境要求

- Python 3.8+
- 依赖库：见 `requirements.txt`

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/your-username/cyber-openai.git
   cd cyber-openai
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境
   - 复制 `.env.example` 到 `.env`
   - 配置 Cyber Engine 连接信息
   - 配置 API 服务参数

4. 启动服务
   ```bash
   python main.py
   ```

## 配置说明

`.env` 文件中的主要配置项：

```ini
# HTTP服务配置
HOST=0.0.0.0
PORT=8000

# Cyber Engine配置
CYBER_ENGINE_HOST=127.0.0.1
CYBER_ENGINE_PORT=6898

# 安全配置
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=https://example.com,https://app.example.com

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## API参考

### 聊天完成 API

```
POST /v1/chat/completions
```

#### 请求参数

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
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### 响应格式

**流式响应**:
```json
{
  "id": "chatcmpl-xxxxxxxxxxxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "ena-test",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "部分响应内容"
      },
      "finish_reason": null
    }
  ]
}
```

**非流式响应**:
```json
{
  "id": "chatcmpl-xxxxxxxxxxxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "ena-test",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "完整响应内容"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 50,
    "total_tokens": 70
  }
}
```

### 模型列表 API

```
GET /v1/models
```

返回可用模型列表：

```json
{
  "object": "list",
  "data": [
    {
      "id": "ena-test",
      "object": "model",
      "created": 1686935002,
      "owned_by": "organization-owner"
    }
  ]
}
```

## 认证与安全

Cyber-OpenAI 使用基于 API 密钥的认证机制：

1. 在请求头中包含 API 密钥：
   ```
   Authorization: Bearer sk-your-api-key
   ```

2. API 密钥由服务管理员通过管理界面创建和分配

3. 所有请求都会进行身份验证和权限检查

## 开发指南

### 添加新的 API 端点

在 `routes.py` 中添加新的 API 端点：

```python
@app.post("/v1/new_endpoint")
async def new_endpoint(request: NewRequestModel):
    # 处理请求逻辑
    return response
```

### 扩展请求转换器

在 `converters.py` 中添加新的请求转换逻辑：

```python
def convert_new_request(openai_request):
    # 转换逻辑
    return cyber_engine_request
```

## 故障排除

- **连接问题**：检查 Cyber Engine 服务器是否运行，以及连接信息是否正确
- **认证问题**：确认 API 密钥格式正确并且有效
- **请求格式问题**：确保请求符合 OpenAI API 规范

## 性能优化

- 使用异步处理提高并发能力
- 实现请求缓存减少重复处理
- 使用连接池管理 WebSocket 连接
- 添加请求速率限制防止滥用 