---
name: taskflow-code-review
description: "Review TaskFlow Python code for correctness, security, architecture compliance and guardrails. Use when reviewing Python modules and MCP tools."
---

# TaskFlow Code Review

## Purpose

Review Python source files in TaskFlow without modifying them.

## Required context

Before reviewing code:

1. Read docs/app-requirements.md.
2. Read docs/harness-requirements.md.
3. Read docs/guardrails.md.
4. Read the requested Python file.
5. Search the Obsidian knowledge base using taskflow-vault MCP search_notes.

Use relevant searches such as Task Service, Task Repository, SQLite or MCP.

If MCP is unavailable, report this limitation.

## Review procedure

### Step 1. Understand the component

Identify its purpose, functions, dependencies and related TaskFlow components.

### Step 2. Check correctness

Inspect:
- Input validation.
- Exception handling.
- Return values.
- File operations.
- Database operations.
- Potential data loss.

### Step 3. Check security

Inspect:
- Unsafe shell commands.
- Path traversal.
- Unrestricted file access.
- Secrets exposure.
- Missing permission checks.

### Step 4. Check architecture

Compare the implementation with project requirements and relevant Obsidian notes.

Distinguish implemented features from planned features.

### Step 5. Check guardrails

Verify compliance with docs/guardrails.md.

Pay attention to:
- W-01: changes to connector/server.py require approval.
- W-02: Obsidian writes require approval.
- W-03: Git push requires approval.
- B-01: force push is prohibited.
- B-02: deletion of architecture decisions is prohibited.
- B-03: recursive repository deletion is prohibited.

### Step 6. Check tests

Inspect existing tests and run safe tests when appropriate.

Never invent test results.

### Step 7. Prepare report

Use this structure:

## Code Review Result

File: reviewed file path

### Summary
Purpose and overall assessment.

### Findings
For each issue provide severity, location, problem, impact and recommendation.

### Guardrails Compliance
Relevant rules and detected violations.

### Test Results
Tests actually executed and their results.

### Recommendations
Prioritized improvements.

## Restrictions

- Do not modify project files.
- Do not modify Obsidian notes.
- Do not create commits or push changes.
- Do not execute destructive commands.
- Follow existing TaskFlow guardrails.
- Report missing context instead of guessing.
