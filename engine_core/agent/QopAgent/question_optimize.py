import asyncio

from config import config
from engine_core.utils import get_openai_client, ChunkWrapper
from kb_sdk import KnowledgeBaseSDK
from .prompt import question_generate_agent_prompt


class QopProcess:
    def __init__(self, chunk_wrapper):
        self.kb = KnowledgeBaseSDK(
            base_url=config.kb_base_url,
            api_key=config.kb_api_key,
            dataset_id=config.kb_dataset_id,
        )
        self.__chunk_wrapper: ChunkWrapper = chunk_wrapper
        pass

    async def run(self, base_question):
        yield self.__chunk_wrapper.content_chunk_wrapper("<step>[开始检索相关内容]")
        yield self.__chunk_wrapper.content_chunk_wrapper("\n")
        first_content = await self.kb.search_dataset(base_question)
        first_content = [i['q'] for i in first_content["data"]["list"]]
        for i in str(first_content):
            yield self.__chunk_wrapper.content_chunk_wrapper(i)
        yield self.__chunk_wrapper.content_chunk_wrapper("</step>\n\n\n")

        print(first_content)
        yield self.__chunk_wrapper.content_chunk_wrapper("<step>[正在扩大搜索范围]")
        yield self.__chunk_wrapper.content_chunk_wrapper("\n")
        related_questions = await self.question_generate(base_question, first_content)
        yield self.__chunk_wrapper.content_chunk_wrapper(related_questions)
        question_tasks = [asyncio.create_task(self.basic_assistant(q)) for q in related_questions.split("\n") if q]
        results=asyncio.gather(*question_tasks)
        for task in results:
            result = await task
            print(result)
            related_content=await self.kb.search_dataset(result)
            print(related_content)
            yield self.__chunk_wrapper.content_chunk_wrapper(result)
        yield self.__chunk_wrapper.content_chunk_wrapper("</step>\n\n\n")

    @staticmethod
    async def question_generate(base_question, context):
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": question_generate_agent_prompt(base_question, context)
                },
                {
                    "role": "user",
                    "content": base_question
                }
            ],
            max_tokens=400,
            temperature=0.1,
        )
        return response.choices[0].message.content

    @staticmethod
    async def basic_assistant(questions):
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": f"{questions}"
                }
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content
