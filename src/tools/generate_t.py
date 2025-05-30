#!/usr/bin/python
#****************************************************************#
# ScriptName: generate_t.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2025-05-25 00:19
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2025-05-25 00:19
# Function: Text generation using OpenAI API
#***************************************************************#

from chat2graph.core.common.system_env import SystemEnv
from openai import OpenAI

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
t_client = OpenAI(
    base_url=SystemEnv.LLM_ENDPOINT,
    api_key=SystemEnv.LLM_APIKEY,
)

response = t_client.chat.completions.create(
    model=SystemEnv.LLM_NAME,
    messages=[{"role": "user", "content": "请写一首关于春天的诗"}],
)

print(response.choices[0].message.content)
