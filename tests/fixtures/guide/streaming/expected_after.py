# MAF: streaming agent responses
# Source: "Single-Agent Feature Mapping > Streaming Support > Agent Framework Streaming"

# Agent streaming — uniform chunk shape, no isinstance dispatch needed
async for chunk in agent.run("Hello", stream=True):
    if chunk.text:
        print(chunk.text, end="", flush=True)
