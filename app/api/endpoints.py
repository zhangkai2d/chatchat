from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # 将 Pydantic 模型转换为大模型 API 需要的字典列表格式
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    try:
        reply_content = LLMService.generate_reply(messages_dict)
        return ChatResponse(reply=reply_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))