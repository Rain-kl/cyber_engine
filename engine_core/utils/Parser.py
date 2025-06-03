import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, Literal

from pydantic import BaseModel


class FunctionXMLModel(BaseModel):
    type: Literal["use_tool", "call_expert"]
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
        从字符串中解析指定标签内的XML并转换为JSON格式

        Returns:
            FunctionXMLModel: 解析后的数据模型，如果没有找到指定标签则返回None
        """
        # 使用正则表达式查找指定标签及其内容
        target_tag = "use_tool"
        target_pattern = fr'<{target_tag}>(.*?)</{target_tag}>'
        target_match = re.search(target_pattern, self.content, re.DOTALL)

        if not target_match:
            return None

        # 获取目标标签内的内容
        target_content = target_match.group(1).strip()

        # 查找标签内部的第一个完整XML标签
        inner_xml_pattern = r'<(\w+)>.*?</\1>'
        inner_match = re.search(inner_xml_pattern, target_content, re.DOTALL)

        if not inner_match:
            return None

        xml_content = inner_match.group(0)

        try:
            # 解析XML
            root = ET.fromstring(xml_content)

            # 构建JSON结构
            result = {
                "type": target_tag,
                "function": root.tag,
                "params": [],
                "values": []
            }

            # 遍历子元素
            for child in root:
                result["params"].append(child.tag)
                # 处理文本内容，去除首尾空白
                text_value = child.text.strip() if child.text else ""
                result["values"].append(text_value)

            return FunctionXMLModel(**result)

        except ET.ParseError as e:
            print(f"XML解析错误: {e}")
            return None

    def parse_call_expert(self) -> FunctionXMLModel | None:
        """
        从字符串中解析指定标签内的XML并转换为JSON格式

        Returns:
            FunctionXMLModel: 解析后的数据模型，如果没有找到指定标签则返回None
        """
        target_tag = "call_expert"
        target_pattern = fr'<{target_tag}>(.*?)</{target_tag}>'
        target_match = re.search(target_pattern, self.content, re.DOTALL)

        if not target_match:
            return None

        xml_content = target_match.group(0)

        try:
            # 解析XML
            root = ET.fromstring(xml_content)

            # 构建JSON结构
            result = {
                "type": target_tag,
                "function": root.tag,
                "params": [],
                "values": []
            }

            # 遍历子元素
            for child in root:
                result["params"].append(child.tag)
                # 处理文本内容，去除首尾空白
                text_value = child.text.strip() if child.text else ""
                result["values"].append(text_value)

            return FunctionXMLModel(**result)

        except ET.ParseError as e:
            print(f"XML解析错误: {e}")
            return None


if __name__ == '__main__':
    print(
        XMlParser("""
   <use_tool>
<set_reminder>
<time>2023-10-28 15:00</time>
<message>您下午5点在汉口站有火车，请提前准备</message>
</set_reminder>
</use_tool>
                """
                  ).parse_function())
