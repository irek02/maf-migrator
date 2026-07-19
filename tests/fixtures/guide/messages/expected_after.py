# MAF: message types and creation
# Source: "Single-Agent Feature Mapping > Message Types and Creation > Agent Framework Message Types"
from agent_framework import Message, Content
import base64

# Text message — unified Message class, role= instead of source=
text_msg = Message(role="user", contents=["Hello"])

# Multi-modal message — typed Content objects
image_bytes = b"<your_image_bytes>"
image_b64 = base64.b64encode(image_bytes).decode()
image_uri = f"data:image/jpeg;base64,{image_b64}"

multi_modal_msg = Message(
    role="user",
    contents=[
        Content.from_text(text="Describe this image"),
        Content.from_uri(uri=image_uri, media_type="image/jpeg")
    ]
)
