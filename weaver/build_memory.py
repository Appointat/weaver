from typing import List
from uuid import uuid4

from chat2graph.core.model.message import FileMessage, HybridMessage, TextMessage
from chat2graph.core.sdk.agentic_service import AgenticService
from chat2graph.core.sdk.wrapper.job_wrapper import JobWrapper

from weaver.util.data_loader_v1 import load_data_v1
from weaver.util.init_chat2graph import init_chat2graph
from weaver.util.schema import import_graph_schema


def main():
    """Main function for batch processing travel data."""
    init_chat2graph()
    mas = AgenticService.load("weaver.yml")

    file_ids = load_data_v1()

    import_graph_schema()

    jobs: List[JobWrapper] = []

    # Process files in batches
    batch_size = 20
    for i in range(0, len(file_ids), batch_size):
        file_ids_batch = file_ids[i : i + batch_size]
        session_id = str(uuid4())

        # set the user message
        user_message = TextMessage(
            payload="""
            你好，请你帮我处理一下我的旅游数据。
            请分析这些文件中的旅行信息，提取关键的地点、时间、活动和情感，
            然后为每次旅行生成富有情感的回忆叙述，并建立相应的知识图谱连接。
            """,
            assigned_expert_name="Memory Integration And Graph Expert",
            session_id=session_id,
        )
        file_messages: List[FileMessage] = []
        for file_id in file_ids_batch:
            file_message = FileMessage(file_id=file_id, session_id=session_id)
            file_messages.append(file_message)

        hybrid_message = HybridMessage(
            instruction_message=user_message,
            attached_messages=file_messages,
        )

        # submit the job
        jobs.append(mas.session().submit(hybrid_message))

    print(f"Submitted {len(jobs)} batch jobs for processing...")

    for i, job in enumerate(jobs):
        print(f"Waiting for batch {i + 1}/{len(jobs)}...")
        service_message = job.wait()

        # print the result
        if isinstance(service_message, TextMessage):
            print(f"Batch {i + 1} Result:\n{service_message.get_payload()}")
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            print(f"Batch {i + 1} Result:\n{text_message.get_payload()}")

        print("-" * 80)


def process_single_memory(trip_data: dict, file_ids: List[str]) -> str:
    """Process a single memory for API usage."""
    init_chat2graph()
    mas = AgenticService.load("weaver.yml")
    import_graph_schema()

    result: str = ""

    session_id = str(uuid4())
    batch_num = 2
    batch_size = len(file_ids) // batch_num + 1
    for i in range(0, min(len(file_ids), 1), batch_size):
        file_ids_batch = file_ids[i : i + batch_size]
        file_messages: List[FileMessage] = []
        for file_id in file_ids_batch:
            file_message = FileMessage(file_id=file_id, session_id=session_id)
            file_messages.append(file_message)

        # set the user message
        user_message = TextMessage(
            payload=f"""
请你帮我处理一下我的旅游数据。
请分析这些文件中的旅行信息，提取关键的地点、时间、活动和情感，
然后为每次旅行生成富有情感的回忆叙述，并建立相应的知识图谱连接。

    旅程名称：{trip_data.get("tripName", "")}
    地点：{trip_data.get("location", "")}
    时间：{trip_data.get("startDate", "")} 到 {trip_data.get("endDate", "")}
    我的笔记：{trip_data.get("notes", "")}
    背景音乐：{trip_data.get("music", "")}

请用富有诗意和情感的语言描述这次旅行，突出重要的瞬间和感受。
""",
            assigned_expert_name="Memory Integration And Graph Expert",
            session_id=session_id,
        )

        hybrid_message = HybridMessage(
            instruction_message=user_message,
            attached_messages=file_messages,
        )

        # submit the job
        service_message = mas.session().submit(hybrid_message).wait()

        if isinstance(service_message, TextMessage):
            result += service_message.get_payload() + "\n"
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            result += text_message.get_payload() + "\n"

    return result or "导入记忆失败"


if __name__ == "__main__":
    main()
