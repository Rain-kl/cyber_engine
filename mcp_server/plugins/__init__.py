import importlib
import os

from .ext import mcp


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
            module = importlib.import_module(f"plugins.{module_name}")
            # 将每个模块中的函数添加到插件字典中
            for attr in dir(module):
                if callable(getattr(module, attr)) and not attr.startswith("_"):
                    plugins[attr] = getattr(module, attr)
    return plugins


load_plugins()
