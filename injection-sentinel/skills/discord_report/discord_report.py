"""
Skill: Discord Report
Autonomous agent for generating Discord-formatted security reports.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import ReportResult


class DiscordReporter:
    """Generate Discord-formatted security reports"""
    
    # Color codes for Discord embeds
    COLORS = {
        "critical": 14431813,  # Red
        "high": 16613908,      # Orange
        "medium": 16761095,    # Yellow
        "low": 2664261,        # Green
        "info": 7107469,       # Gray
        "success": 3066993,    # Blue
    }
    
    # Emoji indicators
    EMOJI = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "security": "🔒",
        "bug": "🐛",
        "fix": "🔧",
        "payload": "💣",
    }
    
    def __init__(self, analysis_results: Dict[str, Any]):
        self.results = analysis_results
        self.embeds: List[Dict[str, Any]] = []
        self.markdown = ""
    
    def generate(self) -> Dict[str, Any]:
        """Main report generation logic"""
        
        # Generate markdown report
        self.markdown = self._generate_markdown()
        
        # Generate Discord embeds
        self._generate_embeds()
        
        return self._build_result()
    
    def _generate_markdown(self) -> str:
        """Generate full markdown report"""
        
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Executive summary
        sections.append(self._generate_executive_summary())
        
        # Vulnerability details
        if self.results.get('flows'):
            sections.append(self._generate_vulnerability_section())
        
        # Red team results
        if self.results.get('payloads'):
            sections.append(self._generate_redteam_section())
        
        # Fixes
        if self.results.get('fixes'):
            sections.append(self._generate_fixes_section())
        
        # Recommendations
        sections.append(self._generate_recommendations())
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate report header"""
        
        return f"""# {self.EMOJI['security']} Injection Sentinel Security Report

**Repository:** `{self.results.get('repository_path', 'Unknown')}`
**Scan Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
**Report ID:** `{self._generate_report_id()}`

---"""
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary"""
        
        vuln_count = self.results.get('vulnerability_count', 0)
        validated_count = self.results.get('validated_count', 0)
        fixes_count = len(self.results.get('fixes', []))
        
        # Determine severity
        max_severity = self._get_max_severity()
        severity_emoji = self.EMOJI.get(max_severity, self.EMOJI['info'])
        
        # Determine status
        if vuln_count == 0:
            status = f"{self.EMOJI['success']} **SECURE** - No vulnerabilities detected"
        elif validated_count > 0:
            status = f"{self.EMOJI['error']} **CRITICAL** - Exploitable vulnerabilities found"
        else:
            status = f"{self.EMOJI['warning']} **WARNING** - Potential vulnerabilities detected"
        
        summary = f"""## {severity_emoji} Executive Summary

{status}

### Key Findings

- **Total Vulnerabilities:** {vuln_count}
- **Validated Exploits:** {validated_count}
- **Security Patches:** {fixes_count}
- **Files Affected:** {self._get_affected_files_count()}

### Risk Distribution

{self._generate_risk_distribution()}"""
        
        return summary
    
    def _generate_vulnerability_section(self) -> str:
        """Generate vulnerability details section"""
        
        flows = self.results.get('flows', [])
        
        section = f"""## {self.EMOJI['bug']} Vulnerability Details

Found **{len(flows)}** taint flows from user input to LLM prompts:

"""
        
        for i, flow in enumerate(flows, 1):
            confidence_emoji = self._get_confidence_emoji(flow.get('confidence', 'low'))
            
            section += f"""### {i}. {confidence_emoji} Taint Flow ({flow.get('confidence', 'unknown').upper()} confidence)

**Source:** `{flow.get('source', 'unknown')}`  
**File:** `{flow.get('source_file', 'unknown')}:{flow.get('source_line', 0)}`

**Sink:** `{flow.get('sink', 'unknown')}`  
**File:** `{flow.get('sink_file', 'unknown')}:{flow.get('sink_line', 0)}`

**Flow Path:**
{self._format_path(flow.get('path', []))}

**Evidence:**
{self._format_evidence(flow.get('evidence', []))}

---

