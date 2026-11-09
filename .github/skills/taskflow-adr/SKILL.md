---
name: taskflow-adr
description: "Create and document TaskFlow architecture decisions using Obsidian and MCP. Use when evaluating or recording architecture decisions."
---

# TaskFlow Architecture Decision Record

## Purpose

Document architecture decisions for the TaskFlow application.

Each decision must include its context, alternatives, selected solution, rationale and consequences.

## Required context

Before preparing an ADR:

1. Read docs/app-requirements.md.
2. Read docs/harness-requirements.md.
3. Read docs/guardrails.md.
4. Identify affected TaskFlow components.
5. Search relevant notes using taskflow-vault MCP search_notes.

Search for related concepts, components and existing architecture decisions.

Do not invent information if MCP is unavailable.

## Procedure

### Step 1. Identify the decision

Determine:
- The problem requiring a decision.
- The affected components.
- Existing related decisions.
- Whether the decision is proposed or approved.

### Step 2. Analyze alternatives

Compare at least two reasonable solutions when applicable.

For each alternative describe advantages, disadvantages and risks.

### Step 3. Prepare ADR

Use this structure:

# Architecture Decision: Title

## Context
Describe the problem and current architecture.

## Alternatives
Describe the considered solutions.

## Decision
State the selected solution.

## Rationale
Explain the reasons for the choice.

## Consequences
Describe positive and negative effects.

## Related Components
List relevant Obsidian wiki-links.

## Verification
List project files and notes consulted.

### Step 4. Check guardrails

Read docs/guardrails.md before modifying the knowledge base.

Relevant rules:
- W-02: Obsidian writes require approval.
- W-03: Git push requires approval.
- B-02: deleting architecture decisions is prohibited.
- B-03: deleting repositories is prohibited.

Never delete an existing ADR.

### Step 5. Request approval

Present the complete ADR draft to the user.

Do not write the note until the user explicitly approves the decision and its content.

### Step 6. Save approved ADR

Use taskflow-vault MCP ingest_note.

Provide:
- title: English decision title.
- note_type: decision.
- content: approved ADR text.
- links: existing related note titles.
- approved: true.

The MCP server handles saving and Git synchronization.

Do not perform additional Git operations without authorization.

### Step 7. Verify

Check:
- Tool response.
- Note creation status.
- Resulting file path.
- Git synchronization.
- Any manual corrections required.

## Expected output

# ADR Result

### Decision
Title and description.

### Context Sources
Documents and Obsidian notes consulted.

### Alternatives
Considered solutions.

### Selected Solution
Approved choice and rationale.

### Guardrails
Relevant rules and approval status.

### Obsidian Result
Created file and synchronization status.

### Manual Intervention
Any required corrections.

## Restrictions

- Do not invent architecture facts.
- Do not save unapproved decisions.
- Do not delete previous decisions.
- Do not modify application source code.
- Do not perform force push.
- Do not bypass guardrails.
