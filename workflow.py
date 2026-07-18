import os
import sys
import tempfile
import git
from typing import Iterator, Dict, Any

from state import state
from scan_repository import execute as run_scan
from trace_prompt_injection import execute as run_trace
from red_team import execute as run_red_team
from fix_vulnerability import execute as run_fix
from verify_patch import execute as run_verify
from discord_report import execute as run_report

def acquire_repository(target: str) -> str:
    """
    Acquires the target repository. If it's a GitHub URL, clones it.
    If it's a GitHub PR URL, fetches and checks out the PR HEAD.
    Returns the path to the local repository.
    """
    if not target.startswith("http"):
        return target
        
    temp_dir = tempfile.mkdtemp()
    
    try:
        if "/pull/" in target:
            # Parse PR URL: https://github.com/owner/repo/pull/123
            repo_url = target.split("/pull/")[0] + ".git"
            pr_num = target.split("/pull/")[1].split("/")[0]
            
            print(f"Cloning base repository: {repo_url}")
            repo = git.Repo.clone_from(repo_url, temp_dir)
            
            print(f"Fetching Pull Request #{pr_num}...")
            # Fetch the PR branch
            repo.remotes.origin.fetch(f"pull/{pr_num}/head:pr-{pr_num}")
            
            print(f"Checking out PR HEAD (pr-{pr_num})...")
            repo.git.checkout(f"pr-{pr_num}")
            
            # Identify changed files
            # Determine base branch by checking out origin/main or origin/master if available
            base_branch = "origin/main"
            try:
                changed_files = repo.git.diff("--name-only", f"{base_branch}...HEAD").splitlines()
                state.update("changed_files", changed_files)
                print(f"Computed {len(changed_files)} changed files in the Pull Request.")
            except Exception as e:
                print(f"Could not compute changed files against {base_branch}: {e}")
                
        else:
            # Normal repository URL
            repo_url = target if target.endswith(".git") else target + ".git"
            print(f"Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, temp_dir)
            
    except Exception as e:
        raise RuntimeError(f"Failed to acquire repository: {str(e)}")
        
    return temp_dir


def execute_pipeline(target_url: str) -> Iterator[Dict[str, Any]]:
    """
    Executes the Injection Sentinel pipeline and yields progress updates.
    """
    state.update("target_url", target_url)
    
    # Yield initial state
    yield {"step": 0, "message": "🟡 Acquiring Repository..."}

    try:
        repo_path = acquire_repository(target_url)
        state.update("repository_path", repo_path)
    except Exception as e:
        yield {"step": -1, "message": f"🔴 Pipeline failed at Acquire step: {str(e)}"}
        return

    # 1. Scan Repository
    yield {"step": 1, "message": "🟢 Repository Acquired\n\n🟡 Scanner Running..."}
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
    yield {"step": 3, "message": "🟢 Trace Complete\n\n🟡 Red Team Validating..."}
    red_team_result = run_red_team(state.get_all())
    state.update("red_team_results", red_team_result)

    # 4. Fix Vulnerability
    yield {"step": 4, "message": "🟢 Red Team Complete\n\n🟡 Generating Patches..."}
    fix_result = run_fix(state.get_all())
    state.update("fix_results", fix_result)

    # 5. Verify Patch
    yield {"step": 5, "message": "🟢 Patches Generated\n\n🟡 Verifying Patches..."}
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflow.py <repository_path_or_url>")
        sys.exit(1)
        
    target = sys.argv[1]
    print(f"Spelunking... Starting workflow for {target}")
    
    # Make sure stdout uses UTF-8 to prevent emoji crashes on Windows
    sys.stdout.reconfigure(encoding='utf-8')
    
    for update in execute_pipeline(target):
        print(f"Step {update.get('step')}: {update.get('message')}")
        if update.get('step') == 7:
            print("\nPipeline finished. Report saved to ./outputs/final_report.md")
