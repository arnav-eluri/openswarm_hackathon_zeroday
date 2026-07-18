import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class VulnerabilityFlow:
    source: str
    sink: str
    source_file: str
    source_line: int
    sink_file: str
    sink_line: int
    confidence: str # high, medium, low
    risk: str # critical, high, medium, low

    def to_dict(self):
        return asdict(self)

@dataclass
class PayloadTest:
    name: str
    payload_text: str
    target_sink: str
    risk: str
    validation_result: str # exploitable, likely, uncertain, blocked

    def to_dict(self):
        return asdict(self)

@dataclass
class VulnerabilityFix:
    vulnerability_id: str
    file_path: str
    original_code: str
    fixed_code: str
    reason: str
    technique: str # delimiter, escape, template, validation, isolation

    def to_dict(self):
        return asdict(self)

@dataclass
class ScanResult:
    status: str
    summary: str
    data: Dict[str, Any]
    next_action: str

    def to_dict(self):
        return asdict(self)

def obj_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return obj
