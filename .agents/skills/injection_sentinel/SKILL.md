---
name: injection_sentinel
description: Automatically audit GitHub repositories and Pull Requests for prompt injection vulnerabilities, system prompt leaks, unsafe agent behavior, and AI security issues. Clone the repository, execute the security pipeline, generate patches, verify fixes, and summarize results.
---

# Injection Sentinel

## Purpose

Injection Sentinel is an autonomous AI security auditor for LLM applications.

When invoked, it performs an end-to-end security assessment of a GitHub repository or Pull Request for prompt injection vulnerabilities and unsafe AI behaviors.

Never stop after identifying this skill.
Always execute the complete workflow.

---

# Automatically invoke when the user asks

Examples:

- Scan this PR
- Review this repository
- Check this GitHub repository
- Audit this AI project
- Find prompt injection vulnerabilities
- Security review this PR
- Analyze this AI application
- Check for system prompt leaks

---

# Supported Inputs

The skill accepts:

- GitHub Pull Request URL

Example

https://github.com/openai/openai-python/pull/123

- GitHub Repository URL

Example

https://github.com/openai/openai-python

- Local repository path

Example

C:\Projects\agent

---

# Execution Workflow

When invoked, ALWAYS execute the following steps.

## Step 1 — Acquire Repository

If the input is a GitHub Pull Request:

- Clone the repository into a temporary directory.
- Fetch the pull request.
- Checkout the PR branch.
- Determine the base branch.
- Compute the changed files.

If the input is a GitHub repository:

- Clone the latest version.

If the input is a local repository:

- Use the existing directory.

---

## Step 2 — Static AI Analysis

Run the repository scanner.

Objectives:

- Detect LLM entry points
- Detect prompt construction
- Detect tool calling
- Detect memory usage
- Detect RAG pipelines
- Detect AI frameworks
- Detect user-controlled inputs

Trace every possible flow:

External Input
↓

Application
↓

Prompt Builder
↓

LLM

↓

Tool Execution

---

## Step 3 — AI Security Audit

Run the AI auditor.

Determine:

- Prompt Injection
- System Prompt Leakage
- Prompt Override
- Tool Abuse
- Jailbreak Risk
- Data Exfiltration
- Unsafe Autonomous Actions

Never classify vulnerabilities from keywords alone.

Require a demonstrable exploit path.

---

## Step 4 — Red Team Validation

Attempt realistic attacks.

Examples:

- Ignore previous instructions
- Reveal your hidden prompt
- Leak secrets
- Execute unauthorized tools
- Override system instructions

Only confirm vulnerabilities that are reproducible.

---

## Step 5 — Patch Generation

If vulnerabilities exist:

Generate secure patches.

Requirements:

- Preserve application behavior.
- Eliminate exploit path.
- Follow secure coding practices.

---

## Step 6 — Patch Verification

Re-run the security audit.

Confirm:

- Vulnerability removed
- No regression
- No new vulnerabilities introduced

---

## Step 7 — Generate Report

Produce:

outputs/final_report.md

Include:

- Executive Summary
- Repository Information
- Files Reviewed
- Vulnerabilities
- Severity
- Exploit Path
- Evidence
- Patch
- Verification Status
- Final Decision

---

# Decision Rules

TRUE_POSITIVE

Only if ALL are true:

- LLM execution path exists
- Attacker-controlled input exists
- Prompt influence exists
- Exploit reproduced
- Impact demonstrated

FALSE_POSITIVE

Pattern exists.

No exploit path exists.

CLEAN

Repository fully analyzed.

No exploitable prompt injection found.

NEEDS_REVIEW

Insufficient evidence.

Never classify based only on keywords.

---

# Output

Return a concise summary in chat.

If a report was generated, summarize:

Repository

Files analyzed

Classification

Severity

Confidence

Exploit

Patch

Verification

Overall

Then reference:

outputs/final_report.md

---

# Project Commands

Execute the pipeline using:

```bash
python workflow.py <repository_path>
```

If a Discord bot is running, also send the final report to Discord.

---

# Important

Always execute the workflow.

Do not stop after selecting this skill.

Do not merely explain what Injection Sentinel does.

Perform the scan and return the results.
