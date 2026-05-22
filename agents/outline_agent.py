import json
from typing import List, Optional, Dict, Any, Tuple
from llm_client import LLMClient, LLMResult

class OutlineAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def generate_outline(self, topic: str, style: Optional[str] = None, 
                         audience: Optional[str] = None, 
                         estimated_words: Optional[int] = None) -> Tuple[Dict[str, Any], Dict[str, float]]:
        style_text = f"风格：{style}" if style else ""
        audience_text = f"目标读者：{audience}" if audience else ""
        length_text = f"预计字数：{estimated_words}" if estimated_words else ""
        
        prompt = f"""
你是一个专业的内容策划师。请根据以下信息为文章生成详细的大纲：

主题：{topic}
{style_text}
{audience_text}
{length_text}

请输出结构化的大纲，包含：
1. 文章标题
2. 一级章节（每个章节需要有简短的摘要说明）
3. 每个一级章节下的二级子标题

输出格式要求：
- 使用 JSON 格式输出
- 包含 "title" (字符串) 和 "sections" (数组)
- 每个 section 包含 "id", "title", "summary", "subsections" (数组)
- subsections 包含 "id", "title"

示例输出格式：
{{
  "title": "文章标题",
  "sections": [
    {{
      "id": 1,
      "title": "第一章：引言",
      "summary": "介绍主题背景和重要性",
      "subsections": [
        {{
          "id": 1.1,
          "title": "研究背景"
        }}
      ]
    }}
  ]
}}
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的内容策划师和编辑，擅长为各种主题生成结构化的文章大纲。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.7)
        
        try:
            result = json.loads(llm_result.content)
        except:
            result = self._parse_fallback(llm_result.content, topic)
        
        metrics = {
            "duration": llm_result.duration,
            "prompt_tokens": llm_result.prompt_tokens,
            "completion_tokens": llm_result.completion_tokens,
            "total_tokens": llm_result.total_tokens
        }
        
        return result, metrics
    
    def revise_outline(self, topic: str, current_outline: Dict[str, Any], 
                       feedback: str, previous_feedback: str = "",
                       style: Optional[str] = None, 
                       audience: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, float]]:
        style_text = f"风格：{style}" if style else ""
        audience_text = f"目标读者：{audience}" if audience else ""
        
        current_outline_str = json.dumps(current_outline, ensure_ascii=False, indent=2)
        
        previous_feedback_text = f"""
之前的修改反馈：
{previous_feedback}
""" if previous_feedback else ""
        
        prompt = f"""
你是一位专业的内容策划师。请根据用户反馈修改以下文章大纲：

文章主题：{topic}
{style_text}
{audience_text}

{previous_feedback_text}

当前大纲：
{current_outline_str}

用户反馈：
{feedback}

请根据用户反馈修改大纲，注意保持与原始要求的一致性。

输出格式要求：
- 使用 JSON 格式输出
- 包含 "title" (字符串) 和 "sections" (数组)
- 每个 section 包含 "id", "title", "summary", "subsections" (数组)
- subsections 包含 "id", "title"

示例输出格式：
{{
  "title": "文章标题",
  "sections": [
    {{
      "id": 1,
      "title": "第一章：引言",
      "summary": "介绍主题背景和重要性",
      "subsections": [
        {{
          "id": 1.1,
          "title": "研究背景"
        }}
      ]
    }}
  ]
}}
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的内容策划师和编辑，擅长根据用户反馈修改文章大纲。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.7)
        
        try:
            result = json.loads(llm_result.content)
        except:
            result = self._parse_fallback(llm_result.content, topic)
        
        metrics = {
            "duration": llm_result.duration,
            "prompt_tokens": llm_result.prompt_tokens,
            "completion_tokens": llm_result.completion_tokens,
            "total_tokens": llm_result.total_tokens
        }
        
        return result, metrics
    
    def _parse_fallback(self, content: str, topic: str) -> Dict[str, Any]:
        lines = content.strip().split('\n')
        sections = []
        current_section = None
        section_id = 1
        fallback_title = topic
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                fallback_title = line[2:].strip()
            elif line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "id": section_id,
                    "title": line[3:].strip(),
                    "summary": "",
                    "subsections": []
                }
                section_id += 1
            elif line.startswith('- ') and current_section:
                subsection_id = float(f"{current_section['id']}.{len(current_section['subsections']) + 1}")
                current_section["subsections"].append({
                    "id": subsection_id,
                    "title": line[2:].strip()
                })
        
        if current_section:
            sections.append(current_section)
        
        return {"title": fallback_title, "sections": sections}
