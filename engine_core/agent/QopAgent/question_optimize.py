from config import config
from engine_core.utils import get_openai_client
from prompt import question_generate_agent_prompt

async def question_generate(base_question):
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=config.llm_agent_model,
        messages=[
            {
                "role": "user",
                "content": question_generate_agent_prompt()
            },
            {
                "role": "user",
                "content": base_question
            }
        ],
        max_tokens=200,
        temperature=0.1,
    )
    print(response.choices[0].message['content'])


