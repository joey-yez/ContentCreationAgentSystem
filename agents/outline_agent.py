from typing import List, Optional, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OutlineAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")
    
    def generate_outline(self, topic: str, style: Optional[str] = None, 
                         audience: Optional[str] = None, 
                         estimated_words: Optional[int] = None) -> Dict[str, Any]:
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
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位专业的内容策划师和编辑，擅长为各种主题生成结构化的文章大纲。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return self._parse_fallback(response.choices[0].message.content)
    
    def _parse_fallback(self, content: str) -> Dict[str, Any]:
        lines = content.strip().split('\n')
        sections = []
        current_section = None
        section_id = 1
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                return {"title": title, "sections": []}
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
        
        return {"title": topic, "sections": sections} if sections else {"title": topic, "sections": []}
