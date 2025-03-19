import json
from typing import Tuple, Literal, Dict, Any

from config import config
from engine_core.utils import get_openai_client
from .prompt import router_agent_prompt


class RouterAgent:
    """
    路由代理，用于判断用户输入是指令还是查询，并路由到相应的处理方法
    """
    
    def __init__(self):
        self.client = get_openai_client()
    
    async def route(self, user_messages: list[dict[str, str]]) -> Tuple[Literal["instruction", "question"], Dict[str, Any]]:
        """
        判断用户输入类型并返回路由结果
        
        Args:
            user_messages: 用户输入的内容
            
        Returns:
            tuple: (输入类型, 附加信息)
                - 输入类型: "instruction" 表示指令, "question" 表示问题
                - 附加信息: 额外的处理信息，如预处理后的查询等
        """
        # 调用LLM判断输入类型
        response = await self.client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "system",
                    "content": router_agent_prompt()
                },
                *user_messages
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            input_type = result.get("type")
            
            if input_type not in ["instruction", "question"]:
                # 默认为问题
                input_type = "question"
            
            return input_type, {
                "explanation": result.get("explanation", ""),
            }
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            # 解析错误时的默认处理
            return "question", {"explanation": f"解析错误: {str(e)}"}