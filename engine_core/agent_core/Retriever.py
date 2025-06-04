from config import config
from engine_core.agent_core.AgentBase import AgentBase
from sdk.kb_sdk import KnowledgeBaseSDK


class Retriever(AgentBase):

    def __init__(self):
        self.kb = KnowledgeBaseSDK(
            base_url=config.kb_base_url,
            api_key=config.kb_api_key,
            dataset_id=config.kb_dataset_id,
        )
        pass

    def _prompt(self, **kwargs):
        pass

    async def run(self, base_question):
        try:
            # 步骤1: 第一个agent直接回答问题(可能产生幻觉)
            yield "[初始回答生成]\n"
            initial_answer = ""
            try:
                async for word in self.generate_initial_answer(base_question):
                    initial_answer += word
                    yield word
            except Exception as e:
                print(f"初始回答生成错误: {e}")
                import traceback

                traceback.print_exc()
                yield f"\n[错误: {str(e)}]\n"

            # 步骤2: 将回答结果进行知识库检索
            yield "\n[知识库检索]\n"

            try:
                kb_results = await self.kb.search_dataset(initial_answer)
                relevant_texts = [item["q"] for item in kb_results["data"]["list"]]

                for i, text in enumerate(relevant_texts, 1):
                    # 只显示内容前100个字符，防止输出过长
                    yield f"\n{i}. {text[:100]}...\n"
            except Exception as e:
                print(f"知识库检索错误: {e}")
                import traceback

                traceback.print_exc()
                yield f"\n[错误: {str(e)}]\n"
                relevant_texts = []

            # 步骤3: 交付第二个agent验证和回答
            yield "\n[知识库验证回答]\n"

            # 初始化迭代计数
            iteration_count = 0
            max_iterations = 2
            final_answer = ""

            while iteration_count < max_iterations:
                # 让agent解答并判断知识库内容是否足够
                yield f"迭代{iteration_count + 1}中...\n"
                awe_content = ""
                try:
                    async for i in self.answer_with_evaluation(
                        base_question, relevant_texts
                    ):
                        awe_content += i
                        yield i
                    yield "\n\n"

                except Exception as e:
                    print(f"回答评估错误: {e}")
                    import traceback

                    traceback.print_exc()
                    yield f"\n[错误: {str(e)}]\n"
                    awe_content = f"发生错误: {str(e)}"

                try:
                    # 解析回答、评估和缺失信息
                    is_sufficient = False
                    missing_info = ""

                    if "<answer>" in awe_content and "</answer>" in awe_content:
                        answer = (
                            awe_content.split("<answer>")[1]
                            .split("</answer>")[0]
                            .strip()
                        )
                    else:
                        answer = awe_content  # 如果没有按格式回答，就使用全部内容

                    if "<evaluation>" in awe_content and "</evaluation>" in awe_content:
                        evaluation = (
                            awe_content.split("<evaluation>")[1]
                            .split("</evaluation>")[0]
                            .strip()
                        )
                        if (
                            evaluation.lower() == "y"
                            or evaluation.lower() == "yes"
                            or evaluation.lower() == "足够"
                        ):
                            is_sufficient = True
                    if (
                        "<missing_info>" in awe_content
                        and "</missing_info>" in awe_content
                    ):
                        missing_info = (
                            awe_content.split("<missing_info>")[1]
                            .split("</missing_info>")[0]
                            .strip()
                        )

                except Exception as e:
                    print(f"解析回答错误: {e}")
                    import traceback

                    traceback.print_exc()
                    yield f"\n[解析回答错误: {str(e)}]\n"
                    answer = awe_content
                    is_sufficient = False
                    missing_info = "无法解析回答内容"

                # 增加迭代计数
                iteration_count += 1

                if is_sufficient:
                    # 如果知识库内容足够，使用当前答案作为最终答案
                    yield f"迭代{iteration_count}结果: 知识库内容足够回答问题\n"
                    final_answer = answer
                    break
                else:
                    yield f"迭代{iteration_count}结果: 知识库内容不足\n"
                    yield f"缺失信息: {missing_info}\n\n"

                    # 如果达到最大迭代次数，使用当前答案作为最终答案
                    if iteration_count == max_iterations:
                        yield "达到最大迭代次数，将基于现有资料总结回答\n"
                        # 获取所有已有的知识库结果进行总结
                        yield "生成最终答案中...\n"

                        # 流式输出最终答案
                        try:
                            async for chunk in self.summarize_with_limited_info(
                                base_question, relevant_texts
                            ):
                                final_answer += chunk
                                yield chunk
                        except Exception as e:
                            print(f"总结答案错误: {e}")
                            import traceback

                            traceback.print_exc()
                            yield f"\n[错误: {str(e)}]\n"
                            final_answer = f"生成最终答案时发生错误: {str(e)}"
                        break

                    # 否则，使用缺失信息再次查询知识库
                    yield f"使用缺失信息重新检索知识库...\n"
                    try:
                        new_kb_results = await self.kb.search_dataset(
                            f"{base_question} {missing_info}"
                        )
                        new_relevant_texts = [
                            item["q"] for item in new_kb_results["data"]["list"]
                        ]

                        # 合并所有相关文本，避免丢失之前的上下文
                        relevant_texts.extend(new_relevant_texts)
                        # 去重
                        relevant_texts = list(set(relevant_texts))
                        # 限制最多10条文本
                        # relevant_texts = relevant_texts[:10]
                    except Exception as e:
                        print(f"重新检索知识库错误: {e}")
                        import traceback

                        traceback.print_exc()
                        yield f"\n[重新检索错误: {str(e)}]\n"

            # 输出最终答案(如果不是通过流式方式生成的)
            yield "\n<final_answer>\n"
            yield f"{final_answer}"
            yield "\n</final_answer>\n"

        except Exception as e:
            print(f"整体执行错误: {e}")
            import traceback

            traceback.print_exc()
            yield f"\n[严重错误: {str(e)}]\n"

    async def generate_initial_answer(self, question):
        """第一个agent直接回答问题(可能产生幻觉)"""
        client = self.openai_client()
        try:
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
                        """,
                    }
                ],
                max_tokens=800,
                temperature=0.7,  # 使用较高的温度让回答更加多样化
                stream=True,
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"generate_initial_answer 错误: {e}")
            import traceback

            traceback.print_exc()
            yield f"[生成回答发生错误: {str(e)}]"

    async def answer_with_evaluation(self, question, context):
        """让agent解答并评估知识库内容是否足够"""
        client = self.openai_client()
        try:
            response = await client.chat.completions.create(
                model=config.llm_agent_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                            You will be given a question and related knowledge base content. Please answer the question based on the knowledge base content.
                            Question: {question}
                            Knowledge base content:
                            {context}
                            After answering the question, please evaluate whether the knowledge base content is sufficient to answer the question.
                            When answering the question, clearly indicate which parts are based on the knowledge base and which parts are your speculation. For parts based on the knowledge base, please cite the original information.
                            If the knowledge base content is insufficient, please clearly specify what specific information is missing.
                            Answer in the user's language.
                            Answer format:
                            <answer>Your answer</answer>
                            <evaluation>Whether the knowledge base content is sufficient (y/n)</evaluation>
                            <missing_info>If insufficient, explain what specific information is missing, expressing the missing information in the form of questions</missing_info>
                        """,
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
                stream=True,
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"answer_with_evaluation 错误: {e}")
            import traceback

            traceback.print_exc()
            yield f"[评估回答发生错误: {str(e)}]"

    async def summarize_with_limited_info(self, question, context):
        """当达到最大迭代次数后，基于有限信息总结回答"""
        client = self.openai_client()
        try:
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
                            """,
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
                stream=True,
            )

            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"summarize_with_limited_info 错误: {e}")
            import traceback

            traceback.print_exc()
            yield f"[总结答案发生错误: {str(e)}]"
