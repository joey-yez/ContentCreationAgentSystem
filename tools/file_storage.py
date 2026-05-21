from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime

class FileStorageTool:
    def __init__(self, storage_dir: str = "storage/articles"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_draft(self, task_id: str, data: Dict[str, Any]) -> str:
        file_path = os.path.join(self.storage_dir, f"{task_id}_draft.json")
        data["saved_at"] = datetime.now().isoformat()
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_draft(self, task_id: str) -> Optional[Dict[str, Any]]:
        file_path = os.path.join(self.storage_dir, f"{task_id}_draft.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_drafts(self) -> List[Dict[str, Any]]:
        drafts = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith("_draft.json"):
                task_id = filename.replace("_draft.json", "")
                file_path = os.path.join(self.storage_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    drafts.append({
                        "task_id": task_id,
                        "title": data.get("title", "Untitled"),
                        "saved_at": data.get("saved_at", "")
                    })
        
        return sorted(drafts, key=lambda x: x["saved_at"], reverse=True)
    
    def delete_draft(self, task_id: str) -> bool:
        file_path = os.path.join(self.storage_dir, f"{task_id}_draft.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
