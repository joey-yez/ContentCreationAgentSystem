from typing import Dict, Any, Optional
from runtime.state_manager import StateManager, ArticlePhase, ArticleState, Section
from runtime.context import Context
from runtime.planner import Planner
from agents.outline_agent import OutlineAgent
from agents.writer_agent import WriterAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.feedback_analyzer import FeedbackAnalyzer
from tools.markdown_export import MarkdownExportTool
from tools.file_storage import FileStorageTool
from memory.memory_store import Memory
from evaluation import Evaluation
import uuid

class RuntimeLoop:
    def __init__(self):
        self.state_manager = StateManager()
        self.planner = Planner()
        self.outline_agent = OutlineAgent()
        self.writer_agent = WriterAgent()
        self.evaluator_agent = EvaluatorAgent()
        self.feedback_analyzer = FeedbackAnalyzer()
        self.export_tool = MarkdownExportTool()
        self.storage_tool = FileStorageTool()
    
    def create_task(self, topic: str, style: Optional[str] = None, 
                    audience: Optional[str] = None, 
                    estimated_words: Optional[int] = None,
                    estimated_sections: Optional[int] = None) -> str:
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
        
        memory = Memory(task_id)
        memory.store_initial_input(
            topic=topic,
            style=style,
            audience=audience,
            estimated_words=estimated_words,
            estimated_sections=estimated_sections
        )
        memory.save()
        
        evaluation = Evaluation(task_id)
        evaluation.save()
        
        return task_id
    
    def run(self, task_id: str) -> Dict[str, Any]:
        state = self.state_manager.load_state(task_id)
        evaluation = Evaluation.load(task_id)
        if not state:
            return {"error": "Task not found"}
        
        while not self.planner.is_final_phase(state.phase):
            if self.planner.needs_user_input(state.phase):
                return {
                    "status": "waiting_user_input",
                    "phase": state.phase.value,
                    "task_id": task_id,
                    "state": state.model_dump()
                }
            
            if state.phase == ArticlePhase.CREATED:
                self._process_created(state)
                self.state_manager.save_state(state)
            elif state.phase == ArticlePhase.UNDERSTANDING_TOPIC:
                self._process_understanding_topic(state, evaluation)
                self.state_manager.save_state(state)
                evaluation.save()
            elif state.phase == ArticlePhase.OUTLINE_GENERATED:
                self._process_outline_generated(state)
                self.state_manager.save_state(state)
            elif state.phase == ArticlePhase.DRAFTING:
                progress_info = self._process_drafting(state, evaluation)
                self.state_manager.save_state(state)
                evaluation.save()
                return {
                    "status": "drafting_progress",
                    "task_id": task_id,
                    "phase": state.phase.value,
                    "progress": progress_info,
                    "state": state.model_dump()
                }
            elif state.phase == ArticlePhase.WAITING_REVIEW:
                pass
            elif state.phase == ArticlePhase.READY_TO_EXPORT:
                self._process_ready_to_export(state, evaluation)
                self.state_manager.save_state(state)
                evaluation.save()
        
        return {
            "status": "completed",
            "task_id": task_id,
            "state": state.model_dump(),
            "evaluation": evaluation.get_summary()
        }
    
    def _process_created(self, state: ArticleState) -> None:
        state.phase = ArticlePhase.UNDERSTANDING_TOPIC
    
    def _process_understanding_topic(self, state: ArticleState, evaluation: Evaluation) -> None:
        outline_result, metrics = self.outline_agent.generate_outline(
            topic=state.topic,
            style=state.style,
            audience=state.audience,
            estimated_words=state.estimated_words
        )
        
        evaluation.record_outline_generation(
            duration=metrics["duration"],
            prompt_tokens=metrics["prompt_tokens"],
            completion_tokens=metrics["completion_tokens"],
            total_tokens=metrics["total_tokens"]
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
    
    def _process_drafting(self, state: ArticleState, evaluation: Evaluation) -> Dict[str, Any]:
        pending_sections = [s for s in state.sections if not s.completed]
        
        if not pending_sections:
            state.phase = ArticlePhase.WAITING_REVIEW
            
            completed_count = len(state.sections)
            total_count = len(state.sections)
            
            return {
                "current_section": total_count,
                "section_title": "所有章节",
                "completed_count": completed_count,
                "total_count": total_count,
                "progress_percent": 100.0
            }
        
        current_section = pending_sections[0]
        
        previous_sections_summary = "\n".join([
            f"章节 {s.id}: {s.title} - {s.summary}" 
            for s in state.sections 
            if s.completed and s.id < current_section.id
        ])
        
        result, metrics = self.writer_agent.write_section(
            topic=state.topic,
            section_title=current_section.title,
            section_summary=current_section.summary or "",
            previous_sections=previous_sections_summary,
            style=state.style,
            audience=state.audience
        )
        
        evaluation.record_article_section(
            duration=metrics["duration"],
            prompt_tokens=metrics["prompt_tokens"],
            completion_tokens=metrics["completion_tokens"],
            total_tokens=metrics["total_tokens"]
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
        
        completed_count = sum(1 for s in state.sections if s.completed)
        total_count = len(state.sections)
        
        return {
            "current_section": current_section.id,
            "section_title": current_section.title,
            "completed_count": completed_count,
            "total_count": total_count,
            "progress_percent": (completed_count / total_count) * 100
        }
    
    def _process_ready_to_export(self, state: ArticleState, evaluation: Evaluation) -> None:
        sections_data = [
            {"title": s.title, "content": s.content or ""}
            for s in state.sections
        ]
        
        export_path = self.export_tool.export(
            title=state.metadata.get("title", state.topic),
            sections=sections_data,
            task_id=state.task_id
        )
        
        memory = Memory.load(state.task_id)
        user_requirements = memory.get_initial_input()
        
        outline_dict = {
            "title": state.metadata.get("title", state.topic),
            "sections": [
                {"id": s.id, "title": s.title, "summary": s.summary}
                for s in state.sections
            ]
        }
        
        article_content = "\n\n".join([f"## {s.title}\n\n{s.content}" for s in state.sections])
        
        article_eval_result = self.evaluator_agent.evaluate_article(
            topic=state.topic,
            outline=outline_dict,
            article_content=article_content,
            user_requirements=user_requirements
        )
        
        evaluation.record_article_evaluation(
            score=article_eval_result.score,
            feedback=article_eval_result.feedback,
            criteria=article_eval_result.criteria
        )
        
        evaluation.finish()
        
        state.metadata["export_path"] = export_path
        state.phase = ArticlePhase.EXPORTED
    
    def approve_outline(self, task_id: str) -> Dict[str, Any]:
        state = self.state_manager.load_state(task_id)
        evaluation = Evaluation.load(task_id)
        
        if not state:
            return {"error": "Task not found"}
        
        if state.phase != ArticlePhase.WAITING_USER_APPROVAL:
            return {"error": "Not in outline review phase"}
        
        memory = Memory.load(task_id)
        user_requirements = memory.get_initial_input()
        
        outline_dict = {
            "title": state.metadata.get("title", state.topic),
            "sections": [
                {"id": s.id, "title": s.title, "summary": s.summary}
                for s in state.sections
            ]
        }
        
        outline_eval_result = self.evaluator_agent.evaluate_outline(
            topic=state.topic,
            outline=outline_dict,
            user_requirements=user_requirements
        )
        
        evaluation.record_outline_evaluation(
            score=outline_eval_result.score,
            feedback=outline_eval_result.feedback,
            criteria=outline_eval_result.criteria
        )
        evaluation.save()
        
        state.phase = ArticlePhase.DRAFTING
        self.state_manager.save_state(state)
        
        return {
            "status": "outline_approved",
            "evaluation": {
                "score": outline_eval_result.score,
                "feedback": outline_eval_result.feedback,
                "criteria": outline_eval_result.criteria
            }
        }
    
    def revise_outline(self, task_id: str, feedback: str) -> Dict[str, Any]:
        state = self.state_manager.load_state(task_id)
        evaluation = Evaluation.load(task_id)
        
        if not state:
            return {"error": "Task not found"}
        
        if state.phase != ArticlePhase.WAITING_USER_APPROVAL:
            return {"error": "Not in outline review phase"}
        
        memory = Memory.load(task_id)
        memory.add_feedback("outline_review", feedback)
        
        current_requirements = memory.get_current_requirements()
        
        analysis_result = self.feedback_analyzer.analyze_and_update_memory(
            current_requirements, feedback
        )
        
        if analysis_result.get("style"):
            memory.update_style(analysis_result["style"])
        if analysis_result.get("audience"):
            memory.update_audience(analysis_result["audience"])
        if analysis_result.get("estimated_words"):
            memory.update_estimated_words(analysis_result["estimated_words"])
        if analysis_result.get("estimated_sections"):
            memory.update_estimated_sections(analysis_result["estimated_sections"])
        
        memory.save()
        
        current_outline = {
            "title": state.metadata.get("title", state.topic),
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "summary": s.summary,
                    "subsections": []
                }
                for s in state.sections
            ]
        }
        
        previous_feedback = memory.get_feedback_summary()
        updated_requirements = memory.get_current_requirements()
        
        revised_outline, metrics = self.outline_agent.revise_outline(
            topic=state.topic,
            current_outline=current_outline,
            feedback=feedback,
            previous_feedback=previous_feedback,
            style=updated_requirements.get("style") or state.style,
            audience=updated_requirements.get("audience") or state.audience
        )
        
        evaluation.record_revision(
            phase="OUTLINE_REVIEW",
            duration=metrics["duration"],
            prompt_tokens=metrics["prompt_tokens"],
            completion_tokens=metrics["completion_tokens"],
            total_tokens=metrics["total_tokens"]
        )
        evaluation.save()
        
        state.sections = []
        state.metadata["title"] = revised_outline.get("title", state.topic)
        
        for section_data in revised_outline.get("sections", []):
            section = Section(
                id=int(section_data["id"]),
                title=section_data.get("title", ""),
                summary=section_data.get("summary", "")
            )
            state.sections.append(section)
        
        self.state_manager.save_state(state)
        
        return {
            "status": "outline_revised",
            "task_id": task_id,
            "title": state.metadata["title"],
            "sections_count": len(state.sections),
            "revision_count": memory.memory["revision_count"]
        }
    
    def request_revision(self, task_id: str, section_id: int, feedback: str) -> None:
        state = self.state_manager.load_state(task_id)
        evaluation = Evaluation.load(task_id)
        
        if state:
            self.state_manager.add_feedback(task_id, feedback)
            
            memory = Memory.load(task_id)
            memory.add_feedback("draft_review", feedback)
            memory.save()
            
            state.phase = ArticlePhase.REVISING
            
            for section in state.sections:
                if section.id == section_id:
                    result, metrics = self.writer_agent.rewrite_section(
                        topic=state.topic,
                        section_title=section.title,
                        current_content=section.content or "",
                        feedback=feedback,
                        style=state.style,
                        audience=state.audience
                    )
                    
                    evaluation.record_revision(
                        phase="DRAFT_REVIEW",
                        duration=metrics["duration"],
                        prompt_tokens=metrics["prompt_tokens"],
                        completion_tokens=metrics["completion_tokens"],
                        total_tokens=metrics["total_tokens"]
                    )
                    evaluation.save()
                    
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
    
    def get_memory(self, task_id: str) -> Optional[Memory]:
        return Memory.load(task_id)
    
    def get_evaluation(self, task_id: str) -> Optional[Evaluation]:
        return Evaluation.load(task_id)
