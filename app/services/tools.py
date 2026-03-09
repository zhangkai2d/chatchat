# app/services/tools.py
from typing import Dict, List, Tuple, Any
from langchain.tools import tool, ToolRuntime
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel, Field  
from langchain_core.runnables import RunnableConfig 

# 1. 初始化搜索组件



# 1. 🌟 定义高级输入模式 (Advanced Schema)
class SearchInput(BaseModel):
    """DuckDuckGo 互联网搜索工具的输入参数说明"""
    
    query: str = Field(
        description="搜索的关键词。必须提取出最核心的实体，尽量精准。如果涉及时间，请带上具体年份。"
    )
    max_results: int = Field(
        default=5, 
        ge=1,   # 限制最小值：大于等于1
        le=10,  # 限制最大值：小于等于10
        description="需要返回的搜索结果数量。最小值为1最大值为10"
    )

# 2. 定义工具
@tool(args_schema=SearchInput,response_format="content_and_artifact")
def internet_search(
    query: str,
    max_results: int = 5,
    runtime: ToolRuntime = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    当需要查询实时新闻、验证事实或者用户要求查询资料后回复时调用。

    Args:
        query (str): 搜索查询关键词。
        max_results (int): 返回的最大搜索结果数量，默认为5。（可自行调节搜索的数量）。
    """
    user_id = "匿名用户"
    current_time_str = "未知时间"

    if runtime and runtime.context:
        # 确保你的 Context 类被正确传递和解析
        # 这里的 runtime.context 会是你的 Context(user_id=..., current_time=...) 实例
        if hasattr(runtime.context, "user_id"):
            user_id = runtime.context.user_id
        if hasattr(runtime.context, "current_time"):
            current_time_str = runtime.context.current_time

    if runtime and runtime.context:
        if hasattr(runtime.context, "current_time"):
            current_time_str = runtime.context.current_time


    ddg_official = DuckDuckGoSearchResults(num_results=max_results, output_format="list")
    
    print(f"\n🕵️ 用户[{user_id}] 正在搜索: '{query}')")
    
    # 使用增强后的查询词进行搜索
    raw_results = ddg_official.invoke(query)
    
    llm_view_list = []
    for i, res in enumerate(raw_results, 1):
        llm_view_list.append(f"[{i}] 标题: {res.get('title')}\n内容: {res.get('snippet')}")
    
    llm_content = "\n\n".join(llm_view_list)
    print(llm_content)
    print(raw_results)
    return llm_content, raw_results
    
if __name__ == "__main__":
    # 本地测试工具
    search_input = SearchInput(
        query="2024年最新的人工智能发展趋势", 
        max_results=3
    )
    content, artifacts = internet_search(**search_input.model_dump())
