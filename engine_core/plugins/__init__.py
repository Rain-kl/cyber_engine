import importlib
import os

from .send_email import email_tools
from .set_schedule import schedule_tools


def load_plugins() -> dict[str, callable]:
    """
    加载插件, 返回插件字典
    :return:
    """
    plugins_folder = os.path.join(os.path.dirname(__file__), "")
    plugins = {}
    for filename in os.listdir(plugins_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"engine_core.plugins.{module_name}")
            # 将每个模块中的函数添加到插件字典中
            for attr in dir(module):
                if callable(getattr(module, attr)) and not attr.startswith("_"):
                    plugins[attr] = getattr(module, attr)
    return plugins


def load_plugin(function_name):
    """
    加载指定函数
    :param function_name:
    :return:
    """
    return load_plugins()[function_name]


tools = [
    email_tools,
    schedule_tools
]
