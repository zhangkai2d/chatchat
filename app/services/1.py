import os
from typing import Literal
from dotenv import load_dotenv
from typing import Literal, Dict, List, Tuple, Any
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from time import time
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.messages import AIMessageChunk
from datetime import datetime



# 1. 加载环境变量
env_path = r"F:\zhangkai\code\chatchat\.env"
load_dotenv(dotenv_path=env_path)

api_key = "sk-48581151e52849faa01799d4f33b2742"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"


ddg_official = DuckDuckGoSearchResults(
    num_results=5,
    output_format="string"  
)


@tool(response_format="content_and_artifact") # 🌟 开启内容与附件分离模式
def internet_search(
    query: str,
    max_results: int = 5,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    当需要查询实时新闻、验证事实或获取当前日期相关信息时使用。
    """
    try:
        print(f"\n🕵️ Agent 正在发起专业搜索: '{query}'")
        
        # 1. 调用底层的原始数据 (这是一个 list of dict)
        # 注意：DuckDuckGoSearchResults 的 invoke 会返回 (content, raw_results)
        raw_results, _ = ddg_official.invoke(query)
        
        # 2. 加工给“大模型”看的文本 (精简、省 Token)
        # 我们只给模型看标题和摘要，不给模型看长长的链接，除非它主动要
        llm_view_list = []
        for i, res in enumerate(raw_results, 1):
            llm_view_list.append(f"[{i}] 标题: {res.get('title')}\n内容: {res.get('snippet')}")
        
        llm_content = "\n\n".join(llm_view_list)
        
        # 3. 返回元组：(给模型看的字符串, 给程序/前端看的原始列表)
        return llm_content, raw_results

    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}", []
    
# 获取当前时间并格式化
now = datetime.now()
weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
current_time_str = now.strftime(f"%Y-%m-%d %H:%M {weekdays[now.weekday()]}")

# 4. 优化后的 System Prompt
research_instructions = f"""你是一名极其简洁的数字助手。
【当前时间】：{current_time_str}。

【回复准则】：
1. 简洁至上：除非用户要求详细解释，否则回复必须保持简洁完善。
2. 针对性：问什么答什么，不要重复用户的问题，。

【示例】：
用户：现在几点
助手：现在是21:45分

用户：今天几号
助手：今天是3月6号

【工具】
1.internet_search：当需要查询实时新闻、验证事实或获取当前日期相关信息时使用。调用时请提供一个简洁的查询语句和需要的结果数量（默认为5）。工具会返回一个字符串，包含搜索结果的标题和摘要，以及一个原始结果列表供程序使用。
"""

model = ChatOpenAI(
    model="qwen-plus",
    api_key=api_key,
    base_url=base_url,
)


# 6. 初始化 Agent 并执行
agent = create_deep_agent(
    model=model,
    tools=[internet_search], 
    system_prompt=research_instructions
)

def get_agent_response(user_input: str):
    """
    这是一个生成器函数，模拟流式接口
    """
    # 构造输入
    inputs = {"messages": [{"role": "user", "content": user_input}]}
    
    # 这里的 agent.stream 本身就是一个迭代器
    for token, metadata in agent.stream(inputs, stream_mode="messages"):
        if isinstance(token, AIMessageChunk):
            # 提取增量内容
            for block in token.content_blocks:
                if block["type"] == "text":
                    # 使用 yield 一个字一个字地返回数据
                    yield block["text"]
                elif block["type"] == "reasoning":
                    # 推理过程也可以 yield，前端可以展示成“思考中...”
                    yield f"💭 {block['reasoning']}"

# 使用方法：
print("🤖 Agent 开始蹦字：")
for char in get_agent_response("你去网上查找资料，帮我解释什么是 LangChain？"):
    print(char, end="", flush=True)