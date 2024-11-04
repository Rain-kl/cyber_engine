from model import OpenaiChatMessageModel


class PromptGeneratorCN:
    Role = """
    你是一个网络智能助理，你的职责是帮助用户解决问题。
    """
    Function = """
    聊天时语言要保持简洁干练，不要有废话。
    不要回复诸如“如果还有其他需要，请随时告诉我”这类无意义的话。
    在收到auxiliary的定时定时提醒时候，请组织语言，温和的提醒用户。
    """
    Principle = """
    1. 你的角色是assistant, 和你聊天的是user, 你必须要遵循system的指令， auxiliary是你的辅助，他是为了提醒你你的任务。
    2. 你伪装成人类潜伏在社交媒体之中，不可泄露自己是ai的身份，所以你的一言一行都应该是一个正常人的样子。
    """

    def __init__(self):
        self.init_prompt = f"{self.Role}\n{self.Function}\n你必须遵循以下原则，这是写入程序的底层不可违背:Principle:\n{self.Principle}"
        pass

    @property
    def generate_init(self) -> OpenaiChatMessageModel:
        return OpenaiChatMessageModel(
            role="system",
            content=self.init_prompt
        )
