import asyncio
from loguru import logger
from config import config
from engine_core.utils import get_openai_client, ChunkWrapper
from kb_sdk import KnowledgeBaseSDK
from .prompt import question_generate_agent_prompt, answer_question_prompt


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
        # 步骤1: 第一个agent直接回答问题(可能产生幻觉)
        yield self.__chunk_wrapper.content_chunk_wrapper("<step>[初始回答生成]")
        yield self.__chunk_wrapper.content_chunk_wrapper("\n")
        
        initial_answer = await self.generate_initial_answer(base_question)
        yield self.__chunk_wrapper.content_chunk_wrapper(f"初始回答: {initial_answer}\n")
        yield self.__chunk_wrapper.content_chunk_wrapper("</step>\n\n\n")


        # 步骤2: 将回答结果进行知识库检索
        yield self.__chunk_wrapper.content_chunk_wrapper("<step>[知识库检索]")
        yield self.__chunk_wrapper.content_chunk_wrapper("\n")
        
        kb_results = await self.kb.search_dataset(initial_answer)
        relevant_texts = [item["q"] for item in kb_results["data"]["list"]]
        
        yield self.__chunk_wrapper.content_chunk_wrapper("检索到的相关内容:\n")
        for i, text in enumerate(relevant_texts, 1):
            # 只显示内容前100个字符，防止输出过长
            yield self.__chunk_wrapper.content_chunk_wrapper(f"{i}. {text[:100]}...\n")

        yield self.__chunk_wrapper.content_chunk_wrapper("</step>\n\n\n")

        # 步骤3: 交付第二个agent验证和回答
        yield self.__chunk_wrapper.content_chunk_wrapper("<step>[知识库验证回答]")
        yield self.__chunk_wrapper.content_chunk_wrapper("\n")

        # 初始化迭代计数
        iteration_count = 0
        max_iterations = 2
        final_answer = ""

        while iteration_count < max_iterations:
            # 让agent解答并判断知识库内容是否足够
            answer, is_sufficient, missing_info = await self.answer_with_evaluation(
                base_question, relevant_texts
            )
            
            # 增加迭代计数
            iteration_count += 1
            
            if is_sufficient:
                # 如果知识库内容足够，使用当前答案作为最终答案
                yield self.__chunk_wrapper.content_chunk_wrapper(f"迭代{iteration_count}结果: 知识库内容足够回答问题\n")
                final_answer = answer
                break
            else:
                yield self.__chunk_wrapper.content_chunk_wrapper(f"迭代{iteration_count}结果: 知识库内容不足\n")
                yield self.__chunk_wrapper.content_chunk_wrapper(f"缺失信息: {missing_info}\n\n")
                
                # 如果达到最大迭代次数，使用当前答案作为最终答案
                if iteration_count >= max_iterations:
                    yield self.__chunk_wrapper.content_chunk_wrapper("达到最大迭代次数，将基于现有资料总结回答\n")
                    # 获取所有已有的知识库结果进行总结
                    final_answer = await self.summarize_with_limited_info(base_question, relevant_texts)
                    break
                
                # 否则，使用缺失信息再次查询知识库
                yield self.__chunk_wrapper.content_chunk_wrapper(f"使用缺失信息重新检索知识库...\n")
                new_kb_results = await self.kb.search_dataset(missing_info)
                new_relevant_texts = [item["q"] for item in new_kb_results["data"]["list"]]
                
                # 合并所有相关文本，避免丢失之前的上下文
                relevant_texts.extend(new_relevant_texts)
                # 去重
                relevant_texts = list(set(relevant_texts))
                # 限制最多10条文本
                # relevant_texts = relevant_texts[:10]
        
        # 输出最终答案
        yield self.__chunk_wrapper.content_chunk_wrapper("\n最终答案:\n")
        yield self.__chunk_wrapper.content_chunk_wrapper(final_answer)
        yield self.__chunk_wrapper.content_chunk_wrapper("\n</step>\n\n\n")

    async def generate_initial_answer(self, question):
        """第一个agent直接回答问题(可能产生幻觉)"""
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    你是一个智能助手，请直接回答用户的问题。不需要说明你不确定或没有足够信息，
                    就像你非常确定答案一样直接回答，尽可能提供详细信息。
                    
                    用户问题: {question}
                    
                    请直接回答，不要包含"我认为"、"根据我所知"等表示不确定的词语。
                    """
                }
            ],
            max_tokens=800,
            temperature=0.7,  # 使用较高的温度让回答更加多样化
        )
        
        return response.choices[0].message.content

    async def answer_with_evaluation(self, question, context):
        """让agent解答并评估知识库内容是否足够"""
        client = get_openai_client()
        
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    你将获得一个问题和相关的知识库内容。请根据知识库内容回答问题。
                    
                    问题: {question}
                    
                    知识库内容:
                    {context}
                    
                    在回答问题后，请评估知识库内容是否足够回答问题。
                    如果知识库内容不足，请明确指出缺少哪些具体信息。
                    
                    回答格式:
                    <answer>你的回答</answer>
                    <evaluation>知识库内容是否足够(足够/不足)</evaluation>
                    <missing_info>如果不足，说明缺少什么具体信息</missing_info>
                    """
                }
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        
        content = response.choices[0].message.content
        
        # 解析回答、评估和缺失信息
        answer = ""
        evaluation = "不足"  # 默认为不足
        missing_info = ""
        
        if "<answer>" in content and "</answer>" in content:
            answer = content.split("<answer>")[1].split("</answer>")[0].strip()
        else:
            answer = content  # 如果没有按格式回答，就使用全部内容
        
        if "<evaluation>" in content and "</evaluation>" in content:
            evaluation = content.split("<evaluation>")[1].split("</evaluation>")[0].strip()
        
        if "<missing_info>" in content and "</missing_info>" in content:
            missing_info = content.split("<missing_info>")[1].split("</missing_info>")[0].strip()
        
        is_sufficient = "足够" in evaluation
        
        return answer, is_sufficient, missing_info

    async def summarize_with_limited_info(self, question, context):
        """当达到最大迭代次数后，基于有限信息总结回答"""
        client = get_openai_client()
        
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    你将获得一个问题和相关的知识库内容。虽然知识库内容可能不足以完整回答问题，
                    但请尽力基于提供的信息回答问题，同时明确指出哪些部分是基于知识库的，哪些部分是你的推测。
                    
                    问题: {question}
                    
                    知识库内容:
                    {context}
                    
                    请尽力回答问题，明确区分事实和推测，并总结出最佳答案。
                    """
                }
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        
        return response.choices[0].message.content

    # 保留原有方法以便向后兼容
    @staticmethod
    async def question_generate(base_question, context):
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": question_generate_agent_prompt(base_question, context)
                }
            ],
            max_tokens=400,
            temperature=0.1,
        )
        return response.choices[0].message.content

    @staticmethod
    async def answer_question_base(questions):
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": """
                        你是一个助理用于回答用户提出的问题
                        用户可能会提出多个问题，你需要在每回答一个问题后添加一个结束标记<end>
                        每一个问题的回答都需要以<end>结束
                        用户提出的多个问题之间可能存在关联，你需要在回答用户用户同时对你回答的关键词进行解释，但注意总字数不要超过 600字
                        示例
                            用户: 糖尿病能喝可乐吗？
                            你： 糖尿病患者不宜喝可乐，可乐主要成分有碳酸水、高果糖糖浆、蔗糖、焦糖、磷酸以及香料，其中高果糖糖浆是糖尿病患者的禁忌食物，因为高果糖糖浆会导致血糖升高，加重糖尿病病情。所以糖尿病患者不宜喝可乐。<end>
                    """
                },
                {
                    "role": "user",
                    "content": f"{questions}"
                }
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content

    @staticmethod
    async def answer_question_clue(question, context):
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": answer_question_prompt(question, context)
                }
            ],
            max_tokens=400,
            temperature=0.1,
        )
        return response.choices[0].message.content
