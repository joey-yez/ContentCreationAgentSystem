from typing import Dict, Any, Optional, List
from llm_client import LLMClient, LLMResult

class EvaluationResult:
    def __init__(self, score: float, feedback: str, criteria: List[Dict[str, Any]]):
        self.score = score
        self.feedback = feedback
        self.criteria = criteria
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "feedback": self.feedback,
            "criteria": self.criteria
        }

class EvaluatorAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def evaluate_outline(self, topic: str, outline: Dict[str, Any], 
                        user_requirements: Dict[str, Any]) -> EvaluationResult:
        prompt = f"""
你是一位专业的内容评估师。请根据用户的要求评估以下文章大纲：

用户要求：
- 主题：{user_requirements.get('topic', '')}
- 风格：{user_requirements.get('style', '未指定')}
- 目标读者：{user_requirements.get('audience', '未指定')}
- 预计字数：{user_requirements.get('estimated_words', '未指定')}
- 预计段落数：{user_requirements.get('estimated_sections', '未指定')}

大纲内容：
{outline}

请从以下几个方面进行评估：
1. **相关性**：大纲是否紧扣主题？
2. **结构完整性**：是否有合理的引言、主体和结论？
3. **深度**：是否有足够的分析深度？
4. **符合要求**：是否符合用户指定的风格、字数和段落数要求？

评分标准（0-10分）：
- 10分：完全符合所有要求
- 8-9分：基本符合要求，略有不足
- 6-7分：部分符合要求，需要改进
- 4-5分：不太符合要求，需要重大修改
- 0-3分：不符合要求

输出格式要求：
- JSON 格式输出
- 包含 "score" (0-10的数字)、"feedback" (评估反馈文字)、"criteria" (数组，每个元素包含 "name" 和 "score")

示例：
{{
  "score": 8.5,
  "feedback": "大纲结构完整，主题明确，但深度可以进一步加强。",
  "criteria": [
    {{"name": "相关性", "score": 9}},
    {{"name": "结构完整性", "score": 8}},
    {{"name": "深度", "score": 8}},
    {{"name": "符合要求", "score": 9}}
  ]
}}
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的内容评估师，擅长评估文章大纲的质量和符合度。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.3)
        
        import json
        try:
            result = json.loads(llm_result.content)
            return EvaluationResult(
                score=result.get("score", 0),
                feedback=result.get("feedback", ""),
                criteria=result.get("criteria", [])
            )
        except:
            return EvaluationResult(
                score=7.0,
                feedback="无法解析评估结果",
                criteria=[]
            )
    
    def evaluate_article(self, topic: str, outline: Dict[str, Any], 
                        article_content: str, 
                        user_requirements: Dict[str, Any]) -> EvaluationResult:
        prompt = f"""
你是一位专业的内容评估师。请根据用户的要求评估以下文章：

用户要求：
- 主题：{user_requirements.get('topic', '')}
- 风格：{user_requirements.get('style', '未指定')}
- 目标读者：{user_requirements.get('audience', '未指定')}
- 预计字数：{user_requirements.get('estimated_words', '未指定')}

文章大纲：
{outline}

文章内容（前2000字符）：
{article_content[:2000]}

请从以下几个方面进行评估：
1. **相关性**：内容是否紧扣主题？
2. **结构完整性**：是否按照大纲完成了所有章节？
3. **内容深度**：分析是否深入、有说服力？
4. **风格一致性**：是否符合指定的写作风格？
5. **目标受众适配**：是否适合目标读者阅读？
6. **语言质量**：语言表达是否流畅、专业？

评分标准（0-10分）：
- 10分：完全符合所有要求，质量优秀
- 8-9分：基本符合要求，质量良好
- 6-7分：部分符合要求，需要改进
- 4-5分：不太符合要求，需要重大修改
- 0-3分：不符合要求

输出格式要求：
- JSON 格式输出
- 包含 "score" (0-10的数字)、"feedback" (评估反馈文字)、"criteria" (数组，每个元素包含 "name" 和 "score")

示例：
{{
  "score": 8.5,
  "feedback": "文章内容详实，结构清晰，符合专业风格要求。",
  "criteria": [
    {{"name": "相关性", "score": 9}},
    {{"name": "结构完整性", "score": 9}},
    {{"name": "内容深度", "score": 8}},
    {{"name": "风格一致性", "score": 8}},
    {{"name": "目标受众适配", "score": 9}},
    {{"name": "语言质量", "score": 8}}
  ]
}}
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的内容评估师，擅长评估文章的质量和符合度。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.3)
        
        import json
        try:
            result = json.loads(llm_result.content)
            return EvaluationResult(
                score=result.get("score", 0),
                feedback=result.get("feedback", ""),
                criteria=result.get("criteria", [])
            )
        except:
            return EvaluationResult(
                score=7.0,
                feedback="无法解析评估结果",
                criteria=[]
            )
