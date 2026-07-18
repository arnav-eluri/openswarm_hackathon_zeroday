"""
Data models for Injection Sentinel
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FileInfo:
    """Represents a discovered file in the repository"""
    path: str
    language: str
    size: int
    has_llm_code: bool
    has_user_input: bool
    has_prompts: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PromptConstruction:
    """Represents a prompt construction site"""
    file_path: str
    line_number: int
    code_snippet: str
    method: str  # f-string, concatenation, template, etc.
    variables: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaintFlow:
    """Represents a taint flow from source to sink"""
    source: str
    source_file: str
    source_line: int
    sink: str
    sink_file: str
    sink_line: int
    path: List[str]
    confidence: str
    evidence: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RedTeamPayload:
    """Represents a red team attack payload"""
    name: str
    payload: str
    expected_effect: str
    risk: str
    target_sink: str
    validation_result: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VulnerabilityFix:
    """Represents a security patch"""
    vulnerability_id: str
    file_path: str
    original_code: str
    fixed_code: str
    reason: str
    technique: str  # delimiter, escape, template, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    """Result from repository scan"""
    status: str
    summary: str
    repository_path: str
    files: List[FileInfo]
    prompts: List[PromptConstruction]
    tool_calls: List[Dict[str, Any]]
    next_action: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "repository_path": self.repository_path,
            "files": [f.to_dict() for f in self.files],
            "prompts": [p.to_dict() for p in self.prompts],
            "tool_calls": self.tool_calls,
            "next_action": self.next_action,
            "data": self.data
        }


@dataclass
class TraceResult:
    """Result from taint analysis"""
    status: str
    summary: str
    flows: List[TaintFlow]
    vulnerability_count: int
    next_action: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "flows": [f.to_dict() for f in self.flows],
            "vulnerability_count": self.vulnerability_count,
            "next_action": self.next_action,
            "data": self.data
        }


@dataclass
class RedTeamResult:
    """Result from red team analysis"""
    status: str
    summary: str
    payloads: List[RedTeamPayload]
    validated_count: int
    next_action: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "payloads": [p.to_dict() for p in self.payloads],
            "validated_count": self.validated_count,
            "next_action": self.next_action,
            "data": self.data
        }


@dataclass
class FixResult:
    """Result from vulnerability fixing"""
    status: str
    summary: str
    fixes: List[VulnerabilityFix]
    files_changed: int
    next_action: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "fixes": [f.to_dict() for f in self.fixes],
            "files_changed": self.files_changed,
            "next_action": self.next_action,
            "data": self.data
        }


@dataclass
class ReportResult:
    """Result from Discord report generation"""
    status: str
    summary: str
    markdown: str
    embeds: List[Dict[str, Any]]
    critical_count: int
    next_action: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "markdown": self.markdown,
            "embeds": self.embeds,
            "critical_count": self.critical_count,
            "next_action": self.next_action,
            "data": self.data
        }
