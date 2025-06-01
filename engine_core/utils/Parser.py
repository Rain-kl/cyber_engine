import json
import re
import xml.etree.ElementTree as ET
from typing import Dict

from pydantic import BaseModel


class FunctionXMLModel(BaseModel):
    function: str
    params: list
    values: list


class Parser:
    def __init__(self, content):
        self.content = content


class JsonParser(Parser):
    def parse(self) -> Dict:
        """
        从字符串中解析 JSON 对象
        """
        content_arr = list(self.content)

        result = None  # 用于存储查找到的 JSON 对象
        start_index = None  # JSON 对象的起始下标
        stack = 0  # 用于括号匹配的计数变量

        for index, char in enumerate(content_arr):
            if char == "[":
                # 如果当前字符为 [，则作为 JSON 对象的开始
                start_index = index
                stack = 1  # 初始化括号计数
                # 从下一个字符开始继续查找，直到所有的 [ 都匹配到 ]
            for j in range(index + 1, len(content_arr)):
                if content_arr[j] == "[":
                    stack += 1
                elif content_arr[j] == "]":
                    stack -= 1
                # 当 stack 恰好为 0 时，说明匹配完成
                if stack == 0:
                    end_index = j  # JSON 对象的结束下标
                    json_str = "".join(content_arr[start_index:end_index + 1])
                    try:
                        result = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        # print("JSON 解析错误:", e)
                        break
                # 找到后退出外层循环
                if result is not None:
                    break

        if result is not None:
            # print("解析到的 JSON 对象为:")
            return result
        else:
            return {"error": "未找到 JSON 对象"}


class XMlParser(Parser):
    def parse_function(self) -> FunctionXMLModel | None:
        """
        从字符串中解析XML并转换为JSON格式

        Returns:
            dict: 解析后的JSON格式数据，如果没有找到XML则返回None
        """
        # 使用正则表达式查找XML标签
        xml_pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(xml_pattern, self.content, re.DOTALL)

        if not matches:
            return None

        # 假设我们要处理的是第一个完整的XML结构
        # 先找到最外层的XML标签
        outer_xml_pattern = r'<(\w+)>.*?</\1>'
        outer_match = re.search(outer_xml_pattern, self.content, re.DOTALL)

        if not outer_match:
            return None

        xml_content = outer_match.group(0)

        try:
            # 解析XML
            root = ET.fromstring(xml_content)

            # 构建JSON结构
            result = {
                "function": root.tag,
                "params": [],
                "values": []
            }

            # 遍历子元素
            for child in root:
                result["params"].append(child.tag)
                result["values"].append(child.text if child.text else "")

            return FunctionXMLModel(**result)

        except ET.ParseError as e:
            print(f"XML解析错误: {e}")
            return None


if __name__ == '__main__':
    print(
        XMlParser("""
                内心独白：我接收到了一个详细的上下文包。用户请求是“明天有雨通知我”。[environment_info]显示当前时间是晚上8点，位置是武汉。[retrieved_ltm]的Layer 3告诉我用户需要检查天气情况，如果天气恶劣则设置通知提醒。用户意图是查询天气并根据结果设置提醒，这是一个原子性任务，可以直接使用工具完成。我将使用搜索工具查询天气。
                <tools>
                <functionName>查阅2023-10-28武汉的天气</functionName>
                </tools>
                """
                  ).parse_function())
