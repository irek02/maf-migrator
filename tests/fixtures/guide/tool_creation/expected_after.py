# MAF: tool creation with @tool decorator
# Source: "Single-Agent Feature Mapping > Tool Creation and Integration > Agent Framework @tool"
from agent_framework import Agent, tool
from typing import Annotated
from pydantic import Field


@tool
def get_weather(
    location: Annotated[str, Field(description="The location to get weather for")]
) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: sunny"


# Direct use with agent — automatic schema conversion
agent = Agent(name="assistant", client=client, tools=[get_weather])
