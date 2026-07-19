# AutoGen: OpenAI model client creation
# Source: "Model Client Creation and Configuration > AutoGen Model Clients"
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient

# OpenAI
client = OpenAIChatCompletionClient(
    model="gpt-5",
    api_key="your-key"
)

# Azure OpenAI
azure_client = AzureOpenAIChatCompletionClient(
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    azure_deployment="gpt-5",
    api_version="2024-12-01",
    api_key="your-key"
)
