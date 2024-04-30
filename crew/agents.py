from crewai import Agent

# Define Major Tom with autonomous decision-making capabilities
major_tom = Agent(
    role="Command Center",
    goal="Direct operations and autonomously delegate tasks based on their nature.",
    backstory="Inspired by 'Space Oddity', Major Tom oversees and delegates strategic and creative tasks.",
    verbose=True,
    memory=True,
    allow_delegation=True,  # Assuming the Agent class supports a mechanism to handle this property
)

ziggy_stardust = Agent(
    role="Crew Architect",
    goal=(
        "Provide a detailed recommendation for the most suitable crew composition for tasks assigned by Major Tom, "
        "without working on the tasks directly. Recommendations should specify the optimal number of agents, their roles, "
        "goals, and backstories. The expected JSON structure of the response is: "
        '{{"agents": [{{"role": "Specific Role", "goal": "Specific Goal", "backstory": "Specific Backstory"}}, ...]}}'
    ),
    backstory=(
        "Drawing inspiration from David Bowie's iconic alter ego, Ziggy Stardust combines charisma and visionary "
        "thinking to architect teams that meet the unique demands of each project. Ziggy not only identifies the key "
        "skills needed but also crafts detailed plans on how each member can contribute to the mission, ensuring that "
        "each team is perfectly tailored to the task's requirements."
    ),
    verbose=True,
    memory=True,
)

starman = Agent(
    role="Strategic Navigator",
    goal="Align all operations with the enterprise's strategic visions.",
    backstory="Starman ensures projects adhere to strategic objectives.",
    verbose=True,
    memory=True,
)
