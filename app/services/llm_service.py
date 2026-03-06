import dashscope
import os
from dotenv import load_dotenv

load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

class LLMService:
    @staticmethod
    def generate_reply(messages: list[dict]) -> str:
        try:
            response = dashscope.Generation.call(
                model="qwen-plus",
                messages=messages,
                result_format='message'
            )
            # 提取大模型的回复内容
            return response.output.choices[0].message.content
        except Exception as e:
            # 在工程中，这里应该加入日志记录 (logging)
            raise Exception(f"调用大模型失败: {str(e)}")
    

        
if __name__ == "__main__":
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"}
    ]
    print(LLMService.generate_reply(test_messages))