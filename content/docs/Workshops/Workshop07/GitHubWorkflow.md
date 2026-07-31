---
title: Task 3 - Work with GitHub
layout: default
parent: Workshop 07 - Introduction to Codex
nav_order: 3
---

# Task 3 - Work with GitHub

Git tracks versions on your computer. GitHub stores a shared remote copy and provides pull requests, issues and collaboration tools. Codex can help with both, but they are not the same connection.

## Follow the collaboration route

```text
Clone or pull -> create a branch -> edit -> verify -> commit -> push -> pull request
```

1. **Clone** creates a local copy of a remote repository.
2. **Pull** brings remote changes into your current local branch.
3. A **branch** isolates your work from the main branch.
4. A **commit** records a reviewed local snapshot.
5. **Push** uploads your commits to the remote repository.
6. A **pull request** asks the team to review and merge your branch.

Pushing a branch does not automatically merge it into the main branch.

## Create a working branch

Start from the repository's main branch, pull the latest changes and create a descriptive branch such as:

```text
your-name/codex-introduction
```

Confirm the current branch before editing. In a shared repository, avoid working directly on `main` or `master` unless the team has explicitly chosen that workflow.

## Ask Codex for a Git-aware change

```text
Confirm the current repository, branch and Git status.
Then add a short Getting Started note to the README.
Do not commit or push.
Run the relevant check and summarise the diff when finished.
```

Review the files before asking Codex to commit. Use a commit message that describes the outcome, for example:

```text
docs: add Codex getting-started note
```

Push only after the commit is correct. Open a pull request and explain what changed, why it changed and how it was tested.

## Understand the GitHub plugin

A local repository normally connects to GitHub through its Git remote and Git authentication. A GitHub plugin gives Codex additional tools for online information and actions, such as reading issues, inspecting pull requests or checking review feedback.

The plugin does not replace cloning the repository, creating a branch or reviewing local changes.

{: .warning}
> Before any push or pull request, confirm the repository owner, remote URL and current branch. A correct change pushed to the wrong repository is still the wrong result.