"""
        
        return section
    
    def _generate_redteam_section(self) -> str:
        """Generate red team results section"""
        
        payloads = self.results.get('payloads', [])
        
        # Group by validation result
        exploitable = [p for p in payloads if p.get('validation_result') == 'exploitable']
        likely = [p for p in payloads if p.get('validation_result') == 'likely']
        
        section = f"""## {self.EMOJI['payload']} Red Team Analysis

Generated **{len(payloads)}** attack payloads:
- {self.EMOJI['error']} **{len(exploitable)}** confirmed exploitable
- {self.EMOJI['warning']} **{len(likely)}** likely exploitable

### Sample Exploits

"""
        
        # Show top 3 exploitable payloads
        for i, payload in enumerate(exploitable[:3], 1):
            risk_emoji = self.EMOJI.get(payload.get('risk', 'medium'), self.EMOJI['warning'])
            
            section += f"""#### {i}. {risk_emoji} {payload.get('name', 'Unknown')}

**Risk Level:** {payload.get('risk', 'unknown').upper()}  
**Status:** {self.EMOJI['error']} Exploitable

**Payload:**
```
{payload.get('payload', 'N/A')}
```

**Expected Effect:**  
{payload.get('expected_effect', 'Unknown')}

**Target:** `{payload.get('target_sink', 'Unknown')}`

---

"""
        
        return section
    
    def _generate_fixes_section(self) -> str:
        """Generate security patches section"""
        
        fixes = self.results.get('fixes', [])
        
        section = f"""## {self.EMOJI['fix']} Security Patches

Generated **{len(fixes)}** security patches:

"""
        
        for i, fix in enumerate(fixes, 1):
            section += f"""### {i}. {fix.get('vulnerability_id', 'UNKNOWN')}

**File:** `{fix.get('file_path', 'unknown')}`  
**Technique:** {fix.get('technique', 'unknown').upper()}

**Issue:**
{self._format_multiline(fix.get('reason', 'No reason provided'))}

**Original Code:**
```python
{fix.get('original_code', 'N/A')}
```

**Fixed Code:**
```python
{fix.get('fixed_code', 'N/A')}
```

