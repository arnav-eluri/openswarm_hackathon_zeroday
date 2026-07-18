import ast
import os
from typing import List, Dict, Any

def walk_repository(repo_path: str) -> List[str]:
    """Returns a list of all python files in the given directory."""
    py_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def parse_file(filepath: str) -> ast.AST:
    """Parses a Python file into an AST."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return ast.parse(f.read(), filename=filepath)

def find_llm_sinks(tree: ast.AST) -> List[ast.Call]:
    """Finds common LLM invocation calls (sinks)."""
    sinks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['invoke', 'create', 'generate', 'chat']:
                    sinks.append(node)
            elif isinstance(node.func, ast.Name):
                if 'llm' in node.func.id.lower() or 'invoke' in node.func.id.lower():
                    sinks.append(node)
    return sinks

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
