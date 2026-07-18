from typing import Dict, Any
from utils import format_agent_output

import os
import json
from typing import Dict, Any
from utils import format_agent_output
from openai import OpenAI

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses OpenRouter LLM to perform taint analysis and detect prompt injection vulnerabilities.
    """
    scan_data = input_data.get("scan_results", {}).get("data", {})
    sinks = scan_data.get("sinks_detected", [])
    
    flows = []
    
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
    
    for sink in sinks:
        prompt = f"""
        Analyze the following Python code snippet for prompt injection vulnerabilities. 
        Code File: {sink.get('file')}
        Line: {sink.get('line')}
        Code Content:
        ```python
        {sink.get('code')}
        ```
        Determine if there is a path for user input to reach an LLM execution sink without proper sanitization.
        Respond with ONLY a JSON array of objects with the following keys:
        "source": The source of the user input (e.g., 'request.POST["user_input"]')
        "sink": The sink code snippet
        "confidence": "high", "medium", or "low"
        "risk": "critical", "high", "medium", or "low"
        
        If no vulnerability is found, return an empty array [].
        """
        
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise security analyzer. You only output valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            # Cleanup markdown formatting if present
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            analysis_results = json.loads(content)
            for result in analysis_results:
                 flows.append({
                     "source": result.get("source", "unknown"),
                     "sink": result.get("sink", sink.get("code")),
                     "source_file": sink.get("file"),
                     "source_line": sink.get("line"),
                     "sink_file": sink.get("file"),
                     "sink_line": sink.get("line"),
                     "confidence": result.get("confidence", "low"),
                     "risk": result.get("risk", "low")
                 })
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            pass # Continue to next sink on error

    trace_data = {
        "flows_detected": len(flows),
        "flows": flows
    }
    
    severity = "Critical" if flows else "Info"
    
    return format_agent_output(
        agent_name="Prompt Injection Tracer",
        status="completed",
        summary=f"Traced {len(flows)} prompt injection flows via LLM.",
        severity=severity,
        next_action="Red Team Agent",
        data=trace_data
    )
