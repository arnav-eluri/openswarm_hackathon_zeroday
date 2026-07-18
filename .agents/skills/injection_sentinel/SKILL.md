---
name: injection_sentinel
description: A multi-agent security pipeline that scans an AI repository for Prompt Injection vulnerabilities and integrates with a Discord bot.
---

# Skill: Injection Sentinel

## Purpose
A production-quality prompt injection detection and remediation system. It scans a repository for LLM sinks, traces user input to these sinks, performs a complete AI Security Audit via OpenRouter LLM, validates exploitability via red teaming, generates secure defensive patches, verifies those patches, and reports the findings to Discord.

## When to use
Use this skill when you need to audit an AI/LLM-integrated codebase (e.g. from a GitHub Pull Request) for prompt injection vulnerabilities, generate secure fixes for them, and report back to a Discord server.

## Prerequisites
Ensure the `.env` file contains the required credentials:
```
DISCORD_TOKEN=your_discord_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
```

## Running the Discord Bot
The primary interface for this skill is the Discord bot. It must be run persistently in the background.

```bash
pm2 start ecosystem.config.js
```
*Note: The bot uses discord.app_commands for slash commands. In Discord, type `/scan <pr_url>` to execute the pipeline.*

## Running Manually via CLI
You can also execute the pipeline manually against a local directory without Discord:

```bash
python workflow.py [path_to_repository]
```

## Expected Outputs
The pipeline orchestrates various independent agents. The final output is a Markdown report generated in `./outputs/final_report.md` containing:
- Executive Summary of vulnerabilities.
- Detected input-to-prompt traces.
- AI Auditor Classification (CLEAN, TRUE_POSITIVE, etc).
- Validated red team exploits.
- Python code diffs for security patches.

## Architecture & Agents
- **`discord_bot.py`**: Discord interface and orchestrator integration.
- **`workflow.py`**: Pipeline generator that executes the agent chain.
- **`scan_repository.py`**: Static AST parser for identifying LLM sinks.
- **`trace_prompt_injection.py`**: Advanced OpenRouter LLM auditor using a strict security prompt.
- **`red_team.py`**: Exploit payload generator.
- **`fix_vulnerability.py`**: Automated patch generator.
- **`verify_patch.py`**: Patch validator.
- **`discord_report.py`**: Markdown report builder.
