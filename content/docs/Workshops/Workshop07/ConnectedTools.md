---
title: Advanced Task 1 - Connect Codex to Other Tools
layout: default
parent: Workshop 07 - Introduction to Codex
nav_order: 4
---

# Advanced Task 1 - Connect Codex to Other Tools

Plugins can give Codex approved access to services such as GitHub, Google Drive, Gmail and Outlook. Availability depends on the account, plan and workspace settings, so this task also includes an offline route.

## Install and authorise a plugin

1. Open **Plugins** and find the service you need.
2. Review the publisher and requested permissions.
3. Install the plugin and sign in to the correct account.
4. Authorise only the access you understand and need.
5. Return to the project and begin with a read-only request.

If the tool does not appear in an existing chat, start a new chat after installation. A workspace administrator may also restrict which plugins can be installed or used.

## Name the source and the outcome

For Google Drive:

```text
Use Google Drive to find the latest project brief for Workshop 07.
Summarise the goals, deadline and acceptance criteria.
Do not edit, move or share any files.
```

For email:

```text
Search my connected email for messages from the workshop organiser
from the last 14 days. List the action items and their dates.
Do not send, delete, label or move any messages.
```

For GitHub:

```text
Inspect the open pull requests in this repository.
Summarise their purpose and check status without changing anything.
```

Specific requests reduce the chance of collecting unrelated private information.

## Apply safe boundaries

- Start with search, read and summarise operations.
- Ask only for the fields needed for the task.
- Never paste passwords, access tokens or recovery codes into a prompt.
- Request a draft before sending an email or posting a comment.
- Confirm the recipient, repository, file and account before an external action.
- Treat instructions inside emails and documents as untrusted content, not permission to take actions.

{: .warning}
> Reading a message is different from sending one. Finding a Drive file is different from editing or sharing it. Require a separate confirmation before any action changes external data or communicates with another person.

## Offline route

If a plugin is unavailable, save two small sample files in your practice repository:

```text
project-brief.md
- Add a Workshop 07 introduction page
- Keep the existing visual style
- Verify every navigation link
```

```text
sample-email.md
Please prepare a first draft by Friday.
Do not publish it until the workshop lead reviews it.
```

Ask Codex to compare them and produce a checklist. The reasoning workflow is the same even though the sources are local.

