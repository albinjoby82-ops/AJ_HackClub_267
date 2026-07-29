---
title: Advanced Task 2 - Build a Project-Assistant Workflow
layout: default
parent: Workshop 07 - Introduction to Codex
nav_order: 5
---

# Advanced Task 2 - Build a Project-Assistant Workflow

Combine project context, external sources and GitHub into one controlled workflow. The goal is not maximum automation; it is a result that is easy to verify.

## Define the outcome

Use this capstone goal:

```text
Prepare one small improvement to a practice website based on the latest brief.
Keep the work on a separate branch, verify it locally and prepare it for review.
Do not push, open a pull request or contact anyone without my confirmation.
```

## Run the workflow

### 1. Gather

Ask Codex to read the project brief and relevant messages from connected tools. If the tools are unavailable, use the local sample files from the previous task.

Request a short requirements table containing:

- Requirement
- Source
- Proposed change
- Verification method

### 2. Inspect

Ask Codex to inspect the repository, current branch, project instructions and existing design patterns without changing files.

### 3. Plan

Request a file-by-file plan and ask it to flag assumptions, missing information and actions that would affect external systems.

### 4. Build

Create or switch to a working branch, then approve the smallest useful change. Keep unrelated formatting and deployment configuration out of scope.

### 5. Verify

Run the project's documented checks. Open the local page when visual layout matters, test the affected links and inspect the final diff.

### 6. Review and publish

Ask Codex for a summary containing:

- Files changed
- Requirements satisfied
- Checks performed
- Remaining risks or assumptions
- Suggested commit and pull-request text

Only then decide whether to commit, push and open a pull request.

{: .challenge-title}
> Add a human checkpoint
>
> Design a prompt that allows Codex to gather context, edit local files and run tests, but requires your explicit confirmation before each external write: pushing code, opening a pull request, editing Drive or sending email. Explain why each checkpoint matters.

## Completion checklist

- The change is on the intended branch
- The diff contains only relevant files
- No credentials or private source material were committed
- Local checks pass
- External actions were explicitly approved
- Another person can understand the pull-request summary

