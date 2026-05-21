from typing import List, Dict, Any, Optional
from runtime.state_manager import ArticlePhase, ArticleState

class Planner:
    def __init__(self):
        self.phases = [
            ArticlePhase.CREATED,
            ArticlePhase.UNDERSTANDING_TOPIC,
            ArticlePhase.OUTLINE_GENERATED,
            ArticlePhase.WAITING_USER_APPROVAL,
            ArticlePhase.DRAFTING,
            ArticlePhase.WAITING_REVIEW,
            ArticlePhase.READY_TO_EXPORT,
            ArticlePhase.EXPORTED
        ]
    
    def get_next_phase(self, current_phase: ArticlePhase) -> Optional[ArticlePhase]:
        try:
            current_index = self.phases.index(current_phase)
            if current_index < len(self.phases) - 1:
                return self.phases[current_index + 1]
            return None
        except ValueError:
            return None
    
    def get_phase_steps(self, phase: ArticlePhase) -> List[str]:
        steps_map = {
            ArticlePhase.CREATED: ["初始化任务", "设置主题参数"],
            ArticlePhase.UNDERSTANDING_TOPIC: ["分析主题", "确定受众", "推荐结构"],
            ArticlePhase.OUTLINE_GENERATED: ["生成大纲", "验证大纲结构"],
            ArticlePhase.WAITING_USER_APPROVAL: ["等待用户确认", "处理用户修改"],
            ArticlePhase.DRAFTING: ["生成章节内容", "检查连贯性"],
            ArticlePhase.WAITING_REVIEW: ["等待用户审阅", "收集反馈"],
            ArticlePhase.READY_TO_EXPORT: ["准备导出", "格式检查"],
            ArticlePhase.EXPORTED: ["导出完成"]
        }
        return steps_map.get(phase, [])
    
    def create_plan(self, state: ArticleState) -> Dict[str, Any]:
        plan = {
            "task_id": state.task_id,
            "current_phase": state.phase.value,
            "next_phase": self.get_next_phase(state.phase).value if self.get_next_phase(state.phase) else None,
            "current_steps": self.get_phase_steps(state.phase),
            "completed_sections": [s.id for s in state.sections if s.completed],
            "pending_sections": [s.id for s in state.sections if not s.completed],
            "estimated_total_sections": len(state.sections)
        }
        return plan
    
    def needs_user_input(self, phase: ArticlePhase) -> bool:
        return phase in [ArticlePhase.WAITING_USER_APPROVAL, ArticlePhase.WAITING_REVIEW]
    
    def is_final_phase(self, phase: ArticlePhase) -> bool:
        return phase == ArticlePhase.EXPORTED
