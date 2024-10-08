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

    max_chat_message_length: int

    email_auth_code: str
    email_sender: str

    # 可以从配置文件加载配置
    class Config:
        env_file = ".env"


# 实例化全局配置对象
config = Configer()
