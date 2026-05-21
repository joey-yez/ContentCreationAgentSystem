from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
import os

class ArticlePhase(str, Enum):
    CREATED = "CREATED"
    UNDERSTANDING_TOPIC = "UNDERSTANDING_TOPIC"
    RESEARCHING = "RESEARCHING"
    OUTLINE_GENERATED = "OUTLINE_GENERATED"
    WAITING_USER_APPROVAL = "WAITING_USER_APPROVAL"
    DRAFTING = "DRAFTING"
    WAITING_REVIEW = "WAITING_REVIEW"
    REVISING = "REVISING"
    READY_TO_EXPORT = "READY_TO_EXPORT"
    EXPORTED = "EXPORTED"
    PUBLISHED = "PUBLISHED"

class Section(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    completed: bool = False

class ArticleState(BaseModel):
    task_id: str
    topic: str
    style: Optional[str] = None
    audience: Optional[str] = None
    estimated_words: Optional[int] = None
    phase: ArticlePhase = ArticlePhase.CREATED
    current_section: int = 0
    sections: List[Section] = []
    draft_version: int = 1
    last_updated: datetime = datetime.now()
    user_feedback: List[str] = []
    metadata: Dict[str, Any] = {}

class StateManager:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_state(self, state: ArticleState) -> None:
        file_path = os.path.join(self.storage_path, f"{state.task_id}.json")
        state.last_updated = datetime.now()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state.dict(), f, default=str, ensure_ascii=False, indent=2)
    
    def load_state(self, task_id: str) -> Optional[ArticleState]:
        file_path = os.path.join(self.storage_path, f"{task_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])
            data["phase"] = ArticlePhase(data["phase"])
            data["sections"] = [Section(**s) for s in data["sections"]]
            return ArticleState(**data)
    
    def update_phase(self, task_id: str, new_phase: ArticlePhase) -> None:
        state = self.load_state(task_id)
        if state:
            state.phase = new_phase
            state.last_updated = datetime.now()
            self.save_state(state)
    
    def add_section(self, task_id: str, section: Section) -> None:
        state = self.load_state(task_id)
        if state:
            state.sections.append(section)
            state.last_updated = datetime.now()
            self.save_state(state)
    
    def update_section(self, task_id: str, section_id: int, content: str, summary: Optional[str] = None) -> None:
        state = self.load_state(task_id)
        if state:
            for section in state.sections:
                if section.id == section_id:
                    section.content = content
                    if summary:
                        section.summary = summary
                    section.completed = True
                    state.current_section = section_id
                    state.last_updated = datetime.now()
                    break
            self.save_state(state)
    
    def add_feedback(self, task_id: str, feedback: str) -> None:
        state = self.load_state(task_id)
        if state:
            state.user_feedback.append(feedback)
            state.last_updated = datetime.now()
            self.save_state(state)
    
    def increment_version(self, task_id: str) -> None:
        state = self.load_state(task_id)
        if state:
            state.draft_version += 1
            state.last_updated = datetime.now()
            self.save_state(state)
