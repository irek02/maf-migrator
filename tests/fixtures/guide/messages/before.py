# AutoGen: message types and creation
# Source: "Single-Agent Feature Mapping > Message Types and Creation > AutoGen Message Types"
from autogen_agentchat.messages import TextMessage, MultiModalMessage

# Text message — requires source field (string, not Role enum)
text_msg = TextMessage(content="Hello", source="user")

# Multi-modal message — heterogeneous list, image_data is an autogen Image object
multi_modal_msg = MultiModalMessage(
    content=["Describe this image", image_data],
    source="user"
)

# Explicit conversion needed to pass to model clients
user_message = text_msg.to_model_message()
