import os

from langchain_openai import ChatOpenAI

def DeepSeek():
    # 当前 DeepSeek 账户余额不足，股票问答改用已验证可用的通义模型。
    return Tongyi()

def Tongyi():
    return ChatOpenAI(
        model= "qwen-max",
        api_key= os.environ.get("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )