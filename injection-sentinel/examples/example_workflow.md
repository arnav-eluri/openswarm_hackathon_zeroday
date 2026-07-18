# Example Workflow

## How OpenSwarm Orchestrates Injection Sentinel

OpenSwarm acts as the orchestrator, invoking each skill in sequence based on the `next_action` field in each skill's output.

### Step 1: Scan Repository

```json
{
  "skill": "scan_repository",
  "input": {
    "repository_path": "./sample_repo"
  }
}
```

Output:

```json
{
  "status": "success",
  "summary": "Scanned 3 files, found 3 with LLM code",
  "files": [...],
  "prompts": [...],
  "next_action": "trace_prompt_injection"
}
```

### Step 2: Trace Prompt Injection

OpenSwarm sees `next_action: "trace_prompt_injection"` and invokes that skill.

```json
{
  "skill": "trace_prompt_injection",
  "input": {
    "repository_path": "./sample_repo",
    "files": [...],
    "prompts": [...]
  }
}
```

Output:

```json
{
  "status": "success",
  "flows": [...],
  "vulnerability_count": 4,
  "next_action": "red_team"
}
```

### Step 3: Red Team

```json
{
  "skill": "red_team",
  "input": {
    "repository_path": "./sample_repo",
    "flows": [...]
  }
}
```

Output:

```json
{
  "status": "success",
  "payloads": [...],
  "validated_count": 3,
  "next_action": "fix_vulnerability"
}
```

### Step 4: Fix Vulnerability

```json
{
  "skill": "fix_vulnerability",
  "input": {
    "repository_path": "./sample_repo",
    "flows": [...],
    "payloads": [...]
  }
}
```

Output:

```json
{
  "status": "success",
  "fixes": [...],
  "files_changed": 2,
  "next_action": "discord_report"
}
```

### Step 5: Discord Report

```json
{
  "skill": "discord_report",
  "input": {
    "repository_path": "./sample_repo",
    "flows": [...],
    "payloads": [...],
    "fixes": [...]
  }
}
```

Output:

```json
{
  "status": "success",
  "markdown": "# Security Report...",
  "embeds": [...],
  "next_action": "complete"
}
```

### Step 6: Complete

OpenSwarm sees `next_action: "complete"` and ends the workflow.

---

## Key Points

- **No skill calls another skill directly**
- OpenSwarm orchestrator makes all decisions
- Each skill is autonomous and stateless
- Skills communicate only through JSON
- Workflow is data-driven, not code-driven
