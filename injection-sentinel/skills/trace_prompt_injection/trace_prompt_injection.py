"""
Skill: Trace Prompt Injection
Autonomous agent for static taint analysis.
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import TaintFlow, TraceResult
from shared.constants import USER_INPUT_PATTERNS, DANGEROUS_SINKS
from shared.utils import (
    read_file_safe,
    parse_python_ast,
    calculate_confidence,
    get_code_snippet
)


class TaintAnalyzer:
    """Static taint analysis for prompt injection detection"""
    
    def __init__(self, repository_path: str, scan_results: Dict[str, Any]):
        self.repository_path = Path(repository_path)
        self.scan_results = scan_results
        self.flows: List[TaintFlow] = []
        
        # Track tainted variables per file
        self.tainted_vars: Dict[str, Set[str]] = defaultdict(set)
        
        # Track sinks per file
        self.sinks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def analyze(self) -> Dict[str, Any]:
        """Main analysis logic"""
        
        # Extract files with both input and prompts
        vulnerable_files = [
            f for f in self.scan_results.get('files', [])
            if f.get('has_user_input') and f.get('has_prompts')
        ]
        
        if not vulnerable_files:
            return self._build_result()
        
        # Analyze each file
        for file_info in vulnerable_files:
            self._analyze_file(file_info)
        
        return self._build_result()
    
    def _analyze_file(self, file_info: Dict[str, Any]):
        """Analyze single file for taint flows"""
        
        filepath = file_info['path']
        content = read_file_safe(filepath)
        
        if not content:
            return
        
        # Parse AST for Python files
        if file_info['language'] == 'python':
            tree = parse_python_ast(content)
            if tree:
                self._analyze_python_ast(filepath, tree, content)
            else:
                self._analyze_with_regex(filepath, content)
        else:
            self._analyze_with_regex(filepath, content)
    
    def _analyze_python_ast(self, filepath: str, tree: ast.AST, content: str):
        """Analyze Python file using AST"""
        
        lines = content.split('\n')
        
        # Find sources (user input points)
        sources = self._find_sources(filepath, tree, lines)
        
        # Find sinks (prompt constructions)
        sinks = self._find_sinks(filepath, tree, lines)
        
        # Build taint propagation graph
        assignments = self._extract_assignments(tree)
        
        # Trace flows from sources to sinks
        for source in sources:
            source_var = source['variable']
            source_line = source['line']
            
            # Mark source variable as tainted
            self.tainted_vars[filepath].add(source_var)
            
            # Trace taint propagation
            tainted = self._propagate_taint(
                filepath, 
                source_var, 
                assignments
            )
            
            # Check if any tainted variable reaches a sink
            for sink in sinks:
                sink_vars = sink.get('variables', [])
                
                # Check if any sink variable is tainted
                for sink_var in sink_vars:
                    if sink_var in tainted:
                        # Found a flow!
                        flow = self._create_flow(
                            source, 
                            sink, 
                            filepath,
                            self._build_path(source_var, sink_var, assignments)
                        )
                        self.flows.append(flow)
    
    def _find_sources(self, filepath: str, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Find user input sources in AST"""
        
        sources = []
        
        for node in ast.walk(tree):
            # Look for assignments from user input
            if isinstance(node, ast.Assign):
                # Check if RHS contains user input pattern
                rhs_code = ast.unparse(node.value) if hasattr(ast, 'unparse') else ''
                
                for pattern in USER_INPUT_PATTERNS:
                    if re.search(pattern, rhs_code):
                        # Extract variable name
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                sources.append({
                                    'variable': target.id,
                                    'line': node.lineno,
                                    'source_type': pattern,
                                    'code': lines[node.lineno - 1] if node.lineno <= len(lines) else ''
                                })
        
        return sources
    
    def _find_sinks(self, filepath: str, tree: ast.AST, lines: List[str]) -> List[Dict[str, Any]]:
        """Find prompt construction sinks in AST"""
        
        sinks = []
        
        # Look for prompt constructions from scan results
        for prompt in self.scan_results.get('prompts', []):
            if prompt['file_path'] == filepath:
                sinks.append({
                    'line': prompt['line_number'],
                    'variables': prompt.get('variables', []),
                    'method': prompt.get('method', 'unknown'),
                    'code': lines[prompt['line_number'] - 1] if prompt['line_number'] <= len(lines) else ''
                })
        
        # Also look for direct LLM calls
        for call in self.scan_results.get('tool_calls', []):
            if call['file_path'] == filepath:
                # Extract variables passed to LLM call
                code_line = lines[call['line_number'] - 1] if call['line_number'] <= len(lines) else ''
                variables = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code_line)
                
                sinks.append({
                    'line': call['line_number'],
                    'variables': variables,
                    'method': 'llm_call',
                    'code': code_line
                })
        
        return sinks
    
    def _extract_assignments(self, tree: ast.AST) -> Dict[str, List[Tuple[int, Set[str]]]]:
        """Extract variable assignments and their dependencies"""
        
        assignments = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Get LHS variable
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        lhs = target.id
                        
                        # Get RHS variables
                        rhs_vars = set()
                        for n in ast.walk(node.value):
                            if isinstance(n, ast.Name):
                                rhs_vars.add(n.id)
                        
                        assignments[lhs].append((node.lineno, rhs_vars))
        
        return assignments
    
    def _propagate_taint(
        self, 
        filepath: str, 
        source_var: str, 
        assignments: Dict[str, List[Tuple[int, Set[str]]]]
    ) -> Set[str]:
        """Propagate taint from source variable"""
        
        tainted = {source_var}
        changed = True
        
        # Fixed-point iteration
        while changed:
            changed = False
            for var, deps_list in assignments.items():
                for line, deps in deps_list:
                    # If any dependency is tainted, taint this variable
                    if deps & tainted and var not in tainted:
                        tainted.add(var)
                        changed = True
        
        return tainted
    
    def _build_path(
        self, 
        source_var: str, 
        sink_var: str, 
        assignments: Dict[str, List[Tuple[int, Set[str]]]]
    ) -> List[str]:
        """Build taint propagation path"""
        
        path = [f"{source_var} (source)"]
        
        # Simple path reconstruction
        current = source_var
        visited = {current}
        
        for _ in range(10):  # Limit path length
            found_next = False
            for var, deps_list in assignments.items():
                if var in visited:
                    continue
                for line, deps in deps_list:
                    if current in deps:
                        path.append(f"{current} -> {var} (line {line})")
                        current = var
                        visited.add(var)
                        found_next = True
                        if var == sink_var:
                            return path
                        break
                if found_next:
                    break
            if not found_next:
                break
        
        path.append(f"{sink_var} (sink)")
        return path
    
    def _create_flow(
        self, 
        source: Dict[str, Any], 
        sink: Dict[str, Any], 
        filepath: str,
        path: List[str]
    ) -> TaintFlow:
        """Create TaintFlow object"""
        
        evidence = [
            f"Source: {source['code']}",
            f"Sink: {sink['code']}",
            f"No sanitization detected",
        ]
        
        confidence = calculate_confidence(len(evidence), len(path))
        
        return TaintFlow(
            source=source['code'].strip(),
            source_file=filepath,
            source_line=source['line'],
            sink=sink['code'].strip(),
            sink_file=filepath,
            sink_line=sink['line'],
            path=path,
            confidence=confidence,
            evidence=evidence
        )
    
    def _analyze_with_regex(self, filepath: str, content: str):
        """Fallback regex-based analysis"""
        
        lines = content.split('\n')
        
        # Find sources
        sources = []
        for i, line in enumerate(lines, 1):
            for pattern in USER_INPUT_PATTERNS:
                if re.search(pattern, line):
                    # Extract variable name (simple heuristic)
                    match = re.search(r'(\w+)\s*=', line)
                    if match:
                        sources.append({
                            'variable': match.group(1),
                            'line': i,
                            'code': line.strip()
                        })
        
        # Find sinks from scan results
        sinks = []
        for prompt in self.scan_results.get('prompts', []):
            if prompt['file_path'] == filepath:
                sinks.append(prompt)
        
        # Simple heuristic: if source and sink in same file, likely a flow
        for source in sources:
            for sink in sinks:
                # Check if source variable appears in sink line
                sink_line_idx = sink['line_number'] - 1
                if sink_line_idx < len(lines):
                    sink_code = lines[sink_line_idx]
                    if source['variable'] in sink_code:
                        flow = TaintFlow(
                            source=source['code'],
                            source_file=filepath,
                            source_line=source['line'],
                            sink=sink_code.strip(),
                            sink_file=filepath,
                            sink_line=sink['line_number'],
                            path=[
                                f"{source['variable']} (source, line {source['line']})",
                                f"Used in prompt (line {sink['line_number']})"
                            ],
                            confidence="medium",
                            evidence=[
                                "Variable found in prompt construction",
                                "Same-file flow detected"
                            ]
                        )
                        self.flows.append(flow)
    
    def _build_result(self) -> Dict[str, Any]:
        """Build final result"""
        
        next_action = "red_team" if self.flows else "none"
        
        result = TraceResult(
            status="success",
            summary=f"Found {len(self.flows)} taint flows, {len(self.flows)} vulnerabilities",
            flows=self.flows,
            vulnerability_count=len(self.flows),
            next_action=next_action,
            data={
                "total_flows": len(self.flows),
                "high_confidence": sum(1 for f in self.flows if f.confidence == "high"),
                "medium_confidence": sum(1 for f in self.flows if f.confidence == "medium"),
                "low_confidence": sum(1 for f in self.flows if f.confidence == "low"),
            }
        )
        
        return result.to_dict()


def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill entrypoint.
    
    Args:
        input_data: Results from scan_repository skill
    
    Returns:
        Structured JSON result
    """
    
    try:
        repository_path = input_data.get("repository_path", ".")
        
        analyzer = TaintAnalyzer(repository_path, input_data)
        result = analyzer.analyze()
        
        return result
        
    except Exception as e:
        return {
            "status": "failure",
            "summary": f"Trace failed: {str(e)}",
            "flows": [],
            "vulnerability_count": 0,
            "next_action": "none",
            "data": {"error": str(e)}
        }


if __name__ == "__main__":
    # Test execution
    import json
    
    # Mock scan results
    mock_input = {
        "repository_path": "../../sample_repo",
        "files": [
            {
                "path": "../../sample_repo/agent.py",
                "language": "python",
                "has_llm_code": True,
                "has_user_input": True,
                "has_prompts": True
            }
        ],
        "prompts": [
            {
                "file_path": "../../sample_repo/agent.py",
                "line_number": 10,
                "variables": ["user_input"],
                "method": "f-string"
            }
        ],
        "tool_calls": []
    }
    
    result = execute(mock_input)
    print(json.dumps(result, indent=2))
