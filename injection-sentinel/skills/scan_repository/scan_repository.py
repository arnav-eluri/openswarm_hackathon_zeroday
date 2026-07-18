"""
Skill: Scan Repository
Autonomous agent for repository scanning and LLM code detection.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, Any, List

# Import shared utilities
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import FileInfo, PromptConstruction, ScanResult
from shared.constants import (
    LLM_IMPORTS, 
    USER_INPUT_PATTERNS, 
    PROMPT_PATTERNS,
    DANGEROUS_SINKS,
    SCANNABLE_EXTENSIONS
)
from shared.utils import (
    read_file_safe,
    parse_python_ast,
    extract_imports,
    extract_function_calls,
    find_patterns_in_file,
    get_code_snippet,
    detect_language,
    should_skip_file
)


class RepositoryScanner:
    """Repository scanner for LLM code detection"""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path).resolve()
        self.files: List[FileInfo] = []
        self.prompts: List[PromptConstruction] = []
        self.tool_calls: List[Dict[str, Any]] = []
    
    def scan(self) -> Dict[str, Any]:
        """Main scanning logic"""
        
        if not self.repository_path.exists():
            return {
                "status": "failure",
                "summary": f"Repository not found: {self.repository_path}",
                "repository_path": str(self.repository_path),
                "files": [],
                "prompts": [],
                "tool_calls": [],
                "next_action": "none",
                "data": {}
            }
        
        # Traverse repository
        self._traverse_directory(self.repository_path)
        
        # Analyze each file
        for file_info in self.files:
            self._analyze_file(file_info)
        
        # Build result
        return self._build_result()
    
    def _traverse_directory(self, path: Path):
        """Recursively traverse directory"""
        
        try:
            for item in path.iterdir():
                # Skip hidden files and excluded directories
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    if not should_skip_file(str(item)):
                        self._traverse_directory(item)
                elif item.is_file():
                    if not should_skip_file(str(item)):
                        self._process_file(item)
        except PermissionError:
            pass
    
    def _process_file(self, filepath: Path):
        """Process a single file"""
        
        ext = filepath.suffix
        if ext not in SCANNABLE_EXTENSIONS:
            return
        
        language = SCANNABLE_EXTENSIONS[ext]
        
        file_info = FileInfo(
            path=str(filepath),
            language=language,
            size=filepath.stat().st_size,
            has_llm_code=False,
            has_user_input=False,
            has_prompts=False
        )
        
        self.files.append(file_info)
    
    def _analyze_file(self, file_info: FileInfo):
        """Analyze file for LLM patterns"""
        
        content = read_file_safe(file_info.path)
        if not content:
            return
        
        # Check for LLM imports
        if file_info.language == "python":
            self._analyze_python_file(file_info, content)
        else:
            self._analyze_javascript_file(file_info, content)
    
    def _analyze_python_file(self, file_info: FileInfo, content: str):
        """Analyze Python file using AST"""
        
        tree = parse_python_ast(content)
        if not tree:
            # Fallback to regex
            self._analyze_with_regex(file_info, content)
            return
        
        # Extract imports
        imports = extract_imports(tree)
        
        # Check for LLM SDK imports
        for imp in imports:
            if any(llm_lib in imp.lower() for llm_lib in LLM_IMPORTS):
                file_info.has_llm_code = True
                break
        
        # Extract function calls
        calls = extract_function_calls(tree)
        
        # Find LLM API calls
        for call in calls:
            if 'function' in call:
                func_name = call['function']
                
                # Check if it's an LLM call
                for pattern in DANGEROUS_SINKS:
                    if re.search(pattern, func_name):
                        self.tool_calls.append({
                            "file_path": file_info.path,
                            "line_number": call['line'],
                            "function": func_name,
                            "object": call.get('object', '')
                        })
                        file_info.has_llm_code = True
        
        # Find user input patterns
        for pattern in USER_INPUT_PATTERNS:
            matches = find_pattern_in_file(file_info.path, pattern)
            if matches:
                file_info.has_user_input = True
                break
        
        # Find prompt construction
        self._find_prompt_constructions(file_info, content)
    
    def _analyze_javascript_file(self, file_info: FileInfo, content: str):
        """Analyze JavaScript/TypeScript file"""
        
        # Use regex patterns for JS/TS
        self._analyze_with_regex(file_info, content)
    
    def _analyze_with_regex(self, file_info: FileInfo, content: str):
        """Analyze file using regex patterns"""
        
        # Check for LLM imports
        for llm_lib in LLM_IMPORTS:
            if re.search(rf'\b{llm_lib}\b', content, re.IGNORECASE):
                file_info.has_llm_code = True
                break
        
        # Check for user input
        for pattern in USER_INPUT_PATTERNS:
            if re.search(pattern, content):
                file_info.has_user_input = True
                break
        
        # Find prompt constructions
        self._find_prompt_constructions(file_info, content)
    
    def _find_prompt_constructions(self, file_info: FileInfo, content: str):
        """Find prompt construction patterns in file"""
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in PROMPT_PATTERNS:
                if re.search(pattern, line):
                    file_info.has_prompts = True
                    
                    # Determine method
                    method = "unknown"
                    if 'f"' in line or "f'" in line:
                        method = "f-string"
                    elif '.format(' in line:
                        method = "format"
                    elif '.join(' in line:
                        method = "join"
                    elif '+' in line:
                        method = "concatenation"
                    elif 'Template' in line:
                        method = "template"
                    
                    # Extract variables (simple heuristic)
                    variables = re.findall(r'\{(\w+)\}', line)
                    
                    prompt = PromptConstruction(
                        file_path=file_info.path,
                        line_number=i,
                        code_snippet=get_code_snippet(file_info.path, i, context_lines=2),
                        method=method,
                        variables=variables
                    )
                    
                    self.prompts.append(prompt)
                    break
    
    def _build_result(self) -> Dict[str, Any]:
        """Build final result"""
        
        files_with_llm = sum(1 for f in self.files if f.has_llm_code)
        files_with_input = sum(1 for f in self.files if f.has_user_input)
        
        next_action = "trace_prompt_injection" if self.prompts else "none"
        
        result = ScanResult(
            status="success",
            summary=f"Scanned {len(self.files)} files, found {files_with_llm} with LLM code, {len(self.prompts)} prompt constructions",
            repository_path=str(self.repository_path),
            files=self.files,
            prompts=self.prompts,
            tool_calls=self.tool_calls,
            next_action=next_action,
            data={
                "total_files": len(self.files),
                "files_with_llm_code": files_with_llm,
                "files_with_user_input": files_with_input,
                "total_prompts": len(self.prompts),
                "total_tool_calls": len(self.tool_calls)
            }
        )
        
        return result.to_dict()


def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill entrypoint.
    
    Args:
        input_data: {
            "repository_path": str
        }
    
    Returns:
        Structured JSON result
    """
    
    try:
        repository_path = input_data.get("repository_path", ".")
        
        scanner = RepositoryScanner(repository_path)
        result = scanner.scan()
        
        return result
        
    except Exception as e:
        return {
            "status": "failure",
            "summary": f"Scan failed: {str(e)}",
            "repository_path": input_data.get("repository_path", ""),
            "files": [],
            "prompts": [],
            "tool_calls": [],
            "next_action": "none",
            "data": {"error": str(e)}
        }


# Helper for regex pattern matching
def find_pattern_in_file(filepath: str, pattern: str) -> List[tuple]:
    """Find pattern in file"""
    content = read_file_safe(filepath)
    if not content:
        return []
    
    matches = []
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line):
            matches.append((i, line.strip()))
    
    return matches


if __name__ == "__main__":
    # Test execution
    result = execute({"repository_path": "../../sample_repo"})
    
    import json
    print(json.dumps(result, indent=2))
