from pydantic import BaseModel
from typing import List, Dict

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    # 后续可以扩展，比如 model_name, temperature 等参数

class ChatResponse(BaseModel):
    reply: str