---
title: Task 1 - Set Up a Codex Project
layout: default
parent: Workshop 07 - Introduction to Codex
nav_order: 1
---

# Task 1 - Set Up a Codex Project

A Codex project gives related chats access to the folders and instructions needed for the work. Start with a practice repository so every action is easy to inspect and undo.

## Choose the folder

Use the repository root: the folder that contains the project's source files and usually its hidden `.git` folder. Do not select a parent folder containing unrelated projects.

In the Codex app:

1. Open the project's menu and select **Edit project**.
2. Select **Add folder** and choose the practice repository.
3. Make that repository the **Primary** folder.
4. Start a new chat in the project.

New chats start in the primary folder, and Codex uses it as the default location for Git operations and project instructions. Additional source folders can be useful when one task genuinely needs both a website and a separate documentation repository.

{: .tip}
> A project organises access and context. It does not create a Git branch, commit changes or upload files by itself.

## Confirm the context

Begin with a read-only request:

```text
Inspect this project without changing anything.
Tell me the working folder, current Git branch, main files and how the site runs locally.
Mention any project instructions you find.
```

Check that the response names the repository and branch you expected. If it names an old folder, return to **Edit project**, correct the primary folder and start a new chat.

## Set boundaries

Add boundaries when a wrong action would create real work for somebody else:

```text
Work only in this repository.
Do not change deployment settings.
Do not commit, push, open a pull request or contact anyone unless I ask.
Explain any command that needs approval.
```

Keep passwords, API keys, access tokens, private customer data and `.env` files out of prompts and screenshots.

## Checkpoint

Before moving on, you should know:

- Which local folder Codex can work on
- Which branch is currently checked out
- Which commands run or test the project
- Which actions require your confirmation

