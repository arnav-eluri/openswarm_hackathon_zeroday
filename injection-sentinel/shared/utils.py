"""
Utility functions for Injection Sentinel
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib


def get_file_hash(filepath: str) -> str:
    """Generate SHA256 hash of file contents"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return ""


def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get basic file information"""
    path = Path(filepath)
    return {
        "path": str(path),
        "name": path.name,
        "extension": path.suffix,
        "size": path.stat().st_size if path.exists() else 0,
        "hash": get_file_hash(filepath)
    }


def find_files_by_extension(root_path: str, extensions: List[str]) -> List[str]:
    """Recursively find files with given extensions"""
    found_files = []
    root = Path(root_path)
    
    for ext in extensions:
        found_files.extend([str(p) for p in root.rglob(f"*{ext}")])
    
    return found_files


def read_file_safe(filepath: str) -> Optional[str]:
    """Safely read file contents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return None
    except:
        return None


def parse_python_ast(code: str) -> Optional[ast.AST]:
    """Parse Python code into AST"""
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def extract_imports(tree: ast.AST) -> List[str]:
    """Extract import statements from AST"""
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return imports


def extract_function_calls(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract function calls from AST"""
    calls = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_info = {
                "line": node.lineno,
                "col": node.col_offset,
            }
            
            if isinstance(node.func, ast.Name):
                call_info["function"] = node.func.id
            elif isinstance(node.func, ast.Attribute):
                call_info["function"] = node.func.attr
                if isinstance(node.func.value, ast.Name):
                    call_info["object"] = node.func.value.id
            
            calls.append(call_info)
    
    return calls


def extract_string_literals(tree: ast.AST) -> List[Tuple[int, str]]:
    """Extract string literals with line numbers"""
    strings = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Str):
            strings.append((node.lineno, node.s))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.append((node.lineno, node.value))
    
    return strings


def extract_assignments(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract variable assignments from AST"""
    assignments = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append({
                        "variable": target.id,
                        "line": node.lineno,
                    })
    
    return assignments


def find_pattern_in_file(filepath: str, pattern: str) -> List[Tuple[int, str]]:
    """Find regex pattern in file and return matches with line numbers"""
    content = read_file_safe(filepath)
    if not content:
        return []
    
    matches = []
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line):
            matches.append((i, line.strip()))
    
    return matches


def find_patterns_in_file(filepath: str, patterns: List[str]) -> Dict[str, List[Tuple[int, str]]]:
    """Find multiple patterns in file"""
    results = {}
    
    for pattern in patterns:
        matches = find_pattern_in_file(filepath, pattern)
        if matches:
            results[pattern] = matches
    
    return results


def get_code_snippet(filepath: str, line_number: int, context_lines: int = 3) -> str:
    """Get code snippet around a specific line"""
    content = read_file_safe(filepath)
    if not content:
        return ""
    
    lines = content.split('\n')
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    
    snippet_lines = []
    for i in range(start, end):
        marker = ">>> " if i == line_number - 1 else "    "
        snippet_lines.append(f"{marker}{i+1:4d} | {lines[i]}")
    
    return '\n'.join(snippet_lines)


def detect_language(filepath: str) -> str:
    """Detect programming language from file extension"""
    from shared.constants import SCANNABLE_EXTENSIONS
    
    ext = Path(filepath).suffix
    return SCANNABLE_EXTENSIONS.get(ext, "unknown")


def is_test_file(filepath: str) -> bool:
    """Check if file is a test file"""
    path = Path(filepath)
    name = path.name.lower()
    
    return (
        name.startswith('test_') or
        name.endswith('_test.py') or
        'test' in path.parts or
        'tests' in path.parts
    )


def should_skip_file(filepath: str) -> bool:
    """Check if file should be skipped during scanning"""
    path = Path(filepath)
    
    skip_dirs = {
        'node_modules', '.git', '__pycache__', 'venv', 
        'env', '.env', 'dist', 'build', '.next', 
        'coverage', '.pytest_cache'
    }
    
    # Skip if in excluded directory
    if any(skip_dir in path.parts for skip_dir in skip_dirs):
        return True
    
    # Skip if too large (> 1MB)
    if path.exists() and path.stat().st_size > 1_000_000:
        return True
    
    return False


def calculate_confidence(evidence_count: int, path_length: int) -> str:
    """Calculate confidence level for taint flow"""
    if evidence_count >= 3 and path_length <= 3:
        return "high"
    elif evidence_count >= 2 or path_length <= 5:
        return "medium"
    else:
        return "low"
