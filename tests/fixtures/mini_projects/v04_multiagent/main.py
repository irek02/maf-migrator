"""Mini v0.4 multi-agent fixture exercising group-chat, termination, and model-context constructs."""
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_core.models import ChatCompletionClient, UserMessage, AssistantMessage, LLMMessage
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient

client = OpenAIChatCompletionClient(model="gpt-4", api_key="key")
context = BufferedChatCompletionContext(buffer_size=10)
agent1 = AssistantAgent(name="agent1", model_client=client)
agent2 = AssistantAgent(name="agent2", model_client=client)
team = RoundRobinGroupChat(participants=[agent1, agent2])
selector = SelectorGroupChat(participants=[agent1, agent2], model_client=client)
term = MaxMessageTermination(max_messages=10)
mention_term = TextMentionTermination(text="DONE")
