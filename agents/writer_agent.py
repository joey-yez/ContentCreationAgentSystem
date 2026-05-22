from typing import Optional, Dict, Any, Tuple
from llm_client import LLMClient, LLMResult
import json

DEBUG = False

class WriterAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def write_section(self, topic: str, section_title: str, 
                      section_summary: str, previous_sections: str = "",
                      style: Optional[str] = None, 
                      audience: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, float]]:
        style_text = f"写作风格：{style}" if style else ""
        audience_text = f"目标读者：{audience}" if audience else ""
        
        context_prompt = f"""
之前章节内容摘要：
{previous_sections}
""" if previous_sections else ""
        
        prompt = f"""
你是一位专业的内容写作者。请根据以下信息撰写文章的一个章节：

文章主题：{topic}
{style_text}
{audience_text}

当前章节：
标题：{section_title}
摘要：{section_summary}

{context_prompt}

请输出：
1. 当前章节的完整内容（Markdown 格式）
2. 当前章节的简短摘要

输出格式要求：
- 使用 JSON 格式输出，但是开头结尾不要带上代码块标记
- 包含 "content" (字符串，Markdown 格式) 和 "summary" (字符串)
- 章节按照 2 级标题格式输出（## 章节标题），章节内部的段落按照 3 级标题或普通段落格式输出

注意：
- 内容要详实、有深度
- 保持与上下文的连贯性
- 使用适当的 Markdown 格式（标题、列表等）
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的技术写作者，擅长撰写深度分析文章。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.8)
        
        try:
            result = json.loads(llm_result.content)
            if DEBUG:
                print(f"✓ JSON 解析成功")
        except Exception as e:
            if DEBUG:
                print(f"✗ JSON 解析失败: {str(e)}")
                print(f"使用原始内容作为 fallback")
            result = {
                "content": llm_result.content,
                "summary": section_summary
            }
        
        metrics = {
            "duration": llm_result.duration,
            "prompt_tokens": llm_result.prompt_tokens,
            "completion_tokens": llm_result.completion_tokens,
            "total_tokens": llm_result.total_tokens
        }
        
        return result, metrics
    
    def rewrite_section(self, topic: str, section_title: str, 
                        current_content: str, feedback: str,
                        style: Optional[str] = None,
                        audience: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, float]]:
        style_text = f"写作风格：{style}" if style else ""
        audience_text = f"目标读者：{audience}" if audience else ""
        
        prompt = f"""
你是一位专业的内容编辑。请根据用户反馈修改以下章节内容：

文章主题：{topic}
{style_text}
{audience_text}

当前章节：
标题：{section_title}

当前内容：
{current_content}

用户反馈：
{feedback}

请输出修改后的内容：
- 使用 JSON 格式输出，但是开头结尾不要带上代码块标记
- 包含 "content" (字符串，Markdown 格式) 和 "summary" (字符串)
- 章节按照 2 级标题格式输出（## 章节标题），章节内部的段落按照 3 级标题或普通段落格式输出
- 只修改需要调整的部分，保持其他内容不变
- 保持与上下文的连贯性
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的内容编辑，擅长根据用户反馈修改文章。"},
            {"role": "user", "content": prompt}
        ]
        
        llm_result: LLMResult = self.llm.chat(messages, temperature=0.7)
        
        try:
            result = json.loads(llm_result.content)
            if DEBUG:
                print(f"✓ JSON 解析成功")
        except Exception as e:
            if DEBUG:
                print(f"✗ JSON 解析失败: {str(e)}")
                print(f"使用原始内容作为 fallback")
            result = {
                "content": llm_result.content,
                "summary": ""
            }
        
        metrics = {
            "duration": llm_result.duration,
            "prompt_tokens": llm_result.prompt_tokens,
            "completion_tokens": llm_result.completion_tokens,
            "total_tokens": llm_result.total_tokens
        }
        
        return result, metrics
