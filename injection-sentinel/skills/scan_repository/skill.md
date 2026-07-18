# Skill: Scan Repository

## Purpose

Traverse a code repository to discover files containing LLM integration code, user input handling, and prompt construction patterns.

## Entrypoint

`scan_repository.py::execute(input_data)`

## Inputs

```json
{
  "repository_path": "string (absolute or relative path to repository)"
}
```

## Outputs

```json
{
  "status": "success|failure",
  "summary": "string (human-readable summary)",
  "repository_path": "string",
  "files": [
    {
      "path": "string",
      "language": "python|javascript|typescript",
      "size": "number",
      "has_llm_code": "boolean",
      "has_user_input": "boolean",
      "has_prompts": "boolean"
    }
  ],
  "prompts": [
    {
      "file_path": "string",
      "line_number": "number",
      "code_snippet": "string",
      "method": "f-string|concatenation|template|format",
      "variables": ["string"]
    }
  ],
  "tool_calls": [
    {
      "file_path": "string",
      "line_number": "number",
      "function": "string",
      "object": "string"
    }
  ],
  "next_action": "trace_prompt_injection|none",
  "data": {}
}
```

## Capabilities

- Recursively traverse directory structure
- Detect Python, JavaScript, TypeScript files
- Identify LLM SDK imports (OpenAI, Anthropic, LangChain, etc.)
- Find user input sources (HTTP requests, CLI args, file reads)
- Locate prompt construction patterns (f-strings, templates, concatenation)
- Discover LLM API calls and tool invocations
- Build file dependency graph

## Detection Methods

- AST parsing for Python files
- Regex pattern matching for all languages
- Import statement analysis
- Function call extraction
- String interpolation detection

## Constraints

- No external API calls
- Local filesystem access only
- Must handle syntax errors gracefully
- Skip binary files and large files (>1MB)
- Ignore test directories and dependencies (node_modules, venv, etc.)

## Examples

### Input Example

```json
{
  "repository_path": "./sample_repo"
}
```

### Output Example

```json
{
  "status": "success",
  "summary": "Scanned 15 files, found 3 with LLM code, 8 prompt constructions",
  "repository_path": "./sample_repo",
  "files": [
    {
      "path": "./sample_repo/agent.py",
      "language": "python",
      "size": 2048,
      "has_llm_code": true,
      "has_user_input": true,
      "has_prompts": true
    }
  ],
  "prompts": [
    {
      "file_path": "./sample_repo/agent.py",
      "line_number": 42,
      "code_snippet": "prompt = f\"User said: {user_input}. Respond.\"",
      "method": "f-string",
      "variables": ["user_input"]
    }
  ],
  "tool_calls": [
    {
      "file_path": "./sample_repo/agent.py",
      "line_number": 50,
      "function": "create",
      "object": "client.chat.completions"
    }
  ],
  "next_action": "trace_prompt_injection",
  "data": {
    "total_files": 15,
    "python_files": 12,
    "javascript_files": 3
  }
}
```
