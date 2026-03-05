from fastapi import FastAPI
from app.api.endpoints import router as chat_router

app = FastAPI(
    title="ChatChat API",
    description="后端大模型对话接口服务",
    version="0.1.0"
)

# 注册路由
app.include_router(chat_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    # 本地启动服务器
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)