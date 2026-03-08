# app/services/tools.py
from typing import Dict, List, Tuple, Any
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

# 1. 初始化搜索组件


# 2. 定义工具
@tool(response_format="content_and_artifact")
def internet_search(
    query: str,
    max_results: int = 5,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    当需要查询实时新闻、验证事实或者用户要求查询资料后回复时调用。

    Args:
        query (str): 搜索查询关键词。
        max_results (int): 返回的最大搜索结果数量，默认为5。（可自行调节搜索的数量）。
    """
    ddg_official = DuckDuckGoSearchResults(
    num_results=max_results,
    output_format="list" 
)
    try:
        print(f"\n🕵️ Agent 正在发起专业搜索: '{query}'")
        raw_results = ddg_official.invoke(query) 
        
        llm_view_list = []
        for i, res in enumerate(raw_results, 1):
            llm_view_list.append(f"[{i}] 标题: {res.get('title')}\n内容: {res.get('snippet')}")
        
        llm_content = "\n\n".join(llm_view_list)
        return llm_content, raw_results

    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}", []