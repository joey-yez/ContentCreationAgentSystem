from typing import List, Dict, Any
import os
from datetime import datetime

class MarkdownExportTool:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export(self, title: str, sections: List[Dict[str, Any]], 
               task_id: str = None) -> str:
        lines = []
        
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for idx, section in enumerate(sections, 1):
            section_title = section.get("title", "")
            content = section.get("content", "")
            
#            lines.append(f"## {idx}. {section_title}")
#            lines.append("")
            
            if content:
                processed_content = self._process_content(content)
                lines.append(processed_content)
            else:
                lines.append("*（内容待补充）*")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        if lines and lines[-1] == "---\n":
            lines.pop()
        if lines and lines[-1] == "":
            lines.pop()
        
        markdown_content = "\n".join(lines)
        
        if task_id:
            filename = f"{task_id}.md"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.md"
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return file_path
    
    def _process_content(self, content: str) -> str:
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                processed_lines.append("")
                continue
            
            if line.startswith('## ') or line.startswith('### ') or line.startswith('# '):
                processed_lines.append(line)
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('+ '):
                processed_lines.append(f"  {line}")
            elif line.startswith('1. ') or line.startswith('1) ') or line.startswith('(1) '):
                processed_lines.append(f"  {line}")
            elif line.startswith('> '):
                processed_lines.append(f"> {line[2:]}")
            elif line.startswith('```'):
                processed_lines.append(line)
            elif line.startswith('|'):
                processed_lines.append(line)
            elif len(line) > 50 and not line.startswith((' ', '\t', '#', '-', '*', '+', '>', '|', '`')):
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return "\n".join(processed_lines)
    
    def preview(self, title: str, sections: List[Dict[str, Any]]) -> str:
        lines = []
        
        lines.append(f"# {title}")
        lines.append("")
        
        for i, section in enumerate(sections, 1):
            section_title = section.get("title", "")
            content = section.get("content", "")[:200] if section.get("content") else ""
            
            lines.append(f"## {i}. {section_title}")
            lines.append("")
            if content:
                lines.append(f"{content}...")
            else:
                lines.append("(未生成)")
            lines.append("")
        
        return "\n".join(lines)
