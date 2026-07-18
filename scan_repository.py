import os
import ast
from typing import Dict, Any
from utils import walk_repository, parse_file, find_llm_sinks

def format_agent_output(agent_name: str, status: str, summary: str, severity: str, next_action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Standardizes the output of an agent."""
    return {
        "agent": agent_name,
        "status": status,
        "summary": summary,
        "severity": severity,
        "next_action": next_action,
        "data": data or {}
    }

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scans the repository for LLM usages and input patterns.
    """
    repo_path = input_data.get("repository_path", ".")
    
    try:
        py_files = walk_repository(repo_path)
        
        sinks_found = []
        templates_found = []
        
        for file in py_files:
            try:
                tree = parse_file(file)
                sinks = find_llm_sinks(tree)
                for sink in sinks:
                    sinks_found.append({
                        "file": file,
                        "line": sink.lineno,
                        "code": ast.unparse(sink)
                    })
            except Exception as e:
                pass
                
        scan_data = {
            "files_scanned": len(py_files),
            "sinks_detected": sinks_found,
            "templates_detected": templates_found
        }
        
        return format_agent_output(
            agent_name="Repository Scanner",
            status="completed",
            summary=f"Scanned {len(py_files)} files. Found {len(sinks_found)} potential sinks.",
            severity="Info",
            next_action="Prompt Injection Tracer",
            data=scan_data
        )
        
    except Exception as e:
        return format_agent_output(
            agent_name="Repository Scanner",
            status="error",
            summary=f"Scan failed: {str(e)}",
            severity="Critical",
            next_action="stop"
        )
