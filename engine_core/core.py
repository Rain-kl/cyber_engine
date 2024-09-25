from openai import OpenAI, AsyncOpenAI
import os
from config import config


async def ponder(message: str):
    client = AsyncOpenAI(
        base_url=config.llm_base_url,
        api_key=config.llm_api_key,
    )
    chat_completion = await client.chat.completions.create(
        model=config.llm_model,
        temperature=0.4,
        # response_format={"type": "json_object"},
        messages=[
            {
                'role': 'user',
                'content': message,
            }
        ],
    )
    return chat_completion.choices[0].message.content
