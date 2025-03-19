# <div align="center">Cyber Engine</div>

---
<div align="center">
<p><strong>基于 WebSocket 的智能对话引擎，支持知识库问答和指令执行</strong></p>
<a href="https://opensource.org/licenses/Apache-2.0"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-green.svg"></a>
<a><img alt="Static Badge" src="https://img.shields.io/badge/made_with-Python-blue"></a>
</div>

## 项目简介

Cyber Engine 是一个基于 WebSocket 协议的智能对话引擎系统，通过结合大语言模型与知识库系统，提供智能问答和指令执行功能。系统可以自动识别用户输入类型，并将其路由到相应的处理流程。

> [!NOTE]
> 此项目使用WebSocket协议进行通信，如需接入其他平台系统，请按照对应的接入规范进行接入。

## 主要功能

- **智能路由**: 自动识别用户输入类型（问题/指令），并路由到相应处理流程
- **知识库问答**: 连接外部知识库，检索相关信息回答问题
- **指令执行**: 解析并执行用户指令，支持复杂功能调用
- **消息历史**: 维护用户会话历史，提供上下文支持
- **任务管理**: 支持长时间运行任务的创建和管理
- **命令系统**: 提供特殊命令，用于系统控制和状态查询

## 快速开始

### 安装

1. 克隆仓库
   ```bash
   git clone https://github.com/your-username/cyber_engine.git
   cd cyber_engine
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置必要参数
   ```

4. 启动服务
   ```bash
   python start_main_server.py
   ```

### 使用方法

通过 WebSocket 客户端连接服务：

```javascript
// 示例代码 (JavaScript)
const ws = new WebSocket('ws://localhost:6898/your_auth_token');

ws.onopen = () => {
  console.log('连接已建立');
  ws.send(JSON.stringify({
    content: '你好，请问如何使用这个系统？',
    model: 'ena-test'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};
```

## 系统架构

Cyber Engine 由多个核心组件组成：

- **WebSocket 服务**: 处理客户端连接和消息传递
- **引擎核心 (Ponder)**: 自动路由和处理用户输入
- **路由代理**: 判断输入类型（问题/指令）
- **指令处理器**: 解析并执行用户指令
- **知识库查询**: 检索知识并生成答案
- **插件系统**: 提供可扩展功能

详细架构说明请参见 [架构文档](docs/architecture.md)。

## 扩展客户端

Cyber Engine 提供了多种接入方式，方便与不同平台集成：

### cyber-qbot

QQ机器人客户端，将服务接入QQ平台，实现通过QQ与系统交互。

[查看详情](docs/clients/cyber-qbot.md)

### cyber-openai

OpenAI兼容API客户端，提供与OpenAI API格式兼容的接口，方便与现有生态集成。

[查看详情](docs/clients/cyber-openai.md)

## 文档指南

- [API 文档](docs/api.md) - WebSocket通信格式和命令系统
- [配置指南](docs/README.md#配置说明) - 环境配置和参数说明
- [部署指南](docs/README.md#部署指南) - 部署步骤和环境要求
- [开发指南](docs/README.md#开发指南) - 扩展开发和贡献代码

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

