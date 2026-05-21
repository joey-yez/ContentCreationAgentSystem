from typing import List, Dict, Any, Optional
from datetime import datetime

class Context:
    def __init__(self):
        self.system_prompt = ""
        self.user_input = {}
        self.historical_sections = []
        self.tool_results = []
        self.user_feedback = []
        self.current_step = 0
        self.task_id = ""
    
    def add_system_prompt(self, prompt: str) -> None:
        self.system_prompt = prompt
    
    def add_user_input(self, input_data: Dict[str, Any]) -> None:
        self.user_input.update(input_data)
    
    def add_historical_section(self, section: Dict[str, Any]) -> None:
        self.historical_sections.append(section)
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        self.tool_results.append({
            "tool_name": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_feedback(self, feedback: str) -> None:
        self.user_feedback.append(feedback)
    
    def increment_step(self) -> None:
        self.current_step += 1
    
    def set_task_id(self, task_id: str) -> None:
        self.task_id = task_id
    
    def assemble(self) -> str:
        context_parts = []
        
        if self.system_prompt:
            context_parts.append(f"【系统指令】\n{self.system_prompt}\n")
        
        if self.user_input:
            user_input_str = "\n".join([f"- {k}: {v}" for k, v in self.user_input.items()])
            context_parts.append(f"【用户输入】\n{user_input_str}\n")
        
        if self.historical_sections:
            sections_str = "\n".join([f"章节 {s.get('id')}: {s.get('title')} - {s.get('summary', '')}" for s in self.historical_sections])
            context_parts.append(f"【历史章节】\n{sections_str}\n")
        
        if self.tool_results:
            tools_str = "\n".join([f"- {t['tool_name']}: {str(t['result'])[:100]}..." for t in self.tool_results])
            context_parts.append(f"【工具结果】\n{tools_str}\n")
        
        if self.user_feedback:
            feedback_str = "\n".join([f"- {f}" for f in self.user_feedback])
            context_parts.append(f"【用户反馈】\n{feedback_str}\n")
        
        context_parts.append(f"【当前步骤】\n第 {self.current_step} 步\n")
        
        return "\n".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "current_step": self.current_step,
            "system_prompt": self.system_prompt,
            "user_input": self.user_input,
            "historical_sections": self.historical_sections,
            "tool_results": self.tool_results,
            "user_feedback": self.user_feedback
        }
