import pytest

from engine_core.plugins.send_email import send_email


class TestPlugin:
    """测试插件"""

    @pytest.mark.asyncio
    async def test_send_email(self):
        a = await send_email('你好', '希望你很好\n--测试邮件', 'xxxxxxxx@qq.com')
        print(a)
