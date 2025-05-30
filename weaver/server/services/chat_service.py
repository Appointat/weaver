from typing import Any, Dict, List
from uuid import uuid4

from chat2graph.core.model.message import HybridMessage, TextMessage
from chat2graph.core.sdk.agentic_service import AgenticService
from chat2graph.core.sdk.wrapper.job_wrapper import JobWrapper

from weaver.server.services.memory_service import MemoryService
from weaver.weave_memory import meave_memory


class ChatService:
    """对话服务 - 对应HTML页面的各种对话功能"""

    def __init__(self):
        self.mas = AgenticService.load("weaver.yml")
        self.job_dict: Dict[str, JobWrapper] = {}
        self.memory_service = MemoryService()

    def chat_with_memory(self, user_message: str) -> str:
        """提交一次对话"""
        job = meave_memory(user_message)
        service_message = job.wait()
        if isinstance(service_message, TextMessage):
            return service_message.get_payload()
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            return text_message.get_payload()

    def generate_image_from_text_list(self, text_list: List[str]) -> Dict[str, Any]:
        """文本生成图片"""
        result: Dict[str, Any] = {}
        for text in text_list:
            prompt = f"""
            请根据以下文本生成一张旅游风光的图片：

            {text}
            """

            from src.tools.generate_t2i import t2i_client

            image_response = t2i_client.images.generate(
                model="doubao-seedream-3-0-t2i-250415",
                prompt=prompt,
            )
            image_url = image_response.data[0].url
            result[text] = image_url

        return {
            "image_data": result,  # text: image_url
            "format": "url",
        }

    def _generate_ai_narrative_for_stream(self, data: Dict[str, Any]) -> str:
        """为流式输出生成AI叙述"""
        session_id = str(uuid4())

        prompt = f"""
        请为这次旅行生成一段详细的回忆叙述：
        旅程名称：{data.get("tripName", "")}
        地点：{data.get("location", "")}
        我的笔记：{data.get("notes", "")}
        背景音乐：{data.get("music", "")}

        请分成4-5个段落，用富有情感的语言描述，包含关键词如"景色"、"经历"、"感悟"等。
        """

        ai_message = TextMessage(
            payload=prompt,
            assigned_expert_name="Memory Integration And Graph Expert",
            session_id=session_id,
        )

        hybrid_message = HybridMessage(
            instruction_message=ai_message,
            attached_messages=[],
        )

        job = self.mas.session().submit(hybrid_message)
        service_message = job.wait()

        if isinstance(service_message, TextMessage):
            return service_message.get_payload()
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            return text_message.get_payload()

        return "无法生成叙述内容"
