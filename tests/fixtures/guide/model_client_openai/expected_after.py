# MAF: OpenAI model client creation
# Source: "Model Client Creation and Configuration > Agent Framework ChatClients"
from agent_framework.openai import OpenAIChatCompletionClient
from azure.identity import AzureCliCredential

# OpenAI (reads API key from environment)
client = OpenAIChatCompletionClient(model="gpt-5")

# Azure OpenAI (pass explicit Azure routing inputs)
azure_client = OpenAIChatCompletionClient(
    model="gpt-5",
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    api_version="2024-12-01",
    credential=AzureCliCredential(),
)
