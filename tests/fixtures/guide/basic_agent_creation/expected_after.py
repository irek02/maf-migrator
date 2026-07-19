# MAF: basic agent creation and execution
# Source: "Single-Agent Feature Mapping > Basic Agent Creation and Execution > Agent Framework Agent"
from agent_framework import Agent, tool


@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: sunny"


agent = Agent(
    name="assistant",
    client=client,
    instructions="You are a helpful assistant.",
    tools=[get_weather],
)

result = await agent.run("What's the weather?")
