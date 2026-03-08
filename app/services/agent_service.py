# app/services/agent_service.py
import os
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.agents import create_agent
from langchain.messages import AIMessageChunk

# 引入我们刚才拆分出来的模块
from app.services.tools import internet_search
from app.services.prompts import SYSTEM_PROMPT_TEMPLATE
from app.core.config import settings
from app.services.middleware import handle_tool_errors
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from time import time

@dataclass
class Context:
    user_id: str
    current_time: str

@dynamic_prompt
def generate_dynamic_system_prompt(request: ModelRequest) -> str:
    """根据运行时上下文填充系统提示词中的占位符。"""
    context_data = request.runtime.context

    # 确保 context_data.current_time 存在并与 SYSTEM_PROMPT_TEMPLATE 中的占位符名称一致
    formatted_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        current_time=context_data.current_time
    )
    return formatted_prompt

class AgentService:
    def __init__(self):
        """初始化模型和 Agent"""
        # 确保环境变量被加载
        self.model = self.initialize_config()

        # 2. 初始化 Agent（动态获取最新时间 Prompt）
        self.agent = create_agent(
            model=self.model,
            tools=[internet_search], 
            middleware=[handle_tool_errors, generate_dynamic_system_prompt],
            system_prompt="",
            checkpointer=self.checkpointer,
            context_schema=Context
        )
        

    def stream_chat(self, user_input: str, user_id: str = "guest"):
        """流式生成器函数，用于逐字返回结果"""

        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        current_time_str = now.strftime(f"%Y-%m-%d %H:%M {weekdays[now.weekday()]}")

        inputs = {"messages": [{"role": "user", "content": user_input}]}
        
        # 在执行时通过 config 传递上下文
        config = {"configurable": {"thread_id": user_id}}
        
        for token, metadata in self.agent.stream(
            inputs, 
            config=config,  # 🌟 关键：将配置传给整个链
            stream_mode="messages",
            context=Context(user_id=user_id, current_time=current_time_str)
        ):
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
                timeout=120,
            )
        self.checkpointer = InMemorySaver()  # 使用内存保存器，适合短期记忆测试
        return model

from time import time

def test_short_term_memory(service):
    """用于测试性能和记忆的交互式控制台"""
    print("=== 🧠 Agent 性能测试模式 ===")
    
    while True:
        user_input = input("\n🧑 用户: ")
        if user_input.lower() in ['exit', 'quit']: break
            
        print("🤖 Agent 思考中...", end="", flush=True)
        
        start_time = time() # 记录请求开始时间
        first_token_time = None
        
        try:
            for char in service.stream_chat(user_input):
                if first_token_time is None:
                    first_token_time = time() # 记录第一个字弹出的时间
                    ttft = first_token_time - start_time
                    # \r 用于清除“思考中...”的提示
                    print(f"\r[⏱️ 首字耗时: {ttft:.2f}s] 🤖: ", end="", flush=True)
                
                print(char, end="", flush=True)
        except Exception as e:
            print(f"\n[错误]: {str(e)}")
            
        total_time = time() - start_time
        print(f"\n[⏱️ 总计耗时: {total_time:.2f}s]")
        print("-" * 40)


# 如果你只想在这个文件里本地测试一下：
if __name__ == "__main__":
    service = AgentService()
    print("🤖 Agent ：")
    # for char in service.stream_chat("你去网上查找资料，帮我解释什么是 LangChain？"):
    #     print(char, end="", flush=True)
    test_short_term_memory(service)


# https://docs.langchain.com/oss/python/langchain/tools#access-context

# 阅读这篇文档的access context 部分，我现在想要实现这个里面的工具的功能