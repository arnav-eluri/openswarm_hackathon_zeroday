import json
from typing import Dict, Any

class PipelineState:
    def __init__(self):
        self.data = {
            "repository_path": "",
            "scan_results": {},
            "flows": [],
            "payloads": [],
            "fixes": [],
            "verification_results": []
        }
        
    def update(self, key: str, value: Any):
        self.data[key] = value
        
    def get(self, key: str, default=None) -> Any:
        return self.data.get(key, default)
        
    def get_all(self) -> Dict[str, Any]:
        return self.data
        
    def to_json(self) -> str:
        return json.dumps(self.data, indent=2)
        
    def from_json(self, json_str: str):
        self.data = json.loads(json_str)

# Singleton instance for the workflow
state = PipelineState()
