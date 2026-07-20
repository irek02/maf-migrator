"""Mini v0.4 AutoGen project fixture."""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

client = OpenAIChatCompletionClient(model="gpt-4", api_key="key")
agent = AssistantAgent(name="assistant", model_client=client)
