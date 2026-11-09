
---
name: taskflow-code-review
description: Reviews Python code in the TaskFlow project for correctness, security, architecture consistency, and guardrail compliance. Use when reviewing MCP tools, Python modules, tests, or changes to the TaskFlow application.
---

# TaskFlow Code Review

## Purpose

Review Python code in the TaskFlow project.

The review must consider:
- Functional correctness.
- Error handling.
- Security and input validation.
- Architecture consistency.
- Existing project conventions.
- TaskFlow guardrails.

This skill performs analysis only. Do not modify files unless the user separately requests changes and approves them.

## Required project context

Before reviewing code:

1. Read docs/app-requirements.md.
2. Read docs/harness-requirements.md.
3. Read docs/guardrails.md.
4. Identify the target Python file.
5. Search the TaskFlow knowledge base for related concepts and components.

Use the taskflow-vault MCP server when available.

Call search_notes with relevant queries such as:
- Task
- Task Service
- Task Repository
- MCP
- Agent Harness

If MCP is unavailable, report the limitation. Do not invent information from the knowledge base.

## Review procedure

### Step 1. Understand the component

Identify:
- The purpose of the file.
- Its main functions and classes.
- Its external dependencies.
- Its relationship to other TaskFlow components.

### Step 2. Check correctness

Look for:
- Incorrect conditions.
- Missing input validation.
- Unhandled exceptions.
- Incorrect return values.
- Potential data loss.
- Incorrect path handling.

### Step 3. Check security

Look for:
- Dangerous subprocess commands.
- Unsafe file operations.
- Path traversal.
- Unrestricted write access.
- Accidental exposure of credentials.
- Missing validation of external inputs.

### Step 4. Check architecture

Compare the code with the TaskFlow requirements and knowledge base.

Identify inconsistencies between the implementation and documented architecture.

Do not treat planned components as already implemented.

### Step 5. Check guardrails

Check the relevant rules in docs/guardrails.md.

Pay particular attention to:
- W-01: modifications to connector/server.py require approval.
- W-02: writing notes to Obsidian requires approval.
- W-03: Git push requires approval.
- B-01: force push is prohibited.
- B-02: deletion of architecture decisions is prohibited.
- B-03: recursive deletion of repositories is prohibited.

Do not perform prohibited operations.

### Step 6. Check tests

Identify which functions are covered by tests.

If appropriate, run existing automated tests without modifying project files.

Do not claim that tests passed unless they were actually executed.

### Step 7. Prepare the report

Return the review in the following format.

## Code Review Result

File: path to reviewed file

### Summary

Briefly describe the purpose and overall assessment.

### Findings

For each confirmed issue provide:
- Severity: Critical, High, Medium, or Low.
- Location: function and line number when available.
- Problem: what is wrong.
- Impact: why it matters.
- Recommendation: how to fix it.

### Guardrails Compliance

State which rules are relevant and whether violations were found.

### Test Results

List tests actually executed and their results.

### Recommendations

Provide a short prioritized list of improvements.

If no confirmed issues are found, say so clearly.

## Restrictions

- Do not edit source files during review.
- Do not create Git commits.
- Do not perform Git push.
- Do not modify Obsidian notes.
- Do not invent test results.
- Follow the project guardrails.
- Report missing context instead of guessing.
