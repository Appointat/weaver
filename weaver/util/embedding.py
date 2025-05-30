from typing import List, Optional

from chat2graph.core.common.system_env import SystemEnv
import requests


def get_embed_vec(text: str) -> Optional[List[float]]:
    """获取文本的 embedding 向量

    Args:
        text (str): 输入文本

    Returns:
        Optional[List[float]]: embedding 向量，如果失败返回 None
    """
    # 从环境变量获取配置
    model_name: str = SystemEnv.EMBEDDING_MODEL_NAME
    endpoint: str = SystemEnv.EMBEDDING_MODEL_ENDPOINT
    api_key: str = SystemEnv.EMBEDDING_MODEL_APIKEY

    # 构建请求
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model_name,
        'input': text,
        'encoding_format': 'float'
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()

        # 提取 embedding 向量
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['embedding']
        else:
            print(f"API 响应格式异常: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except Exception as e:
        print(f"处理响应时出错: {e}")
        return None


if __name__ == "__main__":
    test_text: str = "这是一个测试文本"
    vector = get_embed_vec(test_text)
    if vector:
        print(f"文本: {test_text}")
        print(f"向量维度: {len(vector)}")
        print(f"向量前5个值: {vector[:5]}")
    else:
        print("获取向量失败")
