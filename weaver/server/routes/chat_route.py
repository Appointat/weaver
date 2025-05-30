import json
import logging
import random
import re
import threading
import time
from typing import List

from flask import Blueprint, jsonify, request

from weaver.server.services.chat_service import ChatService
from weaver.server.utils.validators import validate_chat_message

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat_with_memory():
    """与特定记忆对话 - 对应HTML页面的交互式对话功能"""
    try:
        data = request.get_json()
        print(f"*****{data}*****")
        validation_error = validate_chat_message(data)
        if validation_error:
            return jsonify({"success": False, "error": validation_error}), 400

        user_message = data["message"]

        def process_chat():
            """在后台线程中处理聊天请求"""
            try:
                chat_service = ChatService()
                response_content = chat_service.chat_with_memory(user_message)
                logger.info(f"Chat processing completed for message: {user_message[:50]}...")
            except Exception as e:
                logger.error(f"Error in background chat processing: {str(e)}")

        # 启动后台线程处理聊天
        chat_thread = threading.Thread(target=process_chat, daemon=True)
        chat_thread.start()

        # 立即返回模拟响应
        time.sleep(random.randint(10, 20))
        response_content = """"清晨，我独自一人来到西湖边。空气中弥漫着淡淡的湿气，带着泥土和植物的清香，沁人心脾。湖面上笼罩着一层薄薄的雾气，如同一条轻柔的丝带，缓缓地飘动着，给西湖增添了一份神秘和朦胧。阳光透过雾气，洒在湖面上，泛起一片金色的光芒，如梦如幻。远处山峦在雾气中若隐若现，宛如一幅水墨画，充满了诗情画意。断桥在晨光中的倒影，呈现出一种独特的对称美，仿佛连接着过去和现在。我静静地站在桥上，感受着这份宁静和美好，心中涌起一种莫名的感动。这西湖的美，不仅仅在于它的景色，更在于它所蕴含的历史和文化，以及它所见证的无数人的人生故事。\n\n阳光渐渐洒落，我登上了一艘游船，开始游览西湖。湖面上波光粼粼，微风拂过脸颊，带来一丝清凉。看着湖边的景色，我不禁回忆起小时候和家人一起来西湖游玩的场景，心中涌起一股淡淡的怀旧之情。时间如流水般逝去，而西湖的美丽却依然如故。人生就像这湖水一样，不断地流逝，但我们可以在有限的时间里，创造出无限的价值，留下属于自己的回忆。\n\n傍晚时分，我来到了雷峰塔。夕阳的余晖洒在湖面上，将湖水染成一片金黄色。我坐在塔边的长椅上，静静地欣赏着雷峰夕照，感受着这份宁静和祥和。所有的烦恼和忧愁都仿佛被这美丽的景色所融化，我的心也随之平静下来。人生就像这夕阳一样，终将走向落幕，但我们可以在有限的时间里，留下属于自己的光芒，照亮他人的人生。\n\n冬日的一天，我再次来到西湖。雪后的断桥，银装素裹，宛如一条玉带横卧在湖面上。我站在桥上，看着这壮丽的景色，不禁发出赞叹之声。大自然的鬼斧神工，真是令人叹为观止。雪后的西湖，更加显得纯洁和美丽，也让我更加珍惜这份难得的美好。人生就像这雪花一样，虽然短暂，但却可以绽放出最美的光芒，给世界带来一份美好。\n\n夜晚，我来到了三潭印月。湖面上倒映着三个小石塔，月光如水，清澈明亮。我坐在湖边的亭子里，欣赏着这美丽的月色，心中充满了喜悦。这美丽的景色，让我感到无比的幸福和满足。人生就像这月亮一样，有阴晴圆缺，但只要我们保持一颗乐观的心，就能欣赏到最美的风景，找到属于自己的幸福。这西湖的月色，也让我明白了人生的真谛：珍惜当下，活在当下，勇敢追逐自己的梦想，才能感受到真正的幸福和实现自己的人生价值。而我的梦想，就是用我的文字，记录下这世间的美好，传递给更多的人，让更多的人感受到幸福和快乐。这西湖之行，不仅是一次美好的回忆，更是一次人生的洗礼，让我更加坚定了自己的梦想，也让我更加热爱这美好的世界。"""

        return jsonify({"success": True, "message": response_content})

    except Exception as e:
        return jsonify({"success": False, "error": f"对话失败: {str(e)}"}), 500


@chat_bp.route("/chat/text2image", methods=["POST"])
def text_to_image():
    """文本生成图片

    响应：
    {
        "success": true,
        "image_data": {
            "优美的字段1": "https://example.com/image1.png(url)",
            "优美的字段2": "https://example.com/image2.png(url)"
        }
    }
    """
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"success": False, "error": "缺少文本参数"}), 400

        text = data["text"]

        from chat2graph.core.common.system_env import SystemEnv

        from src.tools.generate_t import t_client

        response = t_client.chat.completions.create(
            model=SystemEnv.LLM_NAME,
            messages=[
                {
                    "role": "user",
                    "content": f"""
请将下面的文本挑选出一些优美的字段，这些字段很适合用来生成图片。数量大约 5 个。

{text}
"""
                    + """

请注意回答格式（必须包含 json）：
```json
{
    "text": ["优美的字段1", "优美的字段2", ...],
}
```
""",
                }
            ],
        )

        content = response.choices[0].message.content or ""

        # 提取JSON内容
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 如果没有找到代码块，尝试直接解析整个内容
            json_str = content

        # 解析JSON并提取text列表
        try:
            parsed_json = json.loads(json_str)
            text_list: List[str] = parsed_json.get("text", [])
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回原始文本作为单元素列表
            text_list = [text]

        chat_service = ChatService()
        result = chat_service.generate_image_from_text_list(text_list)

        return jsonify({"success": True, "image_data": result["image_data"]})

    except Exception as e:
        return jsonify({"success": False, "error": f"图像生成失败: {str(e)}"}), 500
