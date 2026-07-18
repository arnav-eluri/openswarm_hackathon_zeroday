# Skill: Trace Prompt Injection

## Purpose

Perform static taint analysis to trace user input from sources (HTTP requests, CLI, files) to sinks (LLM prompts, tool calls) and identify potential prompt injection vulnerabilities.

## Entrypoint

`trace_prompt_injection.py::execute(input_data)`

## Inputs

```json
{
  "repository_path": "string",
  "files": [
    {
      "path": "string",
      "has_llm_code": "boolean",
      "has_user_input": "boolean",
      "has_prompts": "boolean"
    }
  ],
  "prompts": [
    {
      "file_path": "string",
      "line_number": "number",
      "variables": ["string"]
    }
  ],
  "tool_calls": [
    {
      "file_path": "string",
      "line_number": "number"
    }
  ]
}
```

## Outputs

```json
{
  "status": "success|failure",
  "summary": "string",
  "flows": [
    {
      "source": "string (e.g., 'request.POST')",
      "source_file": "string",
      "source_line": "number",
      "sink": "string (e.g., 'llm.invoke')",
      "sink_file": "string",
      "sink_line": "number",
      "path": ["step1", "step2", "step3"],
      "confidence": "high|medium|low",
      "evidence": ["string"]
    }
  ],
  "vulnerability_count": "number",
  "next_action": "red_team|none",
  "data": {}
}
```

## Capabilities

- Static taint analysis using AST
- Trace variable assignments and flows
- Identify data flow from sources to sinks
- Calculate confidence levels based on evidence
- Detect sanitization functions (if present)
- Build taint propagation graph
- Handle inter-procedural flows

## Detection Strategy

1. **Identify Sources:** Find user input points (HTTP, CLI, files, env vars)
2. **Identify Sinks:** Find prompt constructions and LLM calls
3. **Build Flow Graph:** Track variable assignments and function calls
4. **Path Analysis:** Find paths from sources to sinks
5. **Confidence Scoring:** Calculate based on evidence and path length

## Confidence Levels

- **High:** Direct flow with 3+ evidence points, path length ≤ 3
- **Medium:** Indirect flow with 2+ evidence points, path length ≤ 5
- **Low:** Possible flow with limited evidence

## Constraints

- No execution of target code
- Static analysis only
- No external dependencies required
- Must handle incomplete code gracefully
- Python-focused with regex fallback for other languages

## Examples

### Input Example

```json
{
  "repository_path": "./sample_repo",
  "files": [
    {
      "path": "./sample_repo/agent.py",
      "has_llm_code": true,
      "has_user_input": true,
      "has_prompts": true
    }
  ],
  "prompts": [
    {
      "file_path": "./sample_repo/agent.py",
      "line_number": 42,
      "variables": ["user_input"]
    }
  ],
  "tool_calls": []
}
```

### Output Example

```json
{
  "status": "success",
  "summary": "Found 2 taint flows, 2 vulnerabilities",
  "flows": [
    {
      "source": "request.POST['message']",
      "source_file": "./sample_repo/agent.py",
      "source_line": 15,
      "sink": "llm.invoke(prompt)",
      "sink_file": "./sample_repo/agent.py",
      "sink_line": 42,
      "path": [
        "request.POST['message'] -> user_input (line 15)",
        "user_input -> prompt via f-string (line 42)",
        "prompt -> llm.invoke (line 42)"
      ],
      "confidence": "high",
      "evidence": [
        "Direct assignment from request.POST",
        "No sanitization detected",
        "F-string interpolation into prompt"
      ]
    }
  ],
  "vulnerability_count": 2,
  "next_action": "red_team",
  "data": {
    "sources_found": 3,
    "sinks_found": 2,
    "paths_analyzed": 5
  }
}
```
