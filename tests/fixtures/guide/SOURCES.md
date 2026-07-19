# Guide Fixture Sources

These before/after pairs are extracted from the official Microsoft AutoGen→MAF migration guide:
https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/

Each subdirectory maps directly to a section of the guide. The `before.py` shows canonical
AutoGen 0.4 (`autogen_agentchat`) code; `expected_after.py` shows the MAF equivalent.

| Case | Guide Section | Key Transform |
|---|---|---|
| `model_client_openai` | Model Client Creation > AutoGen Model Clients / Agent Framework ChatClients | `AzureOpenAIChatCompletionClient` → `OpenAIChatCompletionClient`; `api_key` param dropped (reads from env) |
| `basic_agent_creation` | Single-Agent > Basic Agent Creation > AutoGen AssistantAgent / Agent Framework Agent | `AssistantAgent(model_client=, system_message=, max_tool_iterations=)` → `Agent(client=, instructions=)` |
| `tool_creation` | Single-Agent > Tool Creation > AutoGen FunctionTool / Agent Framework @tool | `FunctionTool(func=, description=)` → `@tool` decorator |
| `streaming` | Single-Agent > Streaming Support | `agent.run_stream(task=)` + `isinstance` dispatch → `agent.run(stream=True)` + `chunk.text` |
| `messages` | Single-Agent > Message Types > AutoGen / Agent Framework | `TextMessage(content=, source=)` → `Message(role=, contents=[])` |
