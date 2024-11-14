import json
from typing import Dict
from loguru import logger
from openai import AsyncOpenAI

from model import InputModel, OpenaiChatMessageModel
from vector_db.sdk_vdb import Mnemonic


async def ltm_build_msg(input_model: InputModel) -> OpenaiChatMessageModel:
    logger.debug("start build_message_LTM")

    mn = Mnemonic()
    related_history = await mn.search(input_model.msg, user_id=input_model.user_id)
    assert related_history.status == 200, "Failed to get related history"
    related_data = []
    for i in related_history.data:
        if float(i.distance) < 0.8:
            related_data.append(i.text)
    print(f"""
            相关历史:{related_data}\n
            """)
    return OpenaiChatMessageModel(
        role="system",
        content=f"""
            这是与上一条消息相关的参考信息，如果与实际消息无任何关系，请忽略\n
            相关历史:{related_data}\n
            """
    )


async def intention_recognition(client: AsyncOpenAI, model, msg: str) -> Dict:
    """
    useless, question, command, other
    :param model: model name
    :param client: AsyncOpenAI
    :param msg: user message
    :return: {"type": "useless"}
    """
    prompt = """
        You are a problem classifier, and you need to determine which category the user's input belongs to
        Current classification: \n
            useless: meaningless information, such as greetings or related to greeting\n
            question: Help users solve problems\n
            command: What does the user need you to do, such as providing scheduled reminders\n
            other \n
        Return the judgment result in JSON format as follows:\n
            {
            type: 'useless'
            }
    """
    type_data = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        temperature=0.3,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    return json.loads(type_data.choices[0].message.content)
