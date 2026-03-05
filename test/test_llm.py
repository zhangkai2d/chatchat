from app.services.llm_service import LLMService

messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好，有什么可以帮您的吗？"}
]

try:
    reply = LLMService.generate_reply(messages)
    print("模型回复:", reply)
except Exception as e:
    print("调用失败:", e)
