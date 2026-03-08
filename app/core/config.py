# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import find_dotenv

class Settings(BaseSettings):
    # --- 阿里云大模型配置 ---
    # 定义为 str 类型，如果 .env 里没有配这个值，项目启动时会直接报错提醒你！
    DASHSCOPE_API_KEY: str 
    # 提供默认值，如果在 .env 没配，就用这个默认的
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # --- LangSmith 追踪配置 (可选配置) ---
    LANGSMITH_TRACING: Optional[str] = "false"
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    # Pydantic 专属配置，让它自动去项目根目录找 .env 文件
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略 .env 中存在但这里没定义的变量
    )

# 实例化一个单例对象，整个项目共享这一个 settings！
settings = Settings()