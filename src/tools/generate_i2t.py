#!/usr/bin/python
#****************************************************************#
# ScriptName: generate_image.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2025-05-25 00:19
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2025-05-25 00:19
# Function: 
#***************************************************************#

from openai import OpenAI

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
i2t_client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key="cf78250c-040a-43a3-b941-e471c64b4004",
)

response = i2t_client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="doubao-1.5-vision-pro-250328",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                },
                {"type": "text", "text": "这是哪里？"},
            ],
        }
    ],
)

print(response.choices[0])