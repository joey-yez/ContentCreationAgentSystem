import json
from typing import Dict, Any, Optional
from llm_client import LLMClient, LLMResult

class FeedbackAnalyzer:
    def __init__(self):
        self.llm = LLMClient()
    
    def analyze_and_update_memory(self, current_requirements: Dict[str, Any], 
                                  feedback: str) -> Dict[str, Any]:
        current_requirements_str = json.dumps(current_requirements, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一位智能助手，擅长分析用户反馈并更新任务要求。

当前用户要求：
{current_requirements_str}

用户反馈：
{feedback}

请分析用户反馈中是否包含对以下要求的修改：
1. topic（主题）
2. style（风格）
3. audience（目标读者）
4. estimated_words（预计字数）
5. estimated_sections（预计段落数）

如果用户反馈中包含对某项要求的修改，请提供新的值；如果没有修改，则保持原值为 null。

输出格式要求：
- 使用 JSON 格式输出
- 包含以下字段："topic", "style", "audience", "estimated_words", "estimated_sections"
- 如果某项没有修改，对应字段值为 null
- estimated_words 和 estimated_sections 应为整数或 null

示例输出：
{{
  "topic": null,
  "style": "深度分析",
  "audience": "普通军事爱好者",
  "estimated_words": null,
  "estimated_sections": 6
}}

注意：
- 请仔细阅读用户反馈，理解用户的真实意图
- 如果用户说"增加一个章节"，而当前是 5 个章节，新值应该是 6
- 如果用户说"改为 6 个章节"，新值应该是 6
- 如果用户只是要求修改内容而没有改变要求，所有字段都为 null
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的需求分析助手，擅长理解用户反馈并提取关键需求变更。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.3)
        
        try:
            result = json.loads(llm_result.content)
            return result
        except:
            return {
                "topic": None,
                "style": None,
                "audience": None,
                "estimated_words": None,
                "estimated_sections": None
            }
