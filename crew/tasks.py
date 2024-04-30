from crewai import Task
from .agents import major_tom


def create_task(topic):
    return Task(
        description=f"Analyze the topic: {topic}",
        expected_output=f"A detailed analysis of the topic '{topic}'.",
        agent=major_tom,
    )
