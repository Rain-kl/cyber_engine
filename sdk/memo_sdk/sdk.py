from .model import ChatSummary
from .utilities import AsyncSpider


class MemoryBaseSDK(AsyncSpider):
    def __init__(self, base_url, api_key, dataset_id):
        self.dataset_id = dataset_id
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        super().__init__(base_url, headers=self.headers)

    async def search_memories(
            self,
            text,
            limit="5000",
            similarity="0.3",
            search_mode="mixedRecall",
    ):
        """
        datasetId - 知识库ID
        text - 需要测试的文本
        limit - 最大 tokens 数量
        similarity - 最低相关度（0~1，可选）
        searchMode - 搜索模式：embedding | fullTextRecall | mixedRecall

        usingReRank - 使用重排
        datasetSearchUsingExtensionQuery - 使用问题优化
        datasetSearchExtensionModel - 问题优化模型
        datasetSearchExtensionBg - 问题优化背景描述

        curl --location --request POST 'https://api.fastgpt.in/api/core/dataset/searchTest' \
            --header 'Authorization: Bearer fastgpt-xxxxx' \
            --header 'Content-Type: application/json' \
            --data-raw '{https://img.shields.io/github/license/balancemymoney/balance-open.svg?style=flat-square
                "datasetId": "知识库的ID",
                "text": "导演是谁",
                "limit": 5000,
                "similarity": 0,
                "searchMode": "embedding",
                "usingReRank": false,

                "datasetSearchUsingExtensionQuery": true,
                "datasetSearchExtensionModel": "gpt-4o-mini",
                "datasetSearchExtensionBg": ""
            }'
        """
        payload = {
            "text": text,
            "limit": limit,
            "similarity": similarity,
            "searchMode": search_mode,
        }
        response = await self.post("/memory/searchMemories", _json=payload)
        # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        return response.json()

    async def get_memory_list(self, from_date, to_date, limit=1000):
        """
        from_date - 起始日期
        to_date - 结束日期
        limit - 返回的最大数量

        curl --location --request POST 'https://api.fastgpt.in/api/core/memory/list' \
            --header 'Authorization: Bearer fastgpt-xxxxx' \
            --header 'Content-Type: application/json' \
            --data-raw '{
                "fromDate": "2023-09-01",
                "toDate": "2023-09-30",
                "limit": 1000
            }'
        """
        payload = {
            "fromDate": from_date,
            "toDate": to_date,
            "limit": limit
        }
        response = await self.post("/memory/list", _json=payload)
        # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        return response.json()

    async def upload_memory(self, summary_obj: ChatSummary):
        """
        上传记忆
        :param summary_obj: ChatSummary对象
        :return: response
        """
        payload = {
            "timestamp": summary_obj["timestamp"],
            "summary": summary_obj["summary"],
        }

        response = await self.post("/memory/upload", _json=payload)
        # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        return response.json()
