"""
Workflow state management for Injection Sentinel
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


@dataclass
class WorkflowState:
    """
    Central state object passed between skills.
    OpenSwarm orchestrator maintains this state.
    """
    
    # Input
    repository_path: str
    
    # Scan results
    scanned_files: List[Any] = field(default_factory=list)
    prompt_constructions: List[Any] = field(default_factory=list)
    tool_calls: List[Any] = field(default_factory=list)
    
    # Trace results
    taint_flows: List[Any] = field(default_factory=list)
    vulnerabilities: List[Any] = field(default_factory=list)
    
    # Red team results
    payloads: List[Any] = field(default_factory=list)
    validated_exploits: List[Any] = field(default_factory=list)
    
    # Fix results
    patches: List[Any] = field(default_factory=list)
    fixed_files: List[str] = field(default_factory=list)
    
    # Report results
    discord_markdown: str = ""
    discord_embeds: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    current_step: str = "initialized"
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "repository_path": self.repository_path,
            "scanned_files": self.scanned_files,
            "prompt_constructions": self.prompt_constructions,
            "tool_calls": self.tool_calls,
            "taint_flows": self.taint_flows,
            "vulnerabilities": self.vulnerabilities,
            "payloads": self.payloads,
            "validated_exploits": self.validated_exploits,
            "patches": self.patches,
            "fixed_files": self.fixed_files,
            "discord_markdown": self.discord_markdown,
            "discord_embeds": self.discord_embeds,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "current_step": self.current_step,
            "errors": self.errors,
        }
    
    def to_json(self) -> str:
        """Convert state to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def add_error(self, error: str):
        """Add error to state"""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")
    
    def mark_complete(self):
        """Mark workflow as complete"""
        self.completed_at = datetime.utcnow().isoformat()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get workflow summary"""
        return {
            "repository": self.repository_path,
            "files_scanned": len(self.scanned_files),
            "vulnerabilities_found": len(self.vulnerabilities),
            "payloads_generated": len(self.payloads),
            "patches_created": len(self.patches),
            "current_step": self.current_step,
            "has_errors": len(self.errors) > 0,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }
