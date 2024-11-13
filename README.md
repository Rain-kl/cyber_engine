# <div align="center">智护精灵：基于多模态大模型的智能医护小助手<div>

---
<div align="center">
<p><strong>本项目旨在为智能护理系统提供一个结合长记忆和功能调用的多模态大模型接口，满足护理决策专业化和智能化的多样化应用需求。</strong></p>
<a href="https://opensource.org/licenses/Apache-2.0"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-green.svg"></a>
<a><img alt="Static Badge" src="https://img.shields.io/badge/made_with-Python-blue"></a>
</div>

> [!NOTE]
> 本项目为开源项目，使用者必须在遵循 OpenAI 的[使用条款](https://openai.com/policies/terms-of-use)以及**法律法规**的情况下使用，不得用于非法用途。
>
> 根据[《生成式人工智能服务管理暂行办法》](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)的要求，请勿对中国地区公众提供一切未经备案的生成式人工智能服务。
>
> 此项目使用WebSocket协议进行通信，如需接入其他平台系统，请按照对应的接入规范进行接入。
> 

## 概述

本项目提出了一种结合检索增强、长记忆和功能调用的多模态大模型应用方法，通过本地医疗知识库和向量检索提升智能护理决策的专业性和效率，并通过功能调用模块灵活应对复杂护理任务需求，同时确保用户隐私与数据安全。

![Preview](https://raw.githubusercontent.com/Rain-kl/cyber_engine/main/docs/images/dietary_recommendations_flow.png)

## 功能
1. 支持多种大模型
2. 支持导入本地知识库
3. 支持向量检索
4. 支持功能调用
5. 支持输入分类
6. 支持记忆存储

## 待开发
1. 支持多模态输入
2. 图形化界面开发


## 部署

---

### 手动部署

- 克隆本项目到本地

```bash
git clone https://github.com/Rain-kl/cyber_engine.git
```

- 安装依赖

```bash
pip install -r requirements.txt
```

- 运行项目

```bash
# 启动主服务
python start_main_server.py
# 启动向量数据库服务
python start_vdb_server.py
```


