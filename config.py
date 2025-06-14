from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Configer(BaseSettings):
    virtual_model: str = "ena-test"
    host: str = "127.0.0.1"
    port: int = 6898
    llm_enable_proxy: bool = False
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str
    llm_model: str = "gpt-4o"
    llm_simple_model: str = "gpt-4o-mini"
    llm_agent_model: str = "gpt-4o"
    llm_temperature: float = 0.5

    max_chat_message_length: int = 10

    embedding_method: Literal["openai", "ollama", "sentence_transformers"]
    embedding_model: str
    embedding_base_url: Optional[str] = None
    embedding_api_key: Optional[str] = None

    kb_base_url: str
    kb_api_key: str
    kb_dataset_id: str

    # MCP 连接配置
    mcp_basic_tools_transport: str = "sse"
    mcp_basic_tools_url: str = "http://localhost:3001/sse"

    # 可以从配置文件加载配置
    class Config:
        env_file = ".env"


# 实例化全局配置对象
config = Configer()