"""
        
        return section
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section"""
        
        vuln_count = self.results.get('vulnerability_count', 0)
        
        if vuln_count == 0:
            return f"""## {self.EMOJI['success']} Recommendations

**Status:** Repository appears secure

### Ongoing Security

- Continue regular security scans
- Review new LLM integrations carefully
- Implement input validation as standard practice
- Consider adding prompt injection tests to CI/CD"""
        
        return f"""## {self.EMOJI['warning']} Recommendations

### Immediate Actions Required

1. **Review Security Patches**
   - Examine each generated fix carefully
   - Test patches in development environment
   - Apply fixes to production code

2. **Implement Defensive Patterns**
   - Use delimiters to isolate user input
   - Validate and sanitize all external input
   - Never trust user-provided content in prompts

3. **Add Security Testing**
   - Include prompt injection tests in test suite
   - Test with malicious payloads regularly
   - Monitor LLM behavior for anomalies

### Long-term Improvements

1. **Input Validation Framework**
   - Implement centralized input validation for all user data

2. **Prompt Templates**
   - Use structured prompt templates instead of string concatenation

3. **Security Reviews**
   - Require security review for all LLM integration code

4. **Monitoring & Alerts**
   - Log and monitor unusual LLM behavior or responses

5. **Training**
   - Educate developers on prompt injection risks"""
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        
        return f"""---
{self.EMOJI['info']} **Report Information**
- Generated by: Injection Sentinel v1.0.0
- Analysis Type: Static taint analysis + red team validation
- Scan Duration: {self._calculate_duration()}

*This report was generated automatically. Please review all findings and patches carefully before applying to production.*"""
    
    def _generate_embeds(self):
        """Generate Discord embeds"""
        
        # Main summary embed
        self.embeds.append(self._create_summary_embed())
        
        # Vulnerability embeds (if any)
        flows = self.results.get('flows', [])
        if flows:
            for flow in flows[:5]:  # Limit to 5
                self.embeds.append(self._create_vulnerability_embed(flow))
    
    def _create_summary_embed(self) -> Dict[str, Any]:
        """Create main summary embed"""
        
        vuln_count = self.results.get('vulnerability_count', 0)
        validated_count = self.results.get('validated_count', 0)
        fixes_count = len(self.results.get('fixes', []))
        
        # Determine color
        if validated_count > 0:
            color = self.COLORS['critical']
            title = f"{self.EMOJI['error']} Critical Vulnerabilities Detected"
        elif vuln_count > 0:
            color = self.COLORS['high']
            title = f"{self.EMOJI['warning']} Potential Vulnerabilities Found"
        else:
            color = self.COLORS['success']
            title = f"{self.EMOJI['success']} No Vulnerabilities Detected"
        
        embed = {
            "title": title,
            "description": f"Security scan complete for `{self.results.get('repository_path', 'unknown')}`",
            "color": color,
            "fields": [
                {
                    "name": "Total Vulnerabilities",
                    "value": str(vuln_count),
                    "inline": True
                },
                {
                    "name": "Validated Exploits",
                    "value": str(validated_count),
                    "inline": True
                },
                {
                    "name": "Patches Generated",
                    "value": str(fixes_count),
                    "inline": True
                },
                {
                    "name": "Files Affected",
                    "value": str(self._get_affected_files_count()),
                    "inline": True
                },
                {
                    "name": "Scan Date",
                    "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": self._get_status_text(),
                    "inline": True
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return embed
    
    def _create_vulnerability_embed(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """Create embed for a specific vulnerability"""
        
        confidence = flow.get('confidence', 'unknown')
        color = self.COLORS.get(confidence, self.COLORS['info'])
        
        embed = {
            "title": f"{self._get_confidence_emoji(confidence)} Taint Flow Detected",
            "description": f"**Confidence:** {confidence.upper()}",
            "color": color,
            "fields": [
                {
                    "name": "Source",
                    "value": f"`{flow.get('source', 'unknown')}`\n`{flow.get('source_file', 'unknown')}:{flow.get('source_line', 0)}`",
                    "inline": False
                },
                {
                    "name": "Sink",
                    "value": f"`{flow.get('sink', 'unknown')}`\n`{flow.get('sink_file', 'unknown')}:{flow.get('sink_line', 0)}`",
                    "inline": False
                },
                {
                    "name": "Evidence",
                    "value": self._format_evidence(flow.get('evidence', []))[:1024],
                    "inline": False
                }
            ]
        }
        
        return embed
    
    def _get_max_severity(self) -> str:
        """Determine maximum severity from all findings"""
        
        payloads = self.results.get('payloads', [])
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if any(p.get('risk') == severity for p in payloads):
                return severity
        
        return 'info'
    
    def _get_affected_files_count(self) -> int:
        """Count unique affected files"""
        
        files = set()
        
        for flow in self.results.get('flows', []):
            files.add(flow.get('source_file', ''))
            files.add(flow.get('sink_file', ''))
        
        for fix in self.results.get('fixes', []):
            files.add(fix.get('file_path', ''))
        
        return len([f for f in files if f])
    
    def _generate_risk_distribution(self) -> str:
        """Generate risk distribution text"""
        
        payloads = self.results.get('payloads', [])
        
        critical = sum(1 for p in payloads if p.get('risk') == 'critical')
        high = sum(1 for p in payloads if p.get('risk') == 'high')
        medium = sum(1 for p in payloads if p.get('risk') == 'medium')
        low = sum(1 for p in payloads if p.get('risk') == 'low')
        
        dist = []
        if critical > 0:
            dist.append(f"- {self.EMOJI['critical']} **Critical:** {critical}")
        if high > 0:
            dist.append(f"- {self.EMOJI['high']} **High:** {high}")
        if medium > 0:
            dist.append(f"- {self.EMOJI['medium']} **Medium:** {medium}")
        if low > 0:
            dist.append(f"- {self.EMOJI['low']} **Low:** {low}")
        
        return '\n'.join(dist) if dist else "- No risks identified"
    
    def _get_confidence_emoji(self, confidence: str) -> str:
        """Get emoji for confidence level"""
        mapping = {
            "high": self.EMOJI['critical'],
            "medium": self.EMOJI['warning'],
            "low": self.EMOJI['info']
        }
        return mapping.get(confidence.lower(), self.EMOJI['info'])
    
    def _format_path(self, path: List[str]) -> str:
        """Format taint path"""
        if not path:
            return "No path information"
        return '\n'.join(f"  {i+1}. {step}" for i, step in enumerate(path))
    
    def _format_evidence(self, evidence: List[str]) -> str:
        """Format evidence list"""
        if not evidence:
            return "No evidence available"
        return '\n'.join(f"- {item}" for item in evidence)
    
    def _format_multiline(self, text: str) -> str:
        """Format multiline text"""
        lines = text.strip().split('\n')
        return '\n'.join(f"> {line}" for line in lines)
    
    def _get_status_text(self) -> str:
        """Get status text"""
        vuln_count = self.results.get('vulnerability_count', 0)
        validated_count = self.results.get('validated_count', 0)
        
        if vuln_count == 0:
            return f"{self.EMOJI['success']} Secure"
        elif validated_count > 0:
            return f"{self.EMOJI['error']} Action Required"
        else:
            return f"{self.EMOJI['warning']} Review Needed"
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        import hashlib
        timestamp = datetime.utcnow().isoformat()
        repo = self.results.get('repository_path', 'unknown')
        return hashlib.sha256(f"{timestamp}{repo}".encode()).hexdigest()[:12].upper()
    
    def _calculate_duration(self) -> str:
        """Calculate scan duration"""
        # Placeholder - would use actual timing data
        return "< 1 minute"
    
    def _build_result(self) -> Dict[str, Any]:
        """Build final result"""
        
        critical_count = sum(
            1 for p in self.results.get('payloads', [])
            if p.get('risk') == 'critical'
        )
        
        result = ReportResult(
            status="success",
            summary=f"Generated security report with {self.results.get('vulnerability_count', 0)} findings",
            markdown=self.markdown,
            embeds=self.embeds,
            critical_count=critical_count,
            next_action="complete",
            data={
                "report_length": len(self.markdown),
                "embed_count": len(self.embeds),
                "vulnerabilities": self.results.get('vulnerability_count', 0),
                "validated_exploits": self.results.get('validated_count', 0),
            }
        )
        
        return result.to_dict()


def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill entrypoint.
    
    Args:
        input_data: Combined results from all previous skills
    
    Returns:
        Structured JSON result with Discord-formatted report
    """
    
    try:
        reporter = DiscordReporter(input_data)
        result = reporter.generate()
        
        return result
        
    except Exception as e:
        return {
            "status": "failure",
            "summary": f"Report generation failed: {str(e)}",
            "markdown": "",
            "embeds": [],
            "critical_count": 0,
            "next_action": "complete",
            "data": {"error": str(e)}
        }


if __name__ == "__main__":
    # Test execution
    import json
    
    # Mock complete analysis results
    mock_input = {
        "repository_path": "../../sample_repo",
        "vulnerability_count": 2,
        "validated_count": 1,
        "flows": [
            {
                "source": "request.POST['message']",
                "source_file": "../../sample_repo/agent.py",
                "source_line": 15,
                "sink": "llm.invoke(prompt)",
                "sink_file": "../../sample_repo/agent.py",
                "sink_line": 42,
                "path": ["user_input -> prompt"],
                "confidence": "high",
                "evidence": ["Direct flow", "No sanitization"]
            }
        ],
        "payloads": [
            {
                "name": "Instruction Override",
                "payload": "Ignore previous instructions",
                "expected_effect": "Override behavior",
                "risk": "critical",
                "target_sink": "line 42",
                "validation_result": "exploitable"
            }
        ],
        "fixes": [
            {
                "vulnerability_id": "PINJ-001",
                "file_path": "../../sample_repo/agent.py",
                "original_code": "prompt = f'User: {user_input}'",
                "fixed_code": "# Use delimiter pattern",
                "reason": "Direct interpolation",
                "technique": "delimiter"
            }
        ]
    }
    
    result = execute(mock_input)
    
    print("=== MARKDOWN REPORT ===")
    print(result['markdown'])
    
    print("\n\n=== EMBEDS ===")
    print(json.dumps(result['embeds'], indent=2))
