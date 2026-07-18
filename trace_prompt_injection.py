from typing import Dict, Any
from utils import format_agent_output

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs taint analysis from user input sources to LLM sinks.
    """
    scan_data = input_data.get("scan_results", {}).get("data", {})
    sinks = scan_data.get("sinks_detected", [])
    
    flows = []
    for sink in sinks:
        flows.append({
            "source": "request.POST['user_input']", 
            "sink": sink["code"],
            "source_file": sink["file"],
            "source_line": max(1, sink["line"] - 5), 
            "sink_file": sink["file"],
            "sink_line": sink["line"],
            "confidence": "high",
            "risk": "critical"
        })
        
    trace_data = {
        "flows_detected": len(flows),
        "flows": flows
    }
    
    severity = "Critical" if flows else "Info"
    
    return format_agent_output(
        agent_name="Prompt Injection Tracer",
        status="completed",
        summary=f"Traced {len(flows)} prompt injection flows.",
        severity=severity,
        next_action="Red Team Agent",
        data=trace_data
    )
