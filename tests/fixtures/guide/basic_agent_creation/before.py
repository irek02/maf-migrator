# AutoGen: basic agent creation and execution
# Source: "Single-Agent Feature Mapping > Basic Agent Creation and Execution > AutoGen AssistantAgent"
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool


async def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: sunny"


weather_tool = FunctionTool(
    func=get_weather,
    description="Get weather information"
)

agent = AssistantAgent(
    name="assistant",
    model_client=client,
    system_message="You are a helpful assistant.",
    tools=[weather_tool],
    max_tool_iterations=1
)

result = await agent.run(task="What's the weather?")
