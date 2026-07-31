---
title: Task 2 - Make and Verify Your First Change
layout: default
parent: Workshop 07 - Introduction to Codex
nav_order: 2
---

# Task 2 - Make and Verify Your First Change

Good Codex tasks describe the outcome and the boundaries, not every keystroke. Use four parts:

```text
Context + Goal + Constraints + Verification
```

## Write the task

Try a small documentation change:

```text
Context: This is a static workshop website.
Goal: Add one short sentence to the README explaining who the site is for.
Constraints: Keep the current tone and do not change any other files.
Verification: Show the diff and check the Markdown formatting.
```

The context explains the project, the goal defines success, the constraints limit the change and the verification request makes the result testable.

## Use an inspect-plan-change-check loop

1. **Inspect** - ask Codex to find the relevant files and existing conventions.
2. **Plan** - ask what it intends to change before it edits anything.
3. **Change** - approve a small, clearly scoped implementation.
4. **Check** - run the relevant test or local preview and review the diff.

For a visual change, include the page URL and what you expect to see. For a bug, include the error, the reproduction steps and the expected behaviour.

## Review the result

Use the **Changes** view in GitHub Desktop, the source-control view in your editor or `git diff` in a terminal. Check:

- Only the intended files changed
- Existing content was not accidentally deleted
- No secrets or temporary files were added
- The page still works locally
- The result matches the requested outcome

If the result is too broad, do not commit it. Ask Codex to narrow the change or explain exactly what should be reverted.

{: .challenge-title}
> Improve the prompt
>
> Ask Codex to add a short section to a practice README. Include one style requirement, one file boundary and one concrete verification step. Compare the result with a vague prompt such as `improve the README`.

