# Skill: Discord Report

## Purpose

Generate formatted Discord reports with embeds, markdown, and actionable summaries for prompt injection security analysis results.

## Entrypoint

`discord_report.py::execute(input_data)`

## Inputs

```json
{
  "repository_path": "string",
  "flows": [],
  "payloads": [],
  "fixes": [],
  "vulnerability_count": "number",
  "validated_count": "number"
}
```

## Outputs

```json
{
  "status": "success",
  "summary": "string",
  "markdown": "string (full Discord message)",
  "embeds": [
    {
      "title": "string",
      "description": "string",
      "color": "number",
      "fields": []
    }
  ],
  "critical_count": "number",
  "next_action": "complete",
  "data": {}
}
```

## Capabilities

- Generate Discord-compatible markdown
- Create rich embeds with color coding
- Summarize findings by severity
- Format code snippets with syntax highlighting
- Generate actionable recommendations
- Create visual severity indicators
- Format payload examples
- Include fix previews

## Report Sections

1. **Executive Summary**
   - Total vulnerabilities found
   - Risk distribution
   - Files affected
   - Overall recommendation

2. **Vulnerability Details**
   - Each taint flow
   - Confidence level
   - Source and sink
   - Evidence

3. **Red Team Results**
   - Validated payloads
   - Attack vectors
   - Expected impact

4. **Security Patches**
   - Fix previews
   - Techniques used
   - Files to modify

5. **Recommendations**
   - Immediate actions
   - Long-term improvements
   - Additional security measures

## Discord Formatting

- Bold: `**text**`
- Italic: `*text*`
- Code: `` `code` ``
- Code blocks: ```` ```language\ncode\n``` ````
- Quotes: `> quote`
- Lists: `- item` or `1. item`

## Color Coding

| Severity | Color | Hex |
|----------|-------|-----|
| 🔴 Critical | Red | #DC3545 (14431813) |
| 🟠 High | Orange | #FD7E14 (16613908) |
| 🟡 Medium | Yellow | #FFC107 (16761095) |
| 🟢 Low | Green | #28A745 (2664261) |
| ⚪ Info | Gray | #6C757D (7107469) |

## Constraints

- No external API calls
- Generate text output only
- Maximum embed field length: 1024 chars
- Maximum embed description: 4096 chars
- Maximum total embeds: 10

## Examples

### Input Example

```json
{
  "repository_path": "./sample_repo",
  "flows": [
    {
      "source": "request.POST['message']",
      "sink": "llm.invoke(prompt)",
      "confidence": "high",
      "risk": "critical"
    }
  ],
  "payloads": [
    {
      "name": "Instruction Override",
      "risk": "critical",
      "validation_result": "exploitable"
    }
  ],
  "fixes": [
    {
      "vulnerability_id": "PINJ-001",
      "technique": "delimiter"
    }
  ],
  "vulnerability_count": 1,
  "validated_count": 1
}
```

### Output Example

```json
{
  "status": "success",
  "summary": "Generated security report with 1 critical findings",
  "markdown": "# 🔒 Injection Sentinel Security Report\n\n**Repository:** ./sample_repo...",
  "embeds": [
    {
      "title": "🔴 Critical Vulnerability Detected",
      "description": "Found 1 prompt injection vulnerability",
      "color": 14431813,
      "fields": [
        {
          "name": "Vulnerabilities",
          "value": "1 critical",
          "inline": true
        },
        {
          "name": "Status",
          "value": "⚠️ Action Required",
          "inline": true
        }
      ]
    }
  ],
  "critical_count": 1,
  "next_action": "complete",
  "data": {}
}
```
