import os
from typing import Iterator, Dict, Any

from state import state
from scan_repository import execute as run_scan
from trace_prompt_injection import execute as run_trace
from red_team import execute as run_red_team
from fix_vulnerability import execute as run_fix
from verify_patch import execute as run_verify
from discord_report import execute as run_report

def execute_pipeline(repo_to_scan: str) -> Iterator[Dict[str, Any]]:
    """
    Executes the Injection Sentinel pipeline and yields progress updates.
    """
    state.update("repository_path", repo_to_scan)
    
    # Yield initial state
    yield {"step": 0, "message": "🟡 Cloning Repository..."}

    # 1. Scan Repository
    yield {"step": 1, "message": "🟢 Repository Cloned\n\n🟡 Scanner Running..."}
    scan_result = run_scan(state.get_all())
    state.update("scan_results", scan_result)
    
    if scan_result["status"] != "completed":
        yield {"step": -1, "message": "🔴 Pipeline failed at Scan step."}
        return

    # 2. Trace Prompt Injection
    yield {"step": 2, "message": "🟢 Scanner Complete\n\n🟡 Tracing Prompt Injection..."}
    trace_result = run_trace(state.get_all())
    state.update("trace_results", trace_result)

    # 3. Red Team
    yield {"step": 3, "message": "🟢 Injection Found\n\n🟡 Red Team Building Payload..."}
    red_team_result = run_red_team(state.get_all())
    state.update("red_team_results", red_team_result)

    # 4. Fix Vulnerability
    yield {"step": 4, "message": "🔴 Exploit Confirmed\n\n🟡 Fixing Vulnerability..."}
    fix_result = run_fix(state.get_all())
    state.update("fix_results", fix_result)

    # 5. Verify Patch
    yield {"step": 5, "message": "🟢 Patch Generated\n\n🟡 Verifying Patch..."}
    verify_result = run_verify(state.get_all())
    state.update("verify_results", verify_result)

    # 6. Discord Report
    yield {"step": 6, "message": "🟢 Patch Verified\n\n🟡 Generating Report..."}
    report_result = run_report(state.get_all())
    state.update("report_results", report_result)
    
    # Save output
    os.makedirs("./outputs", exist_ok=True)
    with open("./outputs/final_report.md", "w", encoding="utf-8") as f:
        f.write(report_result["data"]["markdown"])
        
    yield {"step": 7, "message": "🟢 Report Generated", "report": report_result["data"]["markdown"]}
