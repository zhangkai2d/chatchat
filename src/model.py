import os
from dotenv import load_dotenv
from langchain_community.llms import Tongyi

load_dotenv()

def init_qwen():
    # 确保在 .env 中设置了 DASHSCOPE_API_KEY
    llm = Tongyi(model_name="qwen-turbo")
    return llm