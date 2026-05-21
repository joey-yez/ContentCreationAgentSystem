from typing import List, Dict, Any
import os
from datetime import datetime

class MarkdownExportTool:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export(self, title: str, sections: List[Dict[str, Any]], 
               task_id: str = None) -> str:
        markdown_content = f"# {title}\n\n"
        
        for section in sections:
            section_title = section.get("title", "")
            content = section.get("content", "")
            markdown_content += f"## {section_title}\n\n"
            markdown_content += f"{content}\n\n"
        
        if task_id:
            filename = f"{task_id}.md"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.md"
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return file_path
    
    def preview(self, title: str, sections: List[Dict[str, Any]]) -> str:
        preview_content = f"# {title}\n\n"
        
        for i, section in enumerate(sections, 1):
            section_title = section.get("title", "")
            content = section.get("content", "")[:200] if section.get("content") else ""
            preview_content += f"## {i}. {section_title}\n\n"
            if content:
                preview_content += f"{content}...\n\n"
            else:
                preview_content += "(未生成)\n\n"
        
        return preview_content
