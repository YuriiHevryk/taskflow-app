
---
name: taskflow-adr
description: Documents approved architecture decisions for the TaskFlow application in the Obsidian knowledge base. Use when evaluating architecture choices, recording accepted decisions, or updating TaskFlow architecture documentation.
---

# TaskFlow Architecture Decision Record

## Purpose

Document architecture decisions made during the development of TaskFlow.

Each architecture decision must explain:
- The problem being addressed.
- The context of the decision.
- The alternatives considered.
- The selected solution.
- The reasons for the choice.
- The expected consequences.

Use the TaskFlow knowledge base and project guardrails.

## Required project context

Before preparing an ADR:

1. Read docs/app-requirements.md.
2. Read docs/harness-requirements.md.
3. Read docs/guardrails.md.
4. Read the relevant architecture documentation.
5. Search the Obsidian knowledge base.

Use the taskflow-vault MCP server when available.

Call search_notes with relevant queries, including:
- SQLite
- Task Repository
- Task Service
- Architecture
- Decision

Only use queries relevant to the actual task.

If the decision concerns a GitHub change, use GitHub MCP to verify the relevant commit and affected files.

If MCP is unavailable, report the limitation.

Do not invent architecture decisions or implementation details.

## Procedure

### Step 1. Identify the decision

Determine:
- What problem requires a decision.
- Which TaskFlow components are affected.
- Whether a related decision already exists.
- Whether the decision is proposed or approved.

Do not record a proposal as an accepted decision.

### Step 2. Analyze the context

Review project requirements and relevant Obsidian notes.

Identify existing constraints, dependencies and architecture conventions.

### Step 3. Compare alternatives

Consider at least two reasonable alternatives when applicable.

For each alternative, describe:
- Advantages.
- Disadvantages.
- Compatibility with TaskFlow.
- Relevant risks.

### Step 4. Prepare the ADR

Use the following structure:

# Architecture Decision: Title

## Context

Describe the problem and current conditions.

## Alternatives

Describe the available solutions.

## Decision

State the selected solution.

## Rationale

Explain why this solution was selected.

## Consequences

Describe expected positive and negative effects.

## Related Components

List related TaskFlow components using Obsidian wiki-links.

## Verification

State which requirements, project files or knowledge base notes were checked.

### Step 5. Check guardrails

Before creating or updating a note, read docs/guardrails.md.

Relevant rules:

- W-02: Obsidian writes require user approval.
- W-03: Git push requires user approval.
- B-02: Deleting architecture decisions is prohibited.
- B-03: Recursive repository deletion is prohibited.

Never delete existing decision notes.

Never overwrite a previous decision without explicit approval.

If a new decision replaces an older one, preserve the old record and document the supersedes relationship.

### Step 6. Request approval

Present the completed ADR draft to the user.

Ask for explicit confirmation before writing to Obsidian and synchronizing Git.

Do not treat a generated draft as user approval.

### Step 7. Save the approved ADR

Only after explicit user approval, call the taskflow-vault MCP tool ingest_note with:

- title: short English title.
- note_type: decision.
- content: approved ADR content.
- links: related existing note titles.
- approved: true.

The current ingest_note implementation creates accepted decision notes. Therefore, do not use it to save an unapproved proposal.

The MCP tool handles Git synchronization.

Do not perform a separate Git push unless necessary and explicitly authorized.

### Step 8. Verify the result

Check the tool response.

Confirm:
- The expected note path.
- Successful creation or update.
- Git synchronization status.
- Whether manual intervention was required.

Do not claim success without verification.

## Expected output

# ADR Result

### Decision

Title and short description.

### Context Sources

Project documents and Obsidian notes consulted.

### Alternatives

Solutions considered and their tradeoffs.

### Selected Solution

The approved decision and rationale.

### Guardrails

Relevant rules and confirmation status.

### Obsidian Result

- File path.
- Creation or update status.
- Git synchronization result.

### Manual Intervention

Describe any corrections or actions required from the user.

## Restrictions

- Do not invent project facts.
- Do not save an unapproved architecture decision.
- Do not delete historical ADR notes.
- Do not perform force push.
- Do not modify application source code.
- Do not bypass guardrails or user confirmations.
- Report unavailable MCP tools or failed synchronization.
