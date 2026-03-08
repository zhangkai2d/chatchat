# app/services/agent_service.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.messages import AIMessageChunk

# 引入我们刚才拆分出来的模块
from app.services.tools import internet_search
from app.services.prompts import get_agent_system_prompt
from app.core.config import settings
from app.services.middleware import handle_tool_errors



class AgentService:
    def __init__(self):
        """初始化模型和 Agent"""
        # 确保环境变量被加载
        self.model = self.initialize_config()

        # 2. 初始化 Agent（动态获取最新时间 Prompt）
        self.agent = create_deep_agent(
            model=self.model,
            tools=[internet_search], 
            middleware=[handle_tool_errors],
            system_prompt=get_agent_system_prompt()
        )

    def stream_chat(self, user_input: str):
        """流式生成器函数，用于逐字返回结果"""
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        
        for token, metadata in self.agent.stream(inputs, stream_mode="messages"):
            if isinstance(token, AIMessageChunk):
                for block in token.content_blocks:
                    if block["type"] == "text":
                        yield block["text"]
                    elif block["type"] == "reasoning":
                        yield f"💭 {block['reasoning']}\n"

    def initialize_config(self, model_name: str = "qwen-plus") -> ChatOpenAI:
        """初始化环境变量配置"""
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.DASHSCOPE_BASE_URL

        if model_name == "qwen-plus":
            model = ChatOpenAI(
                model="qwen-plus",
                api_key=self.api_key,
                base_url=self.base_url,
            )

        return model




# 如果你只想在这个文件里本地测试一下：
if __name__ == "__main__":
    service = AgentService()
    print("🤖 Agent ：")
    for char in service.stream_chat("你去网上查找资料，帮我解释什么是 LangChain？"):
        print(char, end="", flush=True)


# https://docs.langchain.com/oss/python/langchain/tools#access-context

# 阅读这篇文档的access context 部分，我现在想要实现这个里面的工具的功能