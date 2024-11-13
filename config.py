from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Configer(BaseSettings):
    host: str
    port: int
    llm_enable_proxy: bool
    proxy_host: str
    proxy_port: int
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_simple_model: str
    llm_temperature: float

    max_chat_message_length: int

    embedding_method: Literal["openai", "ollama", "sentence_transformers"]
    embedding_model: str
    embedding_base_url: Optional[str] = None
    embedding_api_key: Optional[str] = None


    email_auth_code: str
    email_smtp_host: str
    email_sender: str

    # 可以从配置文件加载配置
    class Config:
        env_file = ".env"


# 实例化全局配置对象
config = Configer()
