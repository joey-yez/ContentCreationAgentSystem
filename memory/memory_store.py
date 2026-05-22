from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class Memory:
    def __init__(self, task_id: str, storage_path: str = "storage"):
        self.task_id = task_id
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.memory = {
            "initial_input": {},
            "user_preferences": [],
            "feedback_history": [],
            "constraints": [],
            "revision_count": 0
        }
    
    def store_initial_input(self, topic: str, style: Optional[str] = None, 
                           audience: Optional[str] = None, 
                           estimated_words: Optional[int] = None,
                           estimated_sections: Optional[int] = None) -> None:
        self.memory["initial_input"] = {
            "topic": topic,
            "style": style,
            "audience": audience,
            "estimated_words": estimated_words,
            "estimated_sections": estimated_sections,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_preference(self, key: str, value: Any) -> None:
        self.memory["user_preferences"].append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_feedback(self, phase: str, feedback: str) -> None:
        self.memory["feedback_history"].append({
            "phase": phase,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
        self.memory["revision_count"] += 1
    
    def add_constraint(self, constraint: str) -> None:
        if constraint not in self.memory["constraints"]:
            self.memory["constraints"].append(constraint)
    
    def get_constraints(self) -> List[str]:
        return self.memory["constraints"]
    
    def get_feedback_summary(self) -> str:
        summaries = []
        for feedback in self.memory["feedback_history"]:
            summaries.append(f"{feedback['phase']}: {feedback['feedback']}")
        return "\n".join(summaries)
    
    def get_all_feedback(self) -> List[Dict[str, Any]]:
        return self.memory["feedback_history"]
    
    def get_initial_input(self) -> Dict[str, Any]:
        return self.memory["initial_input"]
    
    def validate_constraints(self, new_request: Dict[str, Any]) -> List[str]:
        violations = []
        
        initial_sections = self.memory["initial_input"].get("estimated_sections")
        new_sections = new_request.get("estimated_sections")
        if initial_sections and new_sections and new_sections != initial_sections:
            violations.append(f"段落数量从 {initial_sections} 变更为 {new_sections}")
        
        initial_words = self.memory["initial_input"].get("estimated_words")
        new_words = new_request.get("estimated_words")
        if initial_words and new_words and new_words != initial_words:
            violations.append(f"字数从 {initial_words} 变更为 {new_words}")
        
        return violations
    
    def save(self) -> None:
        file_path = os.path.join(self.storage_path, f"{self.task_id}_memory.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, task_id: str, storage_path: str = "storage") -> 'Memory':
        file_path = os.path.join(storage_path, f"{task_id}_memory.json")
        memory = cls(task_id, storage_path)
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                memory.memory = json.load(f)
        
        return memory
    
    def __repr__(self) -> str:
        return f"Memory(task_id={self.task_id}, revision_count={self.memory['revision_count']})"
