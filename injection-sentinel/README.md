# Injection Sentinel

**Production-quality prompt injection detection and remediation system built for OpenSwarm.**

## Overview

Injection Sentinel is a modular security analysis system that:
- Scans repositories for LLM integration code
- Traces user input to prompt construction (taint analysis)
- Generates red team payloads
- Creates secure patches
- Reports findings via Discord

## Architecture

Built using OpenSwarm's native Skills architecture. Each capability is an autonomous skill that:
- Accepts structured input
- Performs one responsibility
- Returns structured JSON
- Never calls other skills directly

## Skills

1. **scan_repository** - Repository traversal and code detection
2. **trace_prompt_injection** - Static taint analysis
3. **red_team** - Payload generation and validation
4. **fix_vulnerability** - Secure code patch generation
5. **discord_report** - Formatted reporting

## Installation

```bash
pip install -r requirements.txt
```

## Usage with OpenSwarm

Each skill can be invoked independently by the OpenSwarm orchestrator:

```python
from skills.scan_repository.scan_repository import execute as scan
from skills.trace_prompt_injection.trace_prompt_injection import execute as trace

# Scan repository
scan_result = scan({"repository_path": "./target_repo"})

# Trace vulnerabilities
trace_result = trace(scan_result)
```

## Local Execution

No external APIs required. All analysis runs locally using:

- AST parsing
- Static analysis
- Tree traversal
- Regex patterns
- Subprocess execution

## Requirements

- Python 3.9+
- No LLM API keys needed
- No remote inference

## License

MIT
