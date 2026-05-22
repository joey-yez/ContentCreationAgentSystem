from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class LLMCallRecord:
    def __init__(self, phase: str, call_type: str, duration: float, 
                 prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.phase = phase
        self.call_type = call_type
        self.duration = duration
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "call_type": self.call_type,
            "duration": self.duration,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp.isoformat()
        }

class Evaluation:
    def __init__(self, task_id: str, storage_path: str = "storage"):
        self.task_id = task_id
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.data = {
            "task_id": task_id,
            "outline_generation_count": 0,
            "article_section_count": 0,
            "revision_count": 0,
            "llm_calls": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_duration": 0.0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "outline_evaluation": None,
            "article_evaluation": None
        }
    
    def record_outline_generation(self, duration: float, prompt_tokens: int = 0, 
                                  completion_tokens: int = 0, total_tokens: int = 0) -> None:
        self.data["outline_generation_count"] += 1
        self._add_llm_call("OUTLINE_GENERATION", "outline", duration, 
                          prompt_tokens, completion_tokens, total_tokens)
    
    def record_article_section(self, duration: float, prompt_tokens: int = 0, 
                               completion_tokens: int = 0, total_tokens: int = 0) -> None:
        self.data["article_section_count"] += 1
        self._add_llm_call("DRAFTING", "article_section", duration, 
                          prompt_tokens, completion_tokens, total_tokens)
    
    def record_revision(self, phase: str, duration: float, prompt_tokens: int = 0, 
                        completion_tokens: int = 0, total_tokens: int = 0) -> None:
        self.data["revision_count"] += 1
        self._add_llm_call(phase, "revision", duration, 
                          prompt_tokens, completion_tokens, total_tokens)
    
    def record_outline_evaluation(self, score: float, feedback: str, criteria: List[Dict[str, Any]]) -> None:
        self.data["outline_evaluation"] = {
            "score": score,
            "feedback": feedback,
            "criteria": criteria,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_article_evaluation(self, score: float, feedback: str, criteria: List[Dict[str, Any]]) -> None:
        self.data["article_evaluation"] = {
            "score": score,
            "feedback": feedback,
            "criteria": criteria,
            "timestamp": datetime.now().isoformat()
        }
    
    def _add_llm_call(self, phase: str, call_type: str, duration: float,
                      prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
        record = LLMCallRecord(
            phase=phase,
            call_type=call_type,
            duration=duration,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
        self.data["llm_calls"].append(record.to_dict())
        
        self.data["total_duration"] += duration
        self.data["total_prompt_tokens"] += prompt_tokens
        self.data["total_completion_tokens"] += completion_tokens
        self.data["total_tokens"] += total_tokens
    
    def finish(self) -> None:
        self.data["end_time"] = datetime.now().isoformat()
        self.save()
    
    def save(self) -> None:
        file_path = os.path.join(self.storage_path, f"{self.task_id}_evaluation.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, task_id: str, storage_path: str = "storage") -> Optional['Evaluation']:
        file_path = os.path.join(storage_path, f"{task_id}_evaluation.json")
        if not os.path.exists(file_path):
            return None
        
        evaluation = cls(task_id, storage_path)
        with open(file_path, "r", encoding="utf-8") as f:
            evaluation.data = json.load(f)
        return evaluation
    
    def get_summary(self) -> str:
        summary = []
        summary.append(f"┌─────────────────────────────────────────────────────┐")
        summary.append(f"│              Task Evaluation Summary                │")
        summary.append(f"├─────────────────────────────────────────────────────┤")
        summary.append(f"│ Task ID: {self.task_id}")
        summary.append(f"├─────────────────────────────────────────────────────┤")
        summary.append(f"│ Generation Counts:")
        summary.append(f"│   - Outline Generations: {self.data['outline_generation_count']}")
        summary.append(f"│   - Article Sections: {self.data['article_section_count']}")
        summary.append(f"│   - Revisions: {self.data['revision_count']}")
        summary.append(f"├─────────────────────────────────────────────────────┤")
        summary.append(f"│ LLM Token Usage:")
        summary.append(f"│   - Prompt Tokens: {self.data['total_prompt_tokens']:,}")
        summary.append(f"│   - Completion Tokens: {self.data['total_completion_tokens']:,}")
        summary.append(f"│   - Total Tokens: {self.data['total_tokens']:,}")
        summary.append(f"├─────────────────────────────────────────────────────┤")
        summary.append(f"│ Duration:")
        summary.append(f"│   - Total Time: {self.data['total_duration']:.2f} seconds")
        
        avg_duration = self.data['total_duration'] / len(self.data['llm_calls']) if self.data['llm_calls'] else 0
        summary.append(f"│   - Avg per Call: {avg_duration:.2f} seconds")
        
        if self.data['outline_evaluation']:
            outline_eval = self.data['outline_evaluation']
            summary.append(f"├─────────────────────────────────────────────────────┤")
            summary.append(f"│ Outline Evaluation:")
            summary.append(f"│   - Score: {outline_eval['score']}/10")
            summary.append(f"│   - Feedback: {outline_eval['feedback'][:50]}...")
        
        if self.data['article_evaluation']:
            article_eval = self.data['article_evaluation']
            summary.append(f"├─────────────────────────────────────────────────────┤")
            summary.append(f"│ Article Evaluation:")
            summary.append(f"│   - Score: {article_eval['score']}/10")
            summary.append(f"│   - Feedback: {article_eval['feedback'][:50]}...")
        
        summary.append(f"└─────────────────────────────────────────────────────┘")
        
        return "\n".join(summary)
    
    def get_detailed_report(self) -> str:
        report = [self.get_summary()]
        report.append("\n┌─────────────────────────────────────────────────────┐")
        report.append("│           LLM Call Detailed Breakdown              │")
        report.append("├─────────────┬───────────┬─────────┬───────────────┤")
        report.append("│    Phase    │   Type    │ Tokens  │   Duration    │")
        report.append("├─────────────┼───────────┼─────────┼───────────────┤")
        
        for call in self.data["llm_calls"]:
            phase = call["phase"].ljust(11)[:11]
            call_type = call["call_type"].ljust(9)[:9]
            tokens = f"{call['total_tokens']:,}".rjust(7)
            duration = f"{call['duration']:.2f}s".rjust(13)
            report.append(f"│ {phase} │ {call_type} │ {tokens} │ {duration} │")
        
        report.append("└─────────────┴───────────┴─────────┴───────────────┘")
        
        if self.data['outline_evaluation']:
            report.append("\n┌─────────────────────────────────────────────────────┐")
            report.append("│          Outline Evaluation Details                 │")
            report.append("├─────────────────────────────────────────────────────┤")
            outline_eval = self.data['outline_evaluation']
            report.append(f"│ Score: {outline_eval['score']}/10")
            report.append(f"├─────────────────────────────────────────────────────┤")
            report.append(f"│ Feedback:")
            feedback_lines = outline_eval['feedback'].split('\n')
            for line in feedback_lines:
                report.append(f"│   {line}")
            if outline_eval['criteria']:
                report.append(f"├─────────────────────────────────────────────────────┤")
                report.append(f"│ Criteria:")
                for crit in outline_eval['criteria']:
                    report.append(f"│   {crit['name']}: {crit['score']}/10")
            report.append("└─────────────────────────────────────────────────────┘")
        
        if self.data['article_evaluation']:
            report.append("\n┌─────────────────────────────────────────────────────┐")
            report.append("│          Article Evaluation Details                 │")
            report.append("├─────────────────────────────────────────────────────┤")
            article_eval = self.data['article_evaluation']
            report.append(f"│ Score: {article_eval['score']}/10")
            report.append(f"├─────────────────────────────────────────────────────┤")
            report.append(f"│ Feedback:")
            feedback_lines = article_eval['feedback'].split('\n')
            for line in feedback_lines:
                report.append(f"│   {line}")
            if article_eval['criteria']:
                report.append(f"├─────────────────────────────────────────────────────┤")
                report.append(f"│ Criteria:")
                for crit in article_eval['criteria']:
                    report.append(f"│   {crit['name']}: {crit['score']}/10")
            report.append("└─────────────────────────────────────────────────────┘")
        
        return "\n".join(report)
    
    def __repr__(self) -> str:
        return f"Evaluation(task_id={self.task_id}, llm_calls={len(self.data['llm_calls'])})"
