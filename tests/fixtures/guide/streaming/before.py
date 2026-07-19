# AutoGen: streaming agent responses
# Source: "Single-Agent Feature Mapping > Streaming Support > AutoGen Streaming"
from autogen_agentchat.messages import ModelClientStreamingChunkEvent
from autogen_agentchat.base import TaskResult

# Agent streaming — event-based, requires isinstance dispatch
async for event in agent.run_stream(task="Hello"):
    if isinstance(event, ModelClientStreamingChunkEvent):
        print(event.content, end="")
    elif isinstance(event, TaskResult):
        print("Final result received")
