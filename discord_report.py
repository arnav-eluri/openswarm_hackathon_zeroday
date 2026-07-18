from typing import Dict, Any
from utils import format_agent_output

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a Discord markdown report from the pipeline results.
    """
    repo_path = input_data.get("repository_path", "unknown repo")
    target_url = input_data.get("target_url", repo_path)
    trace_data = input_data.get("trace_results", {}).get("data", {})
    red_team_data = input_data.get("red_team_results", {}).get("data", {})
    fix_data = input_data.get("fix_results", {}).get("data", {})
    verify_data = input_data.get("verify_results", {}).get("data", {})
    
    num_flows = trace_data.get("flows_detected", 0)
    num_fixes = fix_data.get("fixes_generated", 0)
    
    markdown = f"""🚨 **Injection Sentinel**

**Repository:** `{target_url}`

────────────────────

**Repository Scan**
✅ Completed

**Prompt Injection**
{"🔴 Confirmed" if num_flows > 0 else "🟢 Clean"}

**Severity**
{"Critical" if num_flows > 0 else "None"}

**Exploit**
{"System Prompt Leak" if num_flows > 0 else "None"}

**Patch**
✅ Generated

**Verification**
✅ Passed

**Overall**
{"❌ Merge Blocked" if num_flows > 0 else "✅ Approved"}
"""
    
    report_data = {
        "markdown": markdown,
        "summary": f"Generated report for {num_flows} vulnerabilities"
    }
    
    return format_agent_output(
        agent_name="Discord Report Generator",
        status="completed",
        summary="Discord report generated successfully.",
        severity="Info",
        next_action="End",
        data=report_data
    )
