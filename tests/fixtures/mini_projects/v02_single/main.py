"""Mini v0.2 AutoGen project fixture."""
import autogen
from autogen import AssistantAgent, UserProxyAgent

config_list = [{"model": "gpt-4", "api_key": "key"}]
assistant = AssistantAgent(name="assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent(name="user", human_input_mode="NEVER")
user_proxy.initiate_chat(assistant, message="Hello")
