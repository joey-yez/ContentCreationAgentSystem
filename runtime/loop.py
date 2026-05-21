from typing import Dict, Any, Optional
from runtime.state_manager import StateManager, ArticlePhase, ArticleState, Section
from runtime.context import Context
from runtime.planner import Planner
from agents.outline_agent import OutlineAgent
from agents.writer_agent import WriterAgent
from tools.markdown_export import MarkdownExportTool
from tools.file_storage import FileStorageTool
import uuid

class RuntimeLoop:
    def __init__(self):
        self.state_manager = StateManager()
        self.planner = Planner()
        self.outline_agent = OutlineAgent()
        self.writer_agent = WriterAgent()
        self.export_tool = MarkdownExportTool()
        self.storage_tool = FileStorageTool()
    
    def create_task(self, topic: str, style: Optional[str] = None, 
                    audience: Optional[str] = None, 
                    estimated_words: Optional[int] = None) -> str:
        task_id = f"article_{uuid.uuid4().hex[:8]}"
        state = ArticleState(
            task_id=task_id,
            topic=topic,
            style=style,
            audience=audience,
            estimated_words=estimated_words,
            phase=ArticlePhase.CREATED
        )
        self.state_manager.save_state(state)
        return task_id
    
    def run(self, task_id: str) -> Dict[str, Any]:
        state = self.state_manager.load_state(task_id)
        if not state:
            return {"error": "Task not found"}
        
        while not self.planner.is_final_phase(state.phase):
            if self.planner.needs_user_input(state.phase):
                return {
                    "status": "waiting_user_input",
                    "phase": state.phase.value,
                    "task_id": task_id,
                    "state": state.dict()
                }
            
            if state.phase == ArticlePhase.CREATED:
                self._process_created(state)
            elif state.phase == ArticlePhase.UNDERSTANDING_TOPIC:
                self._process_understanding_topic(state)
            elif state.phase == ArticlePhase.OUTLINE_GENERATED:
                self._process_outline_generated(state)
            elif state.phase == ArticlePhase.DRAFTING:
                self._process_drafting(state)
            elif state.phase == ArticlePhase.WAITING_REVIEW:
                pass
            elif state.phase == ArticlePhase.READY_TO_EXPORT:
                self._process_ready_to_export(state)
            
            self.state_manager.save_state(state)
        
        return {
            "status": "completed",
            "task_id": task_id,
            "state": state.dict()
        }
    
    def _process_created(self, state: ArticleState) -> None:
        state.phase = ArticlePhase.UNDERSTANDING_TOPIC
    
    def _process_understanding_topic(self, state: ArticleState) -> None:
        outline_result = self.outline_agent.generate_outline(
            topic=state.topic,
            style=state.style,
            audience=state.audience,
            estimated_words=state.estimated_words
        )
        
        state.metadata["title"] = outline_result.get("title", state.topic)
        
        for section_data in outline_result.get("sections", []):
            section = Section(
                id=int(section_data["id"]),
                title=section_data.get("title", ""),
                summary=section_data.get("summary", "")
            )
            state.sections.append(section)
        
        state.phase = ArticlePhase.OUTLINE_GENERATED
    
    def _process_outline_generated(self, state: ArticleState) -> None:
        state.phase = ArticlePhase.WAITING_USER_APPROVAL
    
    def _process_drafting(self, state: ArticleState) -> None:
        pending_sections = [s for s in state.sections if not s.completed]
        
        if not pending_sections:
            state.phase = ArticlePhase.WAITING_REVIEW
            return
        
        current_section = pending_sections[0]
        
        previous_sections_summary = "\n".join([
            f"章节 {s.id}: {s.title} - {s.summary}" 
            for s in state.sections 
            if s.completed and s.id < current_section.id
        ])
        
        result = self.writer_agent.write_section(
            topic=state.topic,
            section_title=current_section.title,
            section_summary=current_section.summary or "",
            previous_sections=previous_sections_summary,
            style=state.style,
            audience=state.audience
        )
        
        self.state_manager.update_section(
            task_id=state.task_id,
            section_id=current_section.id,
            content=result.get("content", ""),
            summary=result.get("summary", "")
        )
        
        updated_state = self.state_manager.load_state(state.task_id)
        if updated_state:
            state.sections = updated_state.sections
            state.current_section = updated_state.current_section
    
    def _process_ready_to_export(self, state: ArticleState) -> None:
        sections_data = [
            {"title": s.title, "content": s.content or ""}
            for s in state.sections
        ]
        
        export_path = self.export_tool.export(
            title=state.metadata.get("title", state.topic),
            sections=sections_data,
            task_id=state.task_id
        )
        
        state.metadata["export_path"] = export_path
        state.phase = ArticlePhase.EXPORTED
    
    def approve_outline(self, task_id: str) -> None:
        state = self.state_manager.load_state(task_id)
        if state and state.phase == ArticlePhase.WAITING_USER_APPROVAL:
            state.phase = ArticlePhase.DRAFTING
            self.state_manager.save_state(state)
    
    def request_revision(self, task_id: str, section_id: int, feedback: str) -> None:
        state = self.state_manager.load_state(task_id)
        if state:
            self.state_manager.add_feedback(task_id, feedback)
            state.phase = ArticlePhase.REVISING
            
            for section in state.sections:
                if section.id == section_id:
                    result = self.writer_agent.rewrite_section(
                        topic=state.topic,
                        section_title=section.title,
                        current_content=section.content or "",
                        feedback=feedback,
                        style=state.style,
                        audience=state.audience
                    )
                    self.state_manager.update_section(
                        task_id=task_id,
                        section_id=section_id,
                        content=result.get("content", ""),
                        summary=result.get("summary", "")
                    )
                    break
            
            state.phase = ArticlePhase.WAITING_REVIEW
            self.state_manager.save_state(state)
    
    def get_state(self, task_id: str) -> Optional[ArticleState]:
        return self.state_manager.load_state(task_id)
