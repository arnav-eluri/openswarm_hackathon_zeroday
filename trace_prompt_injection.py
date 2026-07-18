import os
import json
from typing import Dict, Any
from utils import format_agent_output, walk_repository
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert AI Security Auditor specializing in LLM application security, prompt injection, and AI agent vulnerability assessment.

You are given a GitHub repository URL or a cloned repository.

Your job is to perform a complete repository-level security audit for prompt injection vulnerabilities.

IMPORTANT:
Do not classify vulnerabilities based on keywords, filenames, or the presence of AI-related code alone.

The repository may contain:
- LLM SDK usage
- prompt templates
- system messages
- AI documentation
- test payloads
- examples

These are NOT vulnerabilities by themselves.

You must identify an actual exploitable attack path.

==================================================
REPOSITORY ANALYSIS
==================================================

First determine:

1. Repository type:
   - AI Agent
   - LLM Application
   - IDE Extension
   - SDK / Library
   - Plugin
   - Documentation
   - Traditional Application

2. Identify:
   - LLM providers used
   - AI frameworks used
   - Agent/tool calling logic
   - Prompt construction locations
   - Memory/context handling
   - Retrieval systems
   - External data sources

==================================================
PROMPT INJECTION DETECTION REQUIREMENTS
==================================================

A prompt injection vulnerability is CONFIRMED only if:

ALL conditions are true:

1. The repository contains an LLM execution path.

2. The application processes attacker-controlled or untrusted content.

Examples:
- user chat input
- uploaded files
- repository files
- web content
- emails
- documents
- API responses
- terminal output

3. The untrusted content can influence:

- system instructions
- developer instructions
- tool calls
- agent planning
- memory
- privileged actions

4. There is a realistic exploit scenario.

5. The impact is demonstrable.

==================================================
SYSTEM PROMPT LEAK ANALYSIS
==================================================

Only report "System Prompt Leak" when:

A hidden instruction exists:

SYSTEM_PROMPT = "private internal instructions"

AND

Untrusted data reaches the same LLM context.

Example vulnerable flow:

system_prompt + external_content + user_request
             |
             v
             LLM

AND

An attacker can extract:
- hidden prompts
- internal rules
- secrets
- tool permissions
- private context

==================================================
DO NOT REPORT AS VULNERABLE
==================================================

Ignore these cases:
- OpenAI SDK usage
- AWS SDK usage
- Anthropic SDK usage
- Google AI SDK usage
- LangChain examples
- Prompt templates
- System message examples
- Documentation
- README files
- Unit tests
- Security test cases
- Example attacks
- API wrappers
- Configuration samples

==================================================
REQUIRED SECURITY REVIEW PROCESS
==================================================

Perform:
1. Static code analysis.
2. Search for LLM invocation points.
3. Trace data flow:

External Input
      |
      v
Processing
      |
      v
Prompt Builder
      |
      v
LLM Call
      |
      v
Tool / Action / Output

4. Identify attacker-controlled sources.
5. Determine exploitability.
6. Attempt realistic attack simulation.

==================================================
FINAL DECISION RULES
==================================================

TRUE_POSITIVE:
Only with proven exploit path.

FALSE_POSITIVE:
Pattern exists but no exploit path.

CLEAN:
Repository analyzed and no exploitable prompt injection found.

NEEDS_REVIEW:
Insufficient evidence.

Never approve only because no suspicious strings exist.

==================================================
OUTPUT FORMAT
==================================================

Return JSON only:

{
  "classification": "CLEAN | TRUE_POSITIVE | FALSE_POSITIVE | NEEDS_REVIEW",
  "confidence": 0,
  "repository_type": "",
  "ai_components": [],
  "llm_entrypoints": [],
  "untrusted_input_sources": [],
  "data_flow": "",
  "attack_simulation": [],
  "vulnerability": "",
  "severity": "",
  "evidence": [],
  "reasoning": "",
  "recommended_action": ""
}

Security correctness is more important than finding more issues."""

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses OpenRouter LLM to perform a complete repository-level security audit for prompt injection.
    """
    repo_path = input_data.get("repository_path", ".")
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return format_agent_output(
            agent_name="Prompt Injection Tracer",
            status="error",
            summary="OPENROUTER_API_KEY environment variable not set.",
            severity="Critical",
            next_action="stop"
        )
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # Read repository contents
    py_files = walk_repository(repo_path)
    repo_content = ""
    for f in py_files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                repo_content += f"\n\n--- File: {os.path.basename(f)} ---\n"
                repo_content += file.read()
        except Exception:
            pass
            
    prompt = f"Analyze the following repository code:\n\n{repo_content}"
    
    flows = []
    trace_data = {"flows_detected": 0, "flows": [], "audit_report": {}}
    severity = "Info"
    summary = "Repository analyzed. No vulnerabilities found."
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen-2.5-coder-32b-instruct:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        audit_report = json.loads(content)
        trace_data["audit_report"] = audit_report
        
        classification = audit_report.get("classification", "CLEAN")
        
        if classification == "TRUE_POSITIVE":
            severity = "Critical"
            summary = f"LLM Audit found {classification}: {audit_report.get('vulnerability', 'Prompt Injection')}"
            
            # Map the detailed audit report back to the 'flows' format expected by the rest of the pipeline
            for evidence in audit_report.get("evidence", []):
                flows.append({
                    "source": str(audit_report.get("untrusted_input_sources", ["unknown"])),
                    "sink": str(evidence),
                    "source_file": "unknown",
                    "source_line": 0,
                    "sink_file": "unknown",
                    "sink_line": 0,
                    "confidence": "high" if audit_report.get("confidence", 0) > 80 else "medium",
                    "risk": audit_report.get("severity", "critical").lower()
                })
                
            # If evidence is empty but it's a true positive, create at least one flow so red team can test it
            if not flows:
                flows.append({
                    "source": "untrusted_input",
                    "sink": str(audit_report.get("llm_entrypoints", ["unknown sink"])[0]),
                    "source_file": "unknown",
                    "source_line": 0,
                    "sink_file": "unknown",
                    "sink_line": 0,
                    "confidence": "high",
                    "risk": "critical"
                })
                
        trace_data["flows"] = flows
        trace_data["flows_detected"] = len(flows)
        
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return format_agent_output(
            agent_name="Prompt Injection Tracer",
            status="error",
            summary=f"LLM API Error: {str(e)}",
            severity="Critical",
            next_action="stop"
        )

    return format_agent_output(
        agent_name="Prompt Injection Tracer",
        status="completed",
        summary=summary,
        severity=severity,
        next_action="Red Team Agent",
        data=trace_data
    )
