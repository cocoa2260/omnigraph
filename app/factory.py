# app/factory.py
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

class LLMFactory:
    @staticmethod
    def get_model(mode: str):
        if "LOCAL" in mode:
            return ChatOllama(
                model=os.getenv("OLLAMA_MODEL"),
                base_url=os.getenv("OLLAMA_BASE_URL"),
                temperature=0  # 기업용은 정확도를 위해 0으로 설정
            )
        else:
            # Groq 등 외부 API 지원 확장용
            return ChatOpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="mixtral-8x7b-32768"
            )