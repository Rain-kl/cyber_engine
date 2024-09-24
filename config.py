from pydantic_settings import BaseSettings


class Configer(BaseSettings):
    host: str
    port: int

    # 可以从配置文件加载配置
    class Config:
        env_file = ".env"


# 实例化全局配置对象
config = Configer()
