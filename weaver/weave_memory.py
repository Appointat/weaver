from typing import List

from chat2graph.core.model.message import HybridMessage, TextMessage
from chat2graph.core.sdk.agentic_service import AgenticService
from chat2graph.core.sdk.wrapper.job_wrapper import JobWrapper

from weaver.util.init_chat2graph import init_chat2graph


def main():
    """Main function."""
    init_chat2graph()

    mas = AgenticService.load("weaver.yml")
    jobs: List[JobWrapper] = []

    jobs = run_scene_and_activity_expert(mas, jobs)
    jobs = run_observation_detail_expert(mas, jobs)
    jobs = run_affective_resonance_expert(mas, jobs)
    jobs = run_narrative_anchor_explorer_expert(mas, jobs)

    sotry_context: str = ""
    for job in jobs:
        service_message = job.wait()

        # print the result
        if isinstance(service_message, TextMessage):
            print(f"Service Result:\n{service_message.get_payload()}")
            sotry_context += service_message.get_payload()
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            print(f"Service Result:\n{text_message.get_payload()}")
            sotry_context += text_message.get_payload()

    # set the user message
    user_message = TextMessage(
        payload=f"""
        我想回忆一下杭州西湖的旅游经历。
        你能帮我生成一个有我的旅游故事吗？
        {sotry_context}
        """,
        assigned_expert_name="Creative Story Synthesizer Expert",
    )
    # submit the job
    service_message = mas.session().submit(user_message).wait()
    # print the result
    print(f"Story Context:\n{sotry_context}")
    if isinstance(service_message, TextMessage):
        print(f"Service Result:\n{service_message.get_payload()}")
    # print the result
    elif isinstance(service_message, TextMessage):
        print(f"Service Result:\n{service_message.get_payload()}")


def meave_memory(user_instruction: str) -> JobWrapper:
    """Meave memory."""
    init_chat2graph()

    mas = AgenticService.load("weaver.yml")
    jobs: List[JobWrapper] = []

    jobs = run_scene_and_activity_expert(mas, jobs)
    jobs = run_observation_detail_expert(mas, jobs)
    jobs = run_affective_resonance_expert(mas, jobs)
    jobs = run_narrative_anchor_explorer_expert(mas, jobs)

    sotry_context: str = ""
    for job in jobs:
        service_message = job.wait()

        # print the result
        if isinstance(service_message, TextMessage):
            print(f"Service Result:\n{service_message.get_payload()}")
            sotry_context += service_message.get_payload()
        elif isinstance(service_message, HybridMessage):
            text_message = service_message.get_instruction_message()
            print(f"Service Result:\n{text_message.get_payload()}")
            sotry_context += text_message.get_payload()

    # set the user message
    user_message = TextMessage(
        payload=f"""
    {user_instruction}
    {sotry_context}
        """,
        assigned_expert_name="Creative Story Synthesizer Expert",
    )

    # submit the job
    final_job = mas.session().submit(user_message)
    service_message = final_job.wait()
    # print the result
    print(f"Story Context:\n{sotry_context}")
    if isinstance(service_message, TextMessage):
        print(f"Service Result:\n{service_message.get_payload()}")
    # print the result
    elif isinstance(service_message, TextMessage):
        print(f"Service Result:\n{service_message.get_payload()}")
    return final_job


def run_scene_and_activity_expert(mas: AgenticService, jobs: List[JobWrapper]) -> List[JobWrapper]:
    """Run the Scene and Activity Expert."""
    # set the user message
    user_message = TextMessage(
        payload="""
        我想回忆一下杭州西湖的旅游经历。
        """,
        assigned_expert_name="Scene And Activity Expert",
    )

    # submit the job
    jobs.append(mas.session().submit(user_message))

    return jobs


def run_observation_detail_expert(mas: AgenticService, jobs: List[JobWrapper]) -> List[JobWrapper]:
    """Run the Observation Detail Expert."""
    # set the user message
    user_message = TextMessage(
        payload="""
        我想回忆一下杭州西湖的旅游经历。
        """,
        assigned_expert_name="Observation Detail Expert",
    )

    # submit the job
    jobs.append(mas.session().submit(user_message))

    return jobs


def run_affective_resonance_expert(mas: AgenticService, jobs: List[JobWrapper]) -> List[JobWrapper]:
    """Run the Affective Resonance Expert."""
    # set the user message
    user_message = TextMessage(
        payload="""
        我想回忆一下杭州西湖的旅游经历。
        """,
        assigned_expert_name="Affective Resonance Expert",
    )

    # submit the job
    jobs.append(mas.session().submit(user_message))

    return jobs


def run_narrative_anchor_explorer_expert(mas: AgenticService, jobs: List[JobWrapper]) -> List[JobWrapper]:
    """Run the Narrative Anchor Explorer Expert."""
    # set the user message
    user_message = TextMessage(
        payload="""
        我想回忆一下杭州西湖的旅游经历。
        """,
        assigned_expert_name="Narrative Anchor Explorer Expert",
    )

    # submit the job
    jobs.append(mas.session().submit(user_message))

    return jobs


def run_creative_story_synthesizer_expert(mas: AgenticService, jobs: List[JobWrapper]) -> List[JobWrapper]:
    """Run the Creative Story Synthesizer Expert."""
    # set the user message
    user_message = TextMessage(
        payload="""
        我想回忆一下杭州西湖的旅游经历。
        """,
        assigned_expert_name="Creative Story Synthesizer Expert",
    )

    # submit the job
    jobs.append(mas.session().submit(user_message))

    return jobs


if __name__ == "__main__":
    main()
