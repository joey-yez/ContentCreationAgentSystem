from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class LLMResult:
    def __init__(self, content: str, duration: float, prompt_tokens: int, 
                 completion_tokens: int, total_tokens: int):
        self.content = content
        self.duration = duration
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

class LLMClient:
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "deepseek")
        
        if self.provider == "deepseek":
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        else:
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    def chat(self, messages: list, temperature: float = 0.7) -> LLMResult:
        start_time = time.time()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        
        duration = time.time() - start_time
        
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0
        
        return LLMResult(
            content=response.choices[0].message.content,
            duration=duration,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
