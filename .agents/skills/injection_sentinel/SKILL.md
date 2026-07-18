---
name: injection_sentinel
description: A multi-agent security pipeline that scans an AI repository for Prompt Injection vulnerabilities.
---

# Skill: Injection Sentinel

## Purpose
A production-quality prompt injection detection and remediation system. It scans a repository for LLM sinks, traces user input to these sinks, validates exploitability via red teaming, generates secure defensive patches (like delimiters), verifies those patches, and reports the findings.

## When to use
Use this skill when you need to audit an AI/LLM-integrated codebase for prompt injection vulnerabilities and generate secure fixes for them locally, without relying on remote APIs.

## Entrypoint
`python workflow.py`

## Expected Inputs
Execute the script from the command line, optionally passing the repository directory as an argument.
```bash
python workflow.py [path_to_repository]
```

## Expected Outputs
The pipeline orchestrates various independent agents. The final output is a Markdown report generated in `./outputs/final_report.md` containing:
- Executive Summary of vulnerabilities.
- Detected input-to-prompt traces.
- Validated red team exploits.
- Python code diffs for security patches.

## Constraints
- **Execution:** All operations occur locally using pure Python.
- **Independence:** No remote LLM providers (OpenAI, Gemini, Anthropic) are used.
- **Architecture:** Follows the OpenSwarm multi-agent architecture where agents do not call each other directly; they are coordinated via `workflow.py`.

## Examples
To run against the included sample repository:
```bash
python workflow.py ./sample_repo
```

To run against a custom directory:
```bash
python workflow.py ../my_ai_project
```

IMPORTANT
All file paths below are relative to
C:/Users/arnav/Desktop/Injection-Sentinel
