import json

from kb_sdk.utilities import AsyncSpider


class KnowledgeBaseSDK(AsyncSpider):
    def __init__(self, base_url, api_key, dataset_id):
        self.dataset_id = dataset_id
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        super().__init__(base_url, headers=self.headers)

    async def get_dataset_list(self, parent_id):
        """
        parentId - 父级ID，传空字符串或者null，代表获取根目录下的知识库
        curl --location --request POST 'http://localhost:3000/api/core/dataset/list?parentId=' \
            --header 'Authorization: Bearer xxxx' \
            --header 'Content-Type: application/json' \
            --data-raw '{
                "parentId":""
            }'
        """
        payload = {
            "parentId": parent_id
        }
        response = await self.post(f"/core/dataset/list?parentId={parent_id}", _json=payload)
        print(response.json())
        return response.json()

    async def search_dataset(
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
            --data-raw '{
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
            "datasetId": self.dataset_id,
            "text": text,
            "limit": limit,
            "similarity": similarity,
            "searchMode": search_mode,
            "usingReRank": False,
            "datasetSearchUsingExtensionQuery": False,
            "datasetSearchExtensionModel": "",
            "datasetSearchExtensionBg": ""
        }
        response = await self.post("/core/dataset/searchTest", _json=payload)
        # print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        return response.json()
