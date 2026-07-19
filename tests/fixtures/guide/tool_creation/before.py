# AutoGen: tool creation with FunctionTool
# Source: "Single-Agent Feature Mapping > Tool Creation and Integration > AutoGen FunctionTool"
from autogen_core.tools import FunctionTool


async def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: sunny"


# Manual tool creation — schema inferred from function signature
weather_tool = FunctionTool(
    func=get_weather,
    description="Get weather information"
)

# Use with agent
agent = AssistantAgent(name="assistant", model_client=client, tools=[weather_tool])
